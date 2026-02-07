# Python 异步框架对比：asyncio、anyio、trio

## 为什么有这些框架

Python 的异步编程需要一个"事件循环"来调度协程。标准库提供了 `asyncio`，但社区认为它的 API 设计有缺陷，于是出现了替代方案。三者的关系：

```
asyncio  ← Python 标准库，最广泛
trio     ← 社区重新设计，更安全的并发模型
anyio    ← 兼容层，同一套代码跑在 asyncio 或 trio 上
```

---

## asyncio — 标准库

Python 3.4 引入，3.7+ 趋于成熟。绝大多数异步库（aiohttp、FastAPI、SQLAlchemy async）都基于它。

### 基本用法

```python
import asyncio

async def fetch_data():
    print("开始获取数据")
    await asyncio.sleep(1)  # 模拟 IO 操作
    return {"status": "ok"}

async def main():
    result = await fetch_data()
    print(result)

asyncio.run(main())
```

### 并发执行

```python
import asyncio

async def task(name, seconds):
    print(f"{name} 开始")
    await asyncio.sleep(seconds)
    print(f"{name} 完成")
    return f"{name} 结果"

async def main():
    # gather：并发执行多个协程
    results = await asyncio.gather(
        task("A", 2),
        task("B", 1),
        task("C", 3),
    )
    print(results)  # ['A 结果', 'B 结果', 'C 结果']

asyncio.run(main())
```

### Task 管理

```python
import asyncio

async def background_work():
    while True:
        print("后台运行中...")
        await asyncio.sleep(1)

async def main():
    # 创建后台任务
    bg_task = asyncio.create_task(background_work())

    # 做其他事情
    await asyncio.sleep(3)

    # 取消后台任务
    bg_task.cancel()
    try:
        await bg_task
    except asyncio.CancelledError:
        print("后台任务已取消")

asyncio.run(main())
```

### 超时控制

```python
import asyncio

async def slow_operation():
    await asyncio.sleep(10)

async def main():
    try:
        async with asyncio.timeout(3):
            await slow_operation()
    except asyncio.TimeoutError:
        print("超时了")

asyncio.run(main())
```

### 异步迭代器

```python
import asyncio

async def async_range(n):
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i

async def main():
    async for num in async_range(5):
        print(num)

asyncio.run(main())
```

### asyncio 的问题

1. **Task 取消不安全** — `cancel()` 可以在任意 `await` 点抛出 `CancelledError`，容易导致资源泄漏
2. **异常容易丢失** — `create_task()` 的异常如果没人 `await`，默默消失
3. **API 历史包袱** — 低版本 API（`loop.run_until_complete` 等）和新 API 混杂

#### 问题 1 详解：Task 取消导致资源泄漏

`cancel()` 会在下一个 `await` 点抛出 `CancelledError`。你可能会想"用 `try/finally` 就行了"，但真正的陷阱在于：如果 `finally` 中的清理操作本身是异步的，`CancelledError` 会在清理过程中再次注入，导致清理中断、资源泄漏：

```python
import asyncio

class AsyncDatabase:
    """模拟一个需要异步关闭的数据库连接"""
    def __init__(self, name):
        self.name = name
        self.closed = False
        print(f"  [连接] {name} 已打开")

    async def close(self):
        print(f"  [连接] {self.name} 开始关闭...")
        await asyncio.sleep(0.1)  # ← 第二个 CancelledError 在这里注入！
        self.closed = True
        print(f"  [连接] {self.name} 已关闭")  # 这行永远不会执行

async def bad_task():
    conn = AsyncDatabase("db-1")
    try:
        await asyncio.sleep(10)  # ← 第一个 CancelledError 在这里抛出
        print("处理数据...")
    finally:
        # 你以为 finally 能保证清理？
        # 但 close() 里有 await，cancel 会再次注入 CancelledError
        await conn.close()  # ← 清理被中断！conn 没有真正关闭
        print("清理完成")  # 这行也不会执行

async def main():
    task = asyncio.create_task(bad_task())
    await asyncio.sleep(0.1)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        print("  主程序捕获到取消")
    # db-1 连接泄漏了！close() 被中断，closed 仍然是 False

asyncio.run(main())
# 输出:
#   [连接] db-1 已打开
#   [连接] db-1 开始关闭...
#   主程序捕获到取消
# 注意：没有 "已关闭" 输出！清理被 CancelledError 打断了
```

要正确处理，需要用 `asyncio.shield()` 保护清理操作，防止取消信号穿透：

```python
async def safe_task():
    conn = AsyncDatabase("db-1")
    try:
        await asyncio.sleep(10)
        print("处理数据...")
    finally:
        # shield 阻止 CancelledError 穿透到 close() 内部
        try:
            await asyncio.shield(conn.close())
        except asyncio.CancelledError:
            pass  # 吞掉 shield 抛出的 CancelledError，让清理完成
```

问题在于 `CancelledError` 可以在**任何** `await` 点出现，包括 `finally` 块中的异步清理操作。每个持有资源的地方都需要 `shield` 保护，漏一个就泄漏。这种防御式编程非常容易出错。

trio/anyio 的结构化并发通过 nursery/TaskGroup 的作用域自动管理子任务生命周期，取消是作用域级别的而非任意注入的，从设计上避免了这类问题。

#### 问题 2 详解：异常默默丢失

`create_task()` 创建的任务如果没人 `await`，异常就消失了：

```python
import asyncio

async def exploding_task():
    await asyncio.sleep(0.1)
    raise ValueError("炸了！重要的错误！")

async def main():
    # 创建任务但不 await 它
    task = asyncio.create_task(exploding_task())

    # 继续做别的事，完全不知道 task 炸了
    await asyncio.sleep(1)
    print("主程序正常结束，完全不知道出了错")
    # task 的 ValueError 被吞掉了
    # Python 只会在 task 被垃圾回收时打一行 warning，很容易忽略

asyncio.run(main())
# 输出:
#   主程序正常结束，完全不知道出了错
#   Task exception was never retrieved
#   ...
#   ValueError: 炸了！重要的错误！
```

那行 warning 只在 task 对象被 GC 回收时才打印，时机不确定，生产环境中很容易被淹没在日志里。

对比 anyio 的 TaskGroup，异常会立即传播：

```python
import anyio

async def exploding_task():
    await anyio.sleep(0.1)
    raise ValueError("炸了！")

async def main():
    try:
        async with anyio.create_task_group() as tg:
            tg.start_soon(exploding_task)
            await anyio.sleep(1)  # 不会等到这里，异常立即传播
    except ValueError as e:
        print(f"立即捕获到异常: {e}")  # ← 马上就知道出错了

anyio.run(main)
# 输出:
#   立即捕获到异常: 炸了！
```

TaskGroup 的 `async with` 块保证：子任务一炸，其他任务取消，异常立即抛到父级。不可能有"没人知道的异常"。

---

## trio — 更安全的并发模型

trio 由 Nathaniel J. Smith 设计，核心理念是"结构化并发"（Structured Concurrency）：子任务的生命周期必须被父作用域管理，不会有"野生"任务。

### 基本用法

```python
import trio

async def fetch_data():
    print("开始获取数据")
    await trio.sleep(1)
    return {"status": "ok"}

async def main():
    result = await fetch_data()
    print(result)

trio.run(main)  # 注意：传函数，不是 main()
```

### 结构化并发 — nursery

```python
import trio

async def task(name, seconds):
    print(f"{name} 开始")
    await trio.sleep(seconds)
    print(f"{name} 完成")

async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(task, "A", 2)
        nursery.start_soon(task, "B", 1)
        nursery.start_soon(task, "C", 3)
    # 这里保证所有子任务都已完成
    print("全部完成")

trio.run(main)
```

nursery 的关键特性：
- `async with` 块结束时，所有子任务必须完成
- 任何子任务抛异常，其他子任务自动取消，异常传播到父级
- 不可能出现"忘记 await"的孤儿任务

### 超时与取消

```python
import trio

async def main():
    with trio.move_on_after(3):  # 3 秒后自动取消
        await trio.sleep(10)
        print("这行不会执行")
    print("继续执行")

trio.run(main)
```

### trio 的取舍

优点：
- 并发模型更安全，不会有资源泄漏
- 异常传播清晰
- API 设计一致

缺点：
- 生态小，很多库不支持 trio
- 不是标准库，需要额外安装
- 和 asyncio 库不兼容

---

## anyio — 兼容层

anyio 是一个异步兼容库，提供统一 API，底层可以跑在 asyncio 或 trio 上。Claude Agent SDK 就是基于 anyio 构建的。

### 为什么用 anyio

```python
# 同一份代码，两种后端都能跑
import anyio

async def main():
    print("Hello from anyio")
    await anyio.sleep(1)

anyio.run(main)                          # 默认用 asyncio
anyio.run(main, backend="trio")          # 切换到 trio
```

库作者用 anyio 写代码，用户可以自由选择 asyncio 或 trio 后端。

### 结构化并发 — TaskGroup

```python
import anyio

async def task(name, seconds):
    print(f"{name} 开始")
    await anyio.sleep(seconds)
    print(f"{name} 完成")

async def main():
    async with anyio.create_task_group() as tg:
        tg.start_soon(task, "A", 2)
        tg.start_soon(task, "B", 1)
        tg.start_soon(task, "C", 3)
    print("全部完成")

anyio.run(main)
```

和 trio 的 nursery 语义一致：块结束时所有任务必须完成，异常自动传播。

### 超时

```python
import anyio

async def main():
    with anyio.fail_after(3):
        await anyio.sleep(10)  # 3 秒后抛 TimeoutError

    with anyio.move_on_after(3):
        await anyio.sleep(10)  # 3 秒后静默跳过

anyio.run(main)
```

### 子进程

Claude Agent SDK 内部就是用这个启动 CLI 子进程：

```python
import anyio
from anyio.streams.text import TextReceiveStream

async def main():
    process = await anyio.open_process(
        ["echo", "hello"],
        stdout=-1,  # subprocess.PIPE
    )
    if process.stdout:
        stream = TextReceiveStream(process.stdout)
        async for line in stream:
            print(line.strip())

anyio.run(main)
```

### 文件操作

```python
import anyio
from anyio import Path

async def main():
    path = Path("test.txt")
    await path.write_text("hello anyio")
    content = await path.read_text()
    print(content)

anyio.run(main)
```

### 同步原语

```python
import anyio

async def main():
    # 事件
    event = anyio.Event()

    async def waiter():
        await event.wait()
        print("事件触发了")

    async def setter():
        await anyio.sleep(1)
        event.set()

    async with anyio.create_task_group() as tg:
        tg.start_soon(waiter)
        tg.start_soon(setter)

    # 信号量
    semaphore = anyio.Semaphore(3)  # 最多 3 个并发
    async with semaphore:
        await anyio.sleep(1)

    # 锁
    lock = anyio.Lock()
    async with lock:
        print("临界区")

anyio.run(main)
```

### 内存通道（替代 asyncio.Queue）

```python
import anyio

async def producer(send_stream):
    async with send_stream:
        for i in range(5):
            await send_stream.send(f"消息 {i}")
            await anyio.sleep(0.1)

async def consumer(receive_stream):
    async with receive_stream:
        async for item in receive_stream:
            print(f"收到: {item}")

async def main():
    send, receive = anyio.create_memory_object_stream(max_buffer_size=10)
    async with anyio.create_task_group() as tg:
        tg.start_soon(producer, send)
        tg.start_soon(consumer, receive)

anyio.run(main)
```

---

## 三者 API 对照

| 功能 | asyncio | trio | anyio |
|---|---|---|---|
| 启动入口 | `asyncio.run(main())` | `trio.run(main)` | `anyio.run(main)` |
| 睡眠 | `asyncio.sleep(n)` | `trio.sleep(n)` | `anyio.sleep(n)` |
| 并发执行 | `asyncio.gather(...)` | `nursery.start_soon(...)` | `tg.start_soon(...)` |
| 任务组 | `asyncio.TaskGroup()` (3.11+) | `trio.open_nursery()` | `anyio.create_task_group()` |
| 超时 | `asyncio.timeout(n)` | `trio.fail_after(n)` | `anyio.fail_after(n)` |
| 静默超时 | — | `trio.move_on_after(n)` | `anyio.move_on_after(n)` |
| 事件 | `asyncio.Event()` | `trio.Event()` | `anyio.Event()` |
| 锁 | `asyncio.Lock()` | `trio.Lock()` | `anyio.Lock()` |
| 队列/通道 | `asyncio.Queue()` | `trio.open_memory_channel()` | `anyio.create_memory_object_stream()` |
| 子进程 | `asyncio.create_subprocess_exec()` | `trio.open_process()` | `anyio.open_process()` |
| 取消 | `task.cancel()` | 取消 nursery scope | 取消 task group scope |

---

## 如何选择

| 场景 | 推荐 |
|---|---|
| 写应用代码，用 FastAPI/aiohttp | asyncio（生态最大） |
| 写库代码，希望兼容多后端 | anyio |
| 对并发安全性要求极高 | trio |
| 用 Claude Agent SDK | anyio（SDK 本身基于 anyio） |

实际上 anyio 在 asyncio 后端上运行时，性能和直接用 asyncio 几乎没有差别。选 anyio 基本没有额外成本，还能获得更好的结构化并发 API。
