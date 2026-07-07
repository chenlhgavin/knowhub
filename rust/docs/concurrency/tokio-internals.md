# Tokio 设计原理

## 目录

- [一、整体架构](#一整体架构)
  - [1.1 Tokio 要解决的问题](#11-tokio-要解决的问题)
  - [1.2 四层架构](#12-四层架构)
  - [1.3 三个核心角色的归属](#13-三个核心角色的归属)
- [二、Executor：任务调度器](#二executor任务调度器)
  - [2.1 Task 的本质](#21-task-的本质)
  - [2.2 两种运行时模式](#22-两种运行时模式)
  - [2.3 工作窃取调度器](#23-工作窃取调度器)
  - [2.4 poll 的执行过程](#24-poll-的执行过程)
- [三、Reactor：I/O 事件循环](#三reactorio-事件循环)
  - [3.1 Reactor 的职责](#31-reactor-的职责)
  - [3.2 以 TcpStream::read 为例](#32-以-tcpstreamread-为例)
  - [3.3 Reactor 与 Worker 的集成](#33-reactor-与-worker-的集成)
- [四、Timer：时间轮](#四timer时间轮)
  - [4.1 定时器的挑战](#41-定时器的挑战)
  - [4.2 时间轮原理](#42-时间轮原理)
- [五、Waker：唤醒机制](#五waker唤醒机制)
  - [5.1 Waker 的实现](#51-waker-的实现)
  - [5.2 为什么 Waker 是 Clone + Send 的](#52-为什么-waker-是-clone--send-的)
- [六、spawn_blocking：阻塞任务隔离](#六spawn_blocking阻塞任务隔离)
  - [6.1 为什么需要独立的阻塞线程池](#61-为什么需要独立的阻塞线程池)
  - [6.2 线程池的生命周期与参数](#62-线程池的生命周期与参数)
  - [6.3 内部工作流程](#63-内部工作流程)
  - [6.4 线程池瓶颈与缓解](#64-线程池瓶颈与缓解)
- [七、完整请求处理流程](#七完整请求处理流程)

---

## 一、整体架构

### 1.1 Tokio 要解决的问题

Rust 标准库只定义了 `Future` trait，但没有人来驱动 Future 执行。Tokio 就是那个"驱动者"——它提供 Executor 来 poll Future、提供 Reactor 来监听 I/O 事件、提供 Waker 来在事件就绪时唤醒对应的 Task。

### 1.2 四层架构

```
┌─────────────────────────────────────────────────┐
│            应用层 API                            │
│   tokio::spawn / JoinSet / select! / timeout    │
├─────────────────────────────────────────────────┤
│            异步 I/O 原语                         │
│   TcpStream / UdpSocket / File / Sleep / mpsc   │
├─────────────────────────────────────────────────┤
│            运行时核心                             │
│   ┌───────────────┐    ┌──────────────────┐     │
│   │   Executor    │    │     Reactor      │     │
│   │  (任务调度器)  │◄──►│   (I/O 事件循环)  │     │
│   └───────────────┘    └──────────────────┘     │
├─────────────────────────────────────────────────┤
│            操作系统                               │
│   epoll (Linux) / kqueue (macOS) / IOCP (Win)   │
└─────────────────────────────────────────────────┘
```

### 1.3 三个核心角色的归属

| 角色 | 由谁提供 | 说明 |
|------|---------|------|
| **Future** | **Rust 语言本身**（`std::future::Future` trait） | 编译器将 `async fn` 转换为状态机 |
| **Executor** | **Tokio** | 负责调度和 poll Future |
| **Reactor** | **Tokio** | 基于 OS 事件队列的事件循环 |
| **Waker** | **标准库定义接口，Tokio 实现逻辑** | `std::task::Waker` 是标准库的 trait，唤醒后如何放回就绪队列由 Tokio 实现 |

Rust 语言只定义了 Future + Waker 接口，不内置 Executor 和 Reactor。这也是异步生态"运行时碎片化"的根源——Tokio、async-std、smol 各自实现了不同的 Executor 和 Reactor，导致为某个运行时写的异步 I/O 库无法在另一个运行时中使用。

---

## 二、Executor：任务调度器

### 2.1 Task 的本质

当你调用 `tokio::spawn(async { ... })` 时，Tokio 将这个 `async` 块包装成一个 **Task**——Tokio 的调度单位，类似于 OS 线程是 OS 调度器的调度单位。

```
Task 的内部结构（简化）：
┌──────────────────────────┐
│  Task                    │
│  ├── Future（状态机本体）  │  ← 编译器生成的 async 状态机
│  ├── State（调度状态）     │  ← Idle / Scheduled / Running / Complete
│  ├── Waker（唤醒器）      │  ← 用于从 Pending 恢复到就绪队列
│  └── JoinHandle          │  ← 让其他任务等待此任务完成
└──────────────────────────┘
```

**关键设计：Task 是堆分配的。** 与 Future 本身可以在栈上不同，`tokio::spawn` 会将 Future `Box` 化放到堆上，因为调度器需要在不同线程之间移动 Task。这也是 `spawn` 要求 Future 满足 `Send + 'static` 的原因。

### 2.2 两种运行时模式

Tokio 提供两种 Executor：

**current_thread（单线程）：**

```rust
#[tokio::main(flavor = "current_thread")]
async fn main() { ... }
```

- 所有 Task 在一个线程上执行
- 没有线程同步开销
- 适合轻量级应用、测试、嵌入式场景
- 内部就是一个简单的 FIFO 队列

**multi_thread（多线程，默认）：**

```rust
#[tokio::main(flavor = "multi_thread", worker_threads = 4)]
async fn main() { ... }
```

- 默认 worker 线程数 = CPU 核心数
- 使用**工作窃取（work-stealing）**调度算法
- 这是 Tokio 性能的核心所在

### 2.3 工作窃取调度器

这是 Tokio 最核心的设计。每个 worker 线程有自己的**本地队列**，另外还有一个**全局队列**：

```
Worker 0          Worker 1          Worker 2          Worker 3
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ 本地队列  │    │ 本地队列  │    │ 本地队列  │    │ 本地队列  │
│ [T1][T2] │    │ [T3]     │    │ [空]     │    │ [T4][T5] │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                     │
                                本地队列空了！
                                     ▼
                              从其他 Worker 偷任务
                              或从全局队列取任务

              ┌──────────────────────────────┐
              │        全局队列 (FIFO)        │
              │  [T6] [T7] [T8]              │
              └──────────────────────────────┘
```

**调度流程：**

1. **新任务优先放入当前 worker 的本地队列**——避免跨线程同步
2. **本地队列满了才放入全局队列**——本地队列有容量上限（默认 256）
3. **Worker 空闲时的查找顺序**：
   - 先看自己的本地队列
   - 再看全局队列
   - 最后随机选一个其他 Worker，从它的本地队列**尾部偷一半任务**
4. **如果所有队列都空了**——Worker 线程 park（休眠），等待被唤醒

**为什么用工作窃取而不是简单的全局队列？**

| 方案 | 优点 | 缺点 |
|------|------|------|
| 全局队列 | 实现简单 | 所有线程竞争同一把锁，高并发下成为瓶颈 |
| 固定分配 | 无竞争 | 负载不均衡，某些线程忙死，某些线程闲死 |
| **工作窃取** | **大部分操作无锁（本地队列），负载自动均衡** | 实现复杂 |

本地队列的操作是**无锁的**（基于原子操作的环形缓冲区），只有窃取操作需要 CAS（Compare-And-Swap）。在正常情况下（任务均匀分布），几乎没有线程同步开销。

### 2.4 poll 的执行过程

当 Worker 线程从队列中取出一个 Task 后：

```
Worker 线程执行循环（简化）：

loop {
    // 1. 从队列取出一个 Task
    let task = self.next_task();

    // 2. 调用 task.poll(cx)
    //    ┌─────────────────────────────────────────────┐
    //    │ poll 内部：执行 Future 状态机                  │
    //    │                                             │
    //    │  从上次挂起的状态点恢复执行                     │
    //    │       ↓                                     │
    //    │  执行用户的同步代码（计算、赋值、函数调用...）    │
    //    │       ↓                                     │
    //    │  遇到 .await → 调用内层 Future 的 poll()      │
    //    │       ├── 内层返回 Ready → 拿到结果，继续执行   │
    //    │       │   → 继续执行到下一个 .await 或结束     │
    //    │       └── 内层返回 Pending → 注册 Waker       │
    //    │           → 整个 Task 返回 Pending，挂起      │
    //    └─────────────────────────────────────────────┘
    match task.poll(cx) {
        Poll::Ready(result) => {
            // 任务完成，通知 JoinHandle，释放 Task 内存
            task.complete(result);
        }
        Poll::Pending => {
            // 任务挂起，什么都不做
            // Task 已在 .await 内部通过 Waker 注册了唤醒回调
            // 等事件就绪时，Waker 会把 Task 重新放回队列
        }
    }

    // 3. 检查是否需要处理 I/O 事件（Reactor）
    // 4. 检查是否有定时器到期
    // 5. 继续取下一个 Task
}
```

**关键点：`poll()` 不是空转等待，而是真正执行用户代码。** 每次 poll 从上次挂起的状态点恢复，执行同步代码，直到遇到下一个 `.await` 且内层 Future 返回 `Pending` 时才挂起返回。

---

## 三、Reactor：I/O 事件循环

### 3.1 Reactor 的职责

Reactor 负责与操作系统的 I/O 多路复用机制交互。它内部维护一个**映射表**：文件描述符（fd）→ Waker。当某个 fd 上的事件就绪时，Reactor 找到对应的 Waker 并调用 `wake()`。

```
                    Tokio Reactor
                    ┌─────────────────────┐
                    │                     │
TcpStream ─────────►│  fd → Waker 映射表  │◄──── OS 事件通知
UdpSocket ─────────►│                     │      (epoll_wait)
Timer ─────────────►│  注册/注销 I/O 事件  │
                    │                     │
                    └─────────────────────┘
```

### 3.2 以 TcpStream::read 为例

```rust
// 用户代码
let n = stream.read(&mut buf).await;
```

底层发生了什么：

```
第一次 poll（数据未到达）：
  1. TcpStream 调用 OS 的非阻塞 read()
  2. OS 返回 EWOULDBLOCK（没有数据）
  3. TcpStream 向 Reactor 注册：
     "当 fd=42 可读时，用这个 Waker 唤醒我"
  4. 返回 Poll::Pending

  ... Worker 去执行其他 Task ...

数据到达：
  5. OS 内核收到网络数据包，放入 socket 缓冲区
  6. Reactor 的 epoll_wait() 返回：fd=42 可读
  7. Reactor 查映射表，找到 fd=42 对应的 Waker
  8. 调用 Waker.wake()
  9. Task 被放回 Worker 的就绪队列

第二次 poll（数据已到达）：
  10. TcpStream 再次调用 OS 的非阻塞 read()
  11. OS 返回数据
  12. 返回 Poll::Ready(n)
```

### 3.3 Reactor 与 Worker 的集成

在 Tokio 的多线程运行时中，Reactor 并不是一个独立线程。它被**嵌入到 Worker 线程的事件循环中**：

```
Worker 线程的完整循环：

loop {
    // 1. 执行就绪的 Task（poll 若干个）
    run_tasks();

    // 2. 如果没有就绪的 Task，调用 epoll_wait
    //    - 有 I/O 事件 → 唤醒对应 Task，回到步骤 1
    //    - 超时 → 检查定时器，回到步骤 1
    //    - 被其他 Worker 唤醒（有新任务被窃取）→ 回到步骤 1
    park_and_wait_for_events();
}
```

这种设计避免了 Reactor 线程和 Worker 线程之间的跨线程通信开销。

---

## 四、Timer：时间轮

### 4.1 定时器的挑战

`tokio::time::sleep(Duration::from_secs(5)).await` 看起来简单，但当系统中有数万个定时器时，如何高效管理？

如果用最小堆（`BinaryHeap`），插入和删除是 O(log n)。Tokio 使用了**时间轮（Timing Wheel）**，在大多数情况下可以做到 O(1)。

### 4.2 时间轮原理

```
层级时间轮（Hierarchical Timing Wheel）：

Level 0 (1ms 精度):   [0][1][2][3]...[63]     ← 64 个槽
Level 1 (64ms 精度):  [0][1][2][3]...[63]     ← 64 个槽
Level 2 (4096ms 精度): [0][1][2][3]...[63]    ← 64 个槽
...

类似时钟的秒针、分针、时针：
- 1ms 后到期 → 放入 Level 0 的对应槽
- 100ms 后到期 → 放入 Level 1 的对应槽
- 10s 后到期 → 放入 Level 2 的对应槽

当 Level 0 转完一圈，Level 1 前进一格，
将 Level 1 当前槽中的定时器"降级"到 Level 0
```

**优势：** 插入 O(1)，到期检查 O(1)，只有降级操作需要批量处理。对于大量短期定时器（如网络超时），这比堆结构高效得多。

---

## 五、Waker：唤醒机制

### 5.1 Waker 的实现

标准库定义了 `Waker` 的接口，Tokio 实现了具体逻辑：

```
Waker.wake() 的实现（简化）：

fn wake(task: &Task) {
    // 1. 将 Task 的状态从 Idle 改为 Scheduled（原子操作）
    let prev = task.state.swap(SCHEDULED);

    // 2. 如果之前不是 Scheduled（避免重复入队）
    if prev != SCHEDULED {
        // 3. 将 Task 放入某个 Worker 的就绪队列
        worker.push_task(task);

        // 4. 如果 Worker 正在休眠，唤醒它
        worker.unpark();
    }
}
```

**关键设计：幂等性。** 多次调用 `wake()` 只会让 Task 入队一次。这通过原子状态标记实现，避免了同一个 Task 被重复 poll。

### 5.2 为什么 Waker 是 Clone + Send 的

Waker 需要被传递给 Reactor、定时器、甚至其他线程。它必须：

- **Clone**：一个 Future 可能同时等待多个事件（如 `select!`），每个事件源都需要一份 Waker
- **Send**：事件可能在任意线程上触发（Reactor 可能在不同的 Worker 线程上运行）

Tokio 的 Waker 内部是一个指向 Task 的 `Arc` 指针，Clone 只是增加引用计数。

---

## 六、spawn_blocking：阻塞任务隔离

### 6.1 为什么需要独立的阻塞线程池

如果在 async 任务中执行阻塞操作（如同步文件 I/O、CPU 密集计算），会**霸占 Worker 线程**，导致该线程上的所有其他 Task 饥饿：

```
Worker 0 的灾难场景：

[Task A: poll] → [Task A: 阻塞 10ms 的同步操作] → [Task B: 等待中...]
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                  这 10ms 内，Worker 0 上的所有 Task 都无法推进
```

`spawn_blocking` 通过将阻塞操作转移到独立线程池来解决这个问题：

```rust
let result = tokio::task::spawn_blocking(|| {
    // 在独立线程池中执行，不影响 async Worker
    std::fs::read_to_string("large_file.txt")
}).await?;
```

### 6.2 线程池的生命周期与参数

`spawn_blocking` **不是每次都创建新线程**，它使用一个按需伸缩的线程池：

```
Runtime 启动时：
  Blocking 线程池 = 空（0 个线程）

第一次 spawn_blocking：
  没有空闲线程 → 创建 Thread 0 → 执行任务

第二次 spawn_blocking（Thread 0 还在忙）：
  没有空闲线程 → 创建 Thread 1 → 执行任务

第三次 spawn_blocking（Thread 0 已完成，空闲中）：
  有空闲线程 → 复用 Thread 0 → 不创建新线程

Thread 1 完成任务后空闲 10 秒：
  超时回收 → Thread 1 销毁
```

核心逻辑：**有空闲线程就复用，没有就创建，空闲太久就回收。**

两个线程池的对比：

```
┌──────────────────────────────────────────────────────────┐
│                    Tokio Runtime                         │
│                                                          │
│  ┌─────────────────────┐  ┌────────────────────────┐    │
│  │  Worker 线程池       │  │  Blocking 线程池        │    │
│  │                     │  │                        │    │
│  │  数量: 固定          │  │  数量: 0 ~ 512 (弹性)  │    │
│  │  默认: CPU 核心数    │  │  按需创建，空闲回收      │    │
│  │  职责: poll Future  │  │  职责: 执行阻塞操作      │    │
│  │  调度: 工作窃取      │  │  调度: 简单队列分发      │    │
│  │  阻塞: 绝对禁止      │  │  阻塞: 正常行为         │    │
│  └─────────────────────┘  └────────────────────────┘    │
│           │                         │                    │
│           │    spawn_blocking()     │                    │
│           │ ──────────────────────► │                    │
│           │                         │                    │
│           │    oneshot channel       │                    │
│           │ ◄─────────────────────  │                    │
│           │    (结果传回)            │                    │
└──────────────────────────────────────────────────────────┘
```

线程池的关键参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 最大线程数 | 512 | 超过此数量的 `spawn_blocking` 调用会排队等待 |
| 空闲回收时间 | 10 秒 | 线程空闲超过此时间后被销毁 |
| 初始线程数 | 0 | 完全按需创建，启动时不预分配 |

可以通过 `runtime::Builder` 自定义：

```rust
let rt = tokio::runtime::Builder::new_multi_thread()
    .max_blocking_threads(1024)    // 最大阻塞线程数
    .thread_keep_alive(Duration::from_secs(30)) // 空闲回收时间
    .build()?;
```

### 6.3 内部工作流程

当你调用 `spawn_blocking` 时，内部经历以下步骤：

```
spawn_blocking(closure)
    │
    ▼
1. 创建 oneshot channel: (tx, rx)
    │
    ▼
2. 将 (closure, tx) 打包成一个 BlockingTask
    │
    ▼
3. 尝试获取空闲线程
    ├── 有空闲线程 → 将 BlockingTask 发送给它
    └── 无空闲线程
         ├── 未达上限 → 创建新线程，将 BlockingTask 发送给它
         └── 已达上限 → BlockingTask 放入等待队列，排队
    │
    ▼
4. 返回 JoinHandle（内部持有 rx）
```

调用方 `.await` 这个 `JoinHandle` 时，实际上是在等待 oneshot channel 的 `rx` 端：

```
Blocking 线程执行：              Async 任务等待：

1. 执行 closure                 1. poll JoinHandle
2. 得到 result                     → poll rx
3. tx.send(result) ──────────►     → Pending（数据还没来）
                                2. rx 收到数据 → Waker.wake()
                                3. 再次 poll JoinHandle
                                   → poll rx → Ready(result)
```

### 6.4 线程池瓶颈与缓解

如果同时有大量 `spawn_blocking` 调用且每个阻塞操作耗时较长，线程池可能被耗尽：

```rust
// 危险：512 个线程全部被占满，后续调用排队等待
for _ in 0..1000 {
    tokio::task::spawn_blocking(|| {
        std::thread::sleep(Duration::from_secs(60));
    });
}
```

更严重的是**间接阻塞**：async 任务 `.await` 一个 `spawn_blocking` 的 `JoinHandle`，而该阻塞任务因线程池耗尽无法被调度，导致 async 任务也被间接阻塞，进而影响整个系统的吞吐量。

**缓解策略：**

| 策略 | 说明 |
|------|------|
| 增大 `max_blocking_threads` | 通过 `runtime::Builder` 调大上限，但治标不治本 |
| 为阻塞操作设置超时 | 避免单个操作长时间占用线程 |
| 使用真正的异步替代方案 | `tokio::fs` 替代 `std::fs`，异步数据库驱动替代同步驱动 |
| 限制并发的 `spawn_blocking` 数量 | 使用 `Semaphore` 控制同时提交的阻塞任务数 |

```rust
use tokio::sync::Semaphore;
use std::sync::Arc;

let semaphore = Arc::new(Semaphore::new(64)); // 最多 64 个并发阻塞任务

let permit = semaphore.acquire().await?;
let result = tokio::task::spawn_blocking(move || {
    let _permit = permit; // permit 在阻塞任务完成后释放
    heavy_computation()
}).await?;
```

---

## 七、完整请求处理流程

以一个 HTTP 服务器处理请求为例，串联所有组件：

```
1. TcpListener::accept().await 注册到 Reactor，等待新连接
   │
   ▼
2. Reactor (epoll_wait) 检测到 listener socket 可读
   │
   ▼
3. Waker 唤醒 accept 任务，放入 Worker 0 的就绪队列
   │
   ▼
4. Worker 0 poll accept 任务 → 获得新的 TcpStream
   │
   ▼
5. tokio::spawn 创建新 Task 处理此连接
   Task 放入 Worker 0 的本地队列
   │
   ▼
6. Worker 0 poll 新 Task → 开始读取 HTTP 请求
   socket 无数据 → 向 Reactor 注册 fd 可读事件 → Pending
   │
   ▼
7. Worker 0 去 poll 其他 Task
   （Worker 2 空闲，偷走了几个 Task）
   │
   ▼
8. 客户端数据到达 → Reactor 检测到 → Waker 唤醒 Task
   │
   ▼
9. Worker 0 再次 poll → 读取完整 HTTP 请求
   │
   ▼
10. 需要查询数据库（阻塞操作）→ spawn_blocking
    │
    ▼
11. Blocking 线程执行数据库查询
    完成后通过 Waker 唤醒 async Task
    │
    ▼
12. Worker poll → 构造 HTTP 响应 → 写入 TcpStream
    socket 写缓冲区满 → Pending → 等待可写事件
    │
    ▼
13. 缓冲区可写 → Waker 唤醒 → 继续写入 → 完成
    │
    ▼
14. Task 返回 Ready → 释放资源，连接关闭
```
