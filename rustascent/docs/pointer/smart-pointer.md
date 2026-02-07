# Rust 智能指针：设计原理与应用场景

## 目录

1. [智能指针概述](#1-智能指针概述)
2. [RAII：资源获取即初始化](#2-raii资源获取即初始化)
3. [栈分配与堆分配](#3-栈分配与堆分配)
4. [Box\<T\>：堆分配与单一所有权](#4-boxt堆分配与单一所有权)
5. [Deref 与 DerefMut：自动解引用](#5-deref-与-derefmut自动解引用)
6. [Drop trait：确定性析构](#6-drop-trait确定性析构)
7. [Rc\<T\> 与 Arc\<T\>：引用计数与共享所有权](#7-rct-与-arct引用计数与共享所有权)
8. [Weak\<T\>：弱引用与打破循环](#8-weakt弱引用与打破循环)
9. [Cell\<T\> 与 RefCell\<T\>：内部可变性](#9-cellt-与-refcellt内部可变性)
10. [Cow\<T\>：写时克隆](#10-cowt写时克隆)
11. [Pin\<T\>：固定内存位置](#11-pint固定内存位置)
12. [胖指针与 vtable](#12-胖指针与-vtable)
13. [静态分发与动态分发](#13-静态分发与动态分发)
14. [借用规则：编译器的铁律](#14-借用规则编译器的铁律)
15. [组合模式与最佳实践](#15-组合模式与最佳实践)
16. [智能指针选型决策树](#16-智能指针选型决策树)

---

## 1. 智能指针概述

### 什么是智能指针

智能指针是行为类似指针的数据结构，但附带额外的**元数据**和**能力**。与普通引用 `&T` 不同，智能指针通常**拥有**它所指向的数据。

一个类型要成为智能指针，通常需要实现两个关键 trait：

- **`Deref`**：允许像引用一样使用（`*ptr`、自动解引用）
- **`Drop`**：当值离开作用域时自动执行清理逻辑（RAII）

实际上，`String` 和 `Vec<T>` 也是智能指针——它们拥有堆上的数据，实现了 `Deref` 和 `Drop`。

### 标准库智能指针一览

| 类型 | 用途 | 所有权 | 线程安全 |
|------|------|--------|----------|
| `Box<T>` | 堆分配 | 单一所有者 | 取决于 T |
| `Rc<T>` | 引用计数 | 多所有者 | 否 |
| `Arc<T>` | 原子引用计数 | 多所有者 | 是 |
| `Cell<T>` | 内部可变性（Copy 类型） | 单一所有者 | 否 |
| `RefCell<T>` | 内部可变性（运行时检查） | 单一所有者 | 否 |
| `Cow<T>` | 写时克隆 | 按需 | 取决于 T |
| `Pin<T>` | 固定内存位置 | 取决于内部指针 | 取决于 T |
| `Weak<T>` | 弱引用（不增加引用计数） | 非所有者 | 与 Rc/Arc 对应 |
| `Mutex<T>` | 互斥锁 | 多所有者 | 是 |
| `RwLock<T>` | 读写锁 | 多所有者 | 是 |

---

## 2. RAII：资源获取即初始化

### 核心思想

**RAII（Resource Acquisition Is Initialization）** 是 C++ 首创、Rust 继承并强化的资源管理范式：

> 资源的生命周期绑定到对象的生命周期。对象创建时获取资源，对象销毁时释放资源。

在 Rust 中，RAII 通过所有权系统在编译期强制执行，不需要 GC（垃圾回收器），也不需要程序员手动释放。

### RAII 与 C/Java 的对比

```
C 语言：手动管理，容易忘记释放
    malloc → 使用 → free（容易忘记，或 double-free）

Java：GC 自动管理，但不确定性
    new → 使用 → GC 在"某个时候"回收（无法控制时机）

Rust (RAII)：编译期确定性管理
    创建 → 使用 → 离开作用域时自动调用 drop（零开销，确定性释放）
```

### Rust 的 RAII 升级版：OBRM

Rust 的资源管理有时被称为 **OBRM（Ownership-Based Resource Management）**，因为它比传统 RAII 更进一步：

- **RAII** 解决了"何时释放"的问题（确定性析构）
- **OBRM** 额外解决了"谁能访问"的问题（所有权 + 借用检查）

传统 RAII（C++）仍然允许悬垂指针、数据竞争等问题，Rust 在编译期就消灭了这些隐患。

### RAII 实际示例

```rust
struct DatabaseConnection {
    conn: RawConnection,
}

impl DatabaseConnection {
    fn new(url: &str) -> Self {
        // 资源获取 = 初始化
        DatabaseConnection {
            conn: RawConnection::connect(url),
        }
    }
}

impl Drop for DatabaseConnection {
    fn drop(&mut self) {
        // 离开作用域时自动断开连接
        self.conn.disconnect();
        println!("数据库连接已关闭");
    }
}

fn query_data() {
    let db = DatabaseConnection::new("postgres://localhost/mydb");
    // 使用 db 做查询...
}   // db 离开作用域 → 自动调用 drop → 连接关闭
    // 即使函数因 panic 提前退出，也会调用 drop
```

标准库中的 RAII 实例：

- `MutexGuard`：离开作用域自动释放锁
- `File`：离开作用域自动关闭文件描述符
- `Box<T>`：离开作用域自动释放堆内存
- `Vec<T>` / `String`：离开作用域自动释放缓冲区

---

## 3. 栈分配与堆分配

### 栈（Stack）

```
┌──────────────────────┐ ← 栈顶（低地址）
│  局部变量 z: i32     │
│  局部变量 y: f64     │
│  局部变量 x: i32     │
│  返回地址            │
│  ────────────────    │
│  上一帧的变量...     │
└──────────────────────┘ ← 栈底（高地址）
```

**特点：**

- **分配方式**：指针偏移（bump allocation），几乎零开销
- **速度**：极快，数据连续，缓存友好
- **大小限制**：主线程约 8 MB，子线程约 2 MB
- **生命周期**：与函数作用域绑定，返回时自动回收
- **限制**：**编译时必须知道大小**

```rust
fn stack_example() {
    let x: i32 = 42;              // 4 字节，栈上
    let arr: [u8; 100] = [0; 100]; // 100 字节，栈上
    let point: (f64, f64) = (1.0, 2.0); // 16 字节，栈上
}   // 函数返回时，栈帧直接弹出，全部回收
```

### 堆（Heap）

```
┌──────────────────────┐
│ 分配器元数据         │
├──────────────────────┤
│ Vec 的缓冲区         │ ← Box/Vec 指向这里
│ [1, 2, 3, 4, 5]     │
├──────────────────────┤
│ String 的缓冲区      │
│ "Hello, Rust!"       │
├──────────────────────┤
│ （碎片/空闲区域）    │
└──────────────────────┘
```

**特点：**

- **分配方式**：通过分配器（allocator）查找可用内存块
- **速度**：比栈慢，涉及分配器簿记，可能触发系统调用
- **大小限制**：受限于可用内存，几乎无上限
- **生命周期**：任意，可以超越创建它的作用域
- **优势**：**运行时决定大小**

```rust
fn heap_example() {
    let boxed: Box<i32> = Box::new(42);       // 堆上分配 4 字节
    let vec: Vec<i32> = vec![1, 2, 3, 4, 5];  // 堆上分配缓冲区
    let s: String = String::from("hello");     // 堆上分配字符串数据

    // 栈上存的是指针（+ 长度 + 容量等元数据）
    // 实际数据在堆上
}
```

### 何时选择堆分配

| 场景 | 原因 |
|------|------|
| 编译时大小未知 | `Vec<T>`、`String` 等动态大小类型 |
| 大数据 | 避免栈溢出（如百万元素的数组） |
| 递归类型 | 需要指针间接层打破无限大小递归 |
| 数据需要超越作用域 | 转移所有权、跨线程传递 |
| trait 对象 | `Box<dyn Trait>` 存储运行时多态对象 |

```rust
// 大数据放堆上，避免栈溢出
let huge: Box<[i32; 1_000_000]> = Box::new([0; 1_000_000]);

// 栈上只有一个指针（8 字节），数据在堆上（4 MB）
println!("栈上指针大小: {} 字节", std::mem::size_of_val(&huge));  // 8
```

### 堆分配的性能考量

堆本身不慢，开销来自：

1. **分配/回收开销**：分配器簿记
2. **指针间接访问**：随机指针跳转导致缓存未命中
3. **内存碎片**：大量小分配会降低局部性

**优化建议：**

- 预分配容量：`Vec::with_capacity(n)` 避免反复扩容
- 对通常较小的集合，考虑 `SmallVec`（先栈后堆）
- 大量短生命周期对象，考虑 arena 分配器
- 热路径避免 `Box<dyn Trait>`，优先静态分发

---

## 4. Box\<T\>：堆分配与单一所有权

### 设计原理

`Box<T>` 是最简单的智能指针：在堆上分配数据，在栈上存储指向该数据的指针。它拥有**单一所有权**语义——`Box` 离开作用域时，栈上的指针和堆上的数据一起被释放。

```
栈                    堆
┌─────────┐          ┌─────────┐
│ Box<i32> │ ──────→ │  42     │
│ (8 字节) │          │ (4 字节) │
└─────────┘          └─────────┘
```

`Box<T>` 编译后就是一个裸指针，没有任何额外开销。移动 `Box<T>` 只复制指针（一个 `usize`），不复制堆上的数据。

### 三大应用场景

#### 场景一：递归类型

```rust
// 编译错误："recursive type has infinite size"
// enum List {
//     Cons(i32, List),  // List 里包含 List → 无限嵌套
//     Nil,
// }

// 解决：Box 提供固定大小的指针间接层
enum List {
    Cons(i32, Box<List>),  // Cons 的大小 = i32 + 一个指针
    Nil,
}

fn main() {
    let list = Cons(1, Box::new(Cons(2, Box::new(Cons(3, Box::new(Nil))))));
}
```

编译器需要在编译时知道每个类型的大小。没有 `Box`，`List` 的大小是 `i32 + List` = `i32 + i32 + List` = ... 无穷。加了 `Box` 后，大小变成 `i32 + pointer`，是确定的。

**二叉树的同理：**

```rust
enum BinaryTree {
    Empty,
    Node(Box<TreeNode>),
}

struct TreeNode {
    value: i32,
    left: BinaryTree,
    right: BinaryTree,
}
```

#### 场景二：大数据避免栈溢出

```rust
// 栈上分配 4 MB → 可能栈溢出
// let huge_on_stack: [i32; 1_000_000] = [0; 1_000_000];

// 堆上分配 → 安全
let huge_on_heap: Box<[i32; 1_000_000]> = Box::new([0; 1_000_000]);
```

#### 场景三：trait 对象（动态分发）

```rust
trait Animal {
    fn speak(&self);
}

struct Dog;
impl Animal for Dog {
    fn speak(&self) { println!("Woof!"); }
}

struct Cat;
impl Animal for Cat {
    fn speak(&self) { println!("Meow!"); }
}

fn main() {
    // 异构集合：不同类型放在同一个 Vec 里
    let animals: Vec<Box<dyn Animal>> = vec![
        Box::new(Dog),
        Box::new(Cat),
    ];

    for animal in &animals {
        animal.speak();  // 通过 vtable 动态分发
    }
}
```

---

## 5. Deref 与 DerefMut：自动解引用

### trait 定义

```rust
pub trait Deref {
    type Target: ?Sized;
    fn deref(&self) -> &Self::Target;
}

pub trait DerefMut: Deref {
    fn deref_mut(&mut self) -> &mut Self::Target;
}
```

### 解引用操作符 `*`

当你写 `*v` 时，Rust 编译器实际执行的是 `*(v.deref())`。`deref()` 返回的是**引用**（而非值本身），`*` 再从引用取出值。返回引用而非值是为了避免将数据从 `self` 中移出。

```rust
use std::ops::Deref;

struct MyBox<T>(T);

impl<T> Deref for MyBox<T> {
    type Target = T;
    fn deref(&self) -> &T {
        &self.0
    }
}

fn main() {
    let x = MyBox(42);
    assert_eq!(*x, 42);  // *x 等价于 *(x.deref())
}
```

### 解引用强制转换（Deref Coercion）

这是 Rust 编译器的一个关键机制：**当类型不匹配时，编译器会自动、反复调用 `Deref`，直到类型匹配或无法继续。**

```
编译器的自动转换过程：

&Box<String>
  → Box<String>.deref() → &String
    → String.deref() → &str
      ✓ 匹配目标类型
```

**三条转换规则：**

1. `&T` → `&U`，当 `T: Deref<Target=U>`（不可变到不可变）
2. `&mut T` → `&mut U`，当 `T: DerefMut<Target=U>`（可变到可变）
3. `&mut T` → `&U`，当 `T: Deref<Target=U>`（可变到不可变，安全降级）

**反方向不允许**：`&T` 永远不能转成 `&mut T`，这违反借用规则。

```rust
fn hello(name: &str) {
    println!("Hello, {}!", name);
}

fn main() {
    let m = Box::new(String::from("Rust"));

    // &Box<String> → &String → &str（自动 Deref 链）
    hello(&m);

    // 如果没有 Deref Coercion，你需要写：
    hello(&(*m)[..]);
}
```

### 标准库中的 Deref 实现

| 类型 | Deref Target | 效果 |
|------|-------------|------|
| `String` | `str` | `&String` 自动转为 `&str` |
| `Vec<T>` | `[T]` | `&Vec<T>` 自动转为 `&[T]` |
| `Box<T>` | `T` | `&Box<T>` 自动转为 `&T` |
| `Rc<T>` | `T` | `&Rc<T>` 自动转为 `&T` |
| `Arc<T>` | `T` | `&Arc<T>` 自动转为 `&T` |

### 关键特性：零运行时开销

整个 Deref Coercion 过程在**编译时完成**，生成的代码与手写解引用完全相同。这是 Rust 零成本抽象的典型体现。

### 实现 Deref 的最佳实践

只在你的类型**透明地包装**另一个类型时实现 `Deref`。不要把它当作通用类型转换工具——如果方法名与 Target 类型的方法冲突，会造成混乱。

---

## 6. Drop trait：确定性析构

### trait 定义

```rust
pub trait Drop {
    fn drop(&mut self);
}
```

### Drop 顺序

```rust
struct Named(&'static str);

impl Drop for Named {
    fn drop(&mut self) {
        println!("Dropping: {}", self.0);
    }
}

fn main() {
    let a = Named("first");
    let b = Named("second");
    let c = Named("third");
}
// 输出（局部变量：声明的逆序）：
// Dropping: third
// Dropping: second
// Dropping: first
```

**Drop 顺序规则：**

- **局部变量**：声明的**逆序**（后声明的先 drop）
- **结构体字段**：声明的**正序**（先声明的先 drop）
- 元组和数组：元素顺序

### 不能直接调用 `drop()`

```rust
fn main() {
    let c = CustomResource::new();

    // 编译错误！不允许显式调用析构函数
    // c.drop();

    // 正确方式：使用 std::mem::drop
    drop(c);
    println!("资源在 main 结束前已释放");
}
```

`std::mem::drop` 的实现极其简单：`fn drop<T>(_: T) {}`。它只是取得所有权然后什么都不做——取得所有权后值离开作用域，自动触发 `Drop::drop()`。

### 关键规则

- **`Copy` 和 `Drop` 互斥**：一个类型不能同时实现两者。`Copy` 意味着按位复制安全，`Drop` 意味着有清理逻辑，二者矛盾。
- **不要在 `drop` 中 panic**：如果在栈展开（另一个 panic 正在处理中）时 `drop` 又 panic，程序会直接 abort。
- **字段自动 drop**：即使你没实现自定义 `Drop`，所有字段的析构函数仍会被自动调用。

### ManuallyDrop

当需要精细控制析构时机时，可以使用 `ManuallyDrop<T>`：

```rust
use std::mem::ManuallyDrop;

let mut data = ManuallyDrop::new(String::from("hello"));
// data 不会自动 drop
// 需要手动调用：
unsafe { ManuallyDrop::drop(&mut data); }
```

---

## 7. Rc\<T\> 与 Arc\<T\>：引用计数与共享所有权

### 设计动机

Rust 的所有权模型规定每个值有且只有一个所有者。但有些场景天然需要**多个所有者**：

- 图数据结构中，多条边指向同一个节点
- 多个 UI 组件共享同一份配置数据
- 共享不可变缓存

### Rc\<T\>：单线程引用计数

```
栈                      堆
┌──────────┐           ┌────────────────────┐
│ a: Rc<T> │ ──────┐   │ strong_count: 3    │
└──────────┘       │   │ weak_count:   0    │
┌──────────┐       ├──→│ value: T           │
│ b: Rc<T> │ ──────┤   └────────────────────┘
└──────────┘       │
┌──────────┐       │
│ c: Rc<T> │ ──────┘
└──────────┘
```

```rust
use std::rc::Rc;

fn main() {
    let a = Rc::new(vec![1, 2, 3]);
    println!("引用计数: {}", Rc::strong_count(&a));  // 1

    let b = Rc::clone(&a);  // 只增加计数，不深拷贝
    println!("引用计数: {}", Rc::strong_count(&a));  // 2

    {
        let c = Rc::clone(&a);
        println!("引用计数: {}", Rc::strong_count(&a));  // 3
    }   // c 离开作用域，计数减 1

    println!("引用计数: {}", Rc::strong_count(&a));  // 2
}   // a, b 离开作用域，计数降到 0，Vec 被释放
```

**关键约束：**

- `Rc<T>` 只提供共享引用 `&T`，不能获得 `&mut T`
- 需要修改数据时，必须组合 `Cell` 或 `RefCell`
- **不是线程安全的**：`Rc<T>` 没有实现 `Send` / `Sync`，编译器会拒绝跨线程传递

### Arc\<T\>：多线程原子引用计数

`Arc<T>` 是 `Rc<T>` 的线程安全版本，使用**原子操作**维护引用计数。

```rust
use std::sync::Arc;
use std::thread;

fn main() {
    let data = Arc::new(vec![1, 2, 3]);

    let handles: Vec<_> = (0..3).map(|_| {
        let data = Arc::clone(&data);
        thread::spawn(move || {
            println!("线程读取: {:?}", data);
        })
    }).collect();

    for h in handles {
        h.join().unwrap();
    }
}
```

**关键区别：** `Arc<T>` 让共享引用计数线程安全，但**不**让数据本身线程安全。要跨线程修改数据，必须组合 `Mutex<T>` 或 `RwLock<T>`。

### Rc 与 Arc 对比

| 特性 | `Rc<T>` | `Arc<T>` |
|------|---------|----------|
| 线程安全 | 否 | 是（原子操作） |
| 性能 | 更快（非原子操作） | 稍慢（原子操作开销） |
| 模块 | `std::rc::Rc` | `std::sync::Arc` |
| 配合可变性 | `Cell` / `RefCell` | `Mutex` / `RwLock` / Atomics |
| `Send` / `Sync` | 均否 | 均是（当 `T: Send + Sync`） |

### 共享数据结构示例

```rust
use std::rc::Rc;

enum List {
    Cons(i32, Rc<List>),
    Nil,
}

fn main() {
    //       a = 5 → 10 → Nil
    //             ↗
    //  b = 3 ────
    //             ↘
    //  c = 4 ────

    let a = Rc::new(Cons(5, Rc::new(Cons(10, Rc::new(Nil)))));
    let b = Cons(3, Rc::clone(&a));  // b 和 c 共享 a
    let c = Cons(4, Rc::clone(&a));
}
```

### 选择建议

- 单线程场景用 `Rc`，避免原子操作开销
- 跨线程场景用 `Arc`
- 库代码中更倾向使用 `Arc`，为调用者提供灵活性

---

## 8. Weak\<T\>：弱引用与打破循环

### 循环引用问题

```
A (strong_count: 1) ──→ B (strong_count: 1)
                        │
                        └──→ A (strong_count: 2!)
```

当 A 和 B 互相持有 `Rc` 强引用时，各自的 strong_count 永远不会降到 0，造成**内存泄漏**。

### Weak 的解决方案

`Weak<T>` 是不参与所有权的引用，**不增加 strong_count**：

```rust
use std::rc::{Rc, Weak};

fn main() {
    let strong = Rc::new(42);
    let weak: Weak<i32> = Rc::downgrade(&strong);  // 创建弱引用

    // upgrade() 返回 Option<Rc<T>>
    assert_eq!(*weak.upgrade().unwrap(), 42);

    drop(strong);  // 强引用计数归零，数据被释放

    // 数据已释放，upgrade 返回 None
    assert!(weak.upgrade().is_none());
}
```

### 双重引用计数

每个 `Rc`/`Arc` 维护**两个**计数器：

- **`strong_count`**：`Rc`/`Arc` 的克隆数。归零时**释放数据**
- **`weak_count`**：`Weak` 的引用数。归零时**释放元数据内存块**

### 经典模式：带父指针的树

```rust
use std::rc::{Rc, Weak};
use std::cell::RefCell;

#[derive(Debug)]
struct Node {
    value: i32,
    children: RefCell<Vec<Rc<Node>>>,  // 强引用：父拥有子
    parent: RefCell<Weak<Node>>,        // 弱引用：子不拥有父
}

fn main() {
    let leaf = Rc::new(Node {
        value: 3,
        parent: RefCell::new(Weak::new()),
        children: RefCell::new(vec![]),
    });

    let branch = Rc::new(Node {
        value: 5,
        parent: RefCell::new(Weak::new()),
        children: RefCell::new(vec![Rc::clone(&leaf)]),
    });

    // 设置 leaf 的 parent（弱引用，不会造成循环）
    *leaf.parent.borrow_mut() = Rc::downgrade(&branch);

    // branch 被释放时，leaf.parent.upgrade() 会返回 None
    println!("leaf 的父节点: {:?}", leaf.parent.borrow().upgrade());
}
```

**规则：父 → 子用强引用（`Rc`），子 → 父用弱引用（`Weak`）。**

---

## 9. Cell\<T\> 与 RefCell\<T\>：内部可变性

### 内部可变性的动机

Rust 的借用规则（多个 `&T` 或一个 `&mut T`）有时过于保守。某些情况下，你需要在一个不可变引用 `&T` 背后修改数据。内部可变性类型将借用检查从**编译时**推迟到**运行时**。

所有内部可变性类型的基础是 `UnsafeCell<T>`——Rust 中唯一合法获取可变别名数据的方式。

### Cell\<T\>：值复制的内部可变性

适用于 `Copy` 类型，通过**整体替换**值来实现可变性，无需引用追踪。

```rust
use std::cell::Cell;

fn main() {
    let counter = Cell::new(0);

    // 通过 &Cell<i32>（不可变引用）修改值
    counter.set(counter.get() + 1);
    counter.set(counter.get() + 1);

    println!("counter = {}", counter.get());  // 2
}
```

**优点：** 无运行时借用追踪开销。
**限制：** 只能 `get`/`set` 整个值，不能获取内部引用。

### RefCell\<T\>：运行时借用检查

适用于任意类型，提供引用级别的内部可变性，在运行时执行借用检查。

```rust
use std::cell::RefCell;

fn main() {
    let data = RefCell::new(vec![1, 2, 3]);

    // 不可变借用 → 返回 Ref<T>
    {
        let borrowed = data.borrow();
        println!("{:?}", *borrowed);
    }   // Ref 被 drop，借用结束

    // 可变借用 → 返回 RefMut<T>
    data.borrow_mut().push(4);

    println!("{:?}", data.borrow());  // [1, 2, 3, 4]
}
```

**内部实现：** `RefCell` 用一个有符号整数追踪借用状态：

```
计数 > 0  → 有 N 个不可变借用
计数 = 0  → 无借用
计数 = -1 → 有一个可变借用
```

- `borrow()` 时若计数 = -1（已有可变借用）→ **panic**
- `borrow_mut()` 时若计数 ≠ 0（已有任何借用）→ **panic**

**安全版本：** `try_borrow()` / `try_borrow_mut()` 返回 `Result`，不会 panic。

### Cell 家族一览

| 类型 | 线程安全 | 写入方式 | 说明 |
|------|---------|---------|------|
| `UnsafeCell<T>` | 否 | 不限（unsafe） | 所有内部可变性的基础 |
| `Cell<T>` | 否 | 值替换 | Copy 类型，无借用追踪 |
| `RefCell<T>` | 否 | 引用（运行时检查） | 任意类型，违规时 panic |
| `OnceCell<T>` | 否 | 只写一次 | 延迟初始化 |
| `OnceLock<T>` | 是 | 只写一次 | 线程安全的 `OnceCell` |
| `LazyCell<T>` | 否 | Deref 时自动初始化 | 惰性求值 |
| `LazyLock<T>` | 是 | Deref 时自动初始化 | 线程安全的 `LazyCell` |

### 多线程内部可变性

`Cell` 和 `RefCell` **不是** `Sync`，不能跨线程使用。多线程对应物：

| 单线程 | 多线程 |
|--------|--------|
| `Cell<T>` | `Atomic*` 类型 |
| `RefCell<T>` | `Mutex<T>` / `RwLock<T>` |
| `OnceCell<T>` | `OnceLock<T>` |

---

## 10. Cow\<T\>：写时克隆

### 定义

```rust
pub enum Cow<'a, B: ?Sized + ToOwned + 'a> {
    Borrowed(&'a B),     // 持有借用引用
    Owned(<B as ToOwned>::Owned),  // 持有所有权数据
}
```

`Cow`（Clone on Write）可以持有**借用**或**所有权**数据。不可变访问时直接使用借用数据（零开销），需要修改时才克隆。

### 核心方法

- `Deref`：直接以 `&B` 的方式访问数据，无论是 Borrowed 还是 Owned
- `to_mut()`：返回 `&mut`，如果是 Borrowed 则先克隆
- `into_owned()`：转换为 Owned 变体

### 典型场景：条件性修改

```rust
use std::borrow::Cow;

/// 对字符串进行 HTML 转义
/// 大多数字符串不需要转义 → 直接返回借用，零分配
/// 少数需要转义 → 分配新字符串
fn html_escape(input: &str) -> Cow<str> {
    if input.contains('<') || input.contains('>') || input.contains('&') {
        // 需要转义：分配新字符串
        let escaped = input
            .replace('&', "&amp;")
            .replace('<', "&lt;")
            .replace('>', "&gt;");
        Cow::Owned(escaped)
    } else {
        // 不需要转义：零分配，直接借用
        Cow::Borrowed(input)
    }
}

fn main() {
    let safe = html_escape("Hello, world!");      // Borrowed，零分配
    let escaped = html_escape("<script>alert(1)</script>"); // Owned，分配一次

    println!("{}", safe);     // Hello, world!
    println!("{}", escaped);  // &lt;script&gt;alert(1)&lt;/script&gt;
}
```

### 设计要点

名字是 **Clone** on Write，不是 Copy on Write。Rust 的 `Clone` 可以执行自定义深拷贝逻辑，而 `Copy` 只是 `memcpy`。

### 相关机制

`Rc::make_mut` 和 `Arc::make_mut` 提供了类似的写时克隆语义——只有在引用计数 > 1 时才克隆数据：

```rust
use std::rc::Rc;

let mut data = Rc::new(vec![1, 2, 3]);
let shared = Rc::clone(&data);

// data 被共享，make_mut 会克隆
Rc::make_mut(&mut data).push(4);

println!("{:?}", data);    // [1, 2, 3, 4]
println!("{:?}", shared);  // [1, 2, 3]  — 不受影响
```

---

## 11. Pin\<T\>：固定内存位置

### 问题背景

Rust 的 `async fn` 编译后生成的状态机可能是**自引用结构体**——内部字段引用了自身的其他字段。如果这个结构体被移动（`mem::swap`、函数参数传递等），内部引用就变成**悬垂指针**。

```
移动前：                   移动后：
┌──────────────┐          ┌──────────────┐
│ data: "abc"  │ ← ptr    │ data: "abc"  │
│ ptr: ────────┘          │ ptr: ────────┘ → 悬垂！指向旧地址
└──────────────┘          └──────────────┘
```

### Pin 的保证

`Pin<P>` 包装一个指针 `P`，**保证被指向的值不会在内存中移动**。它通过阻止获取 `&mut T`（`&mut T` 允许 `mem::swap`）来实现这一保证。

```rust
use std::pin::Pin;

// 堆上固定
let pinned: Pin<Box<MyFuture>> = Box::pin(my_async_fn());

// 栈上固定（Rust 1.68+）
let future = my_async_fn();
let pinned = std::pin::pin!(future);
```

### Unpin trait

`Unpin` 是一个自动 trait，大多数类型默认实现它：

- `Unpin` 类型可以在 `Pin` 中自由移动——`Pin` 对它们完全透明
- `async fn` / `async {}` 生成的类型是 `!Unpin`（可能自引用）
- 对于 `Unpin` 类型，`Pin::new()` 可用；对于 `!Unpin` 类型，必须用 `Box::pin()` 或 `pin!` 宏

### 与 Future::poll 的关系

```rust
pub trait Future {
    type Output;
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}
```

`poll` 接受 `self: Pin<&mut Self>` 而不是 `&mut self`，确保 future 一旦开始轮询就不能被移动。使用 `.await` 时编译器自动处理 Pin，你只在手动实现 `Future` 或编写组合器时需要直接处理 `Pin`。

### 结构化固定（Pin Projection）

对于固定的结构体，需要决定哪些字段传播固定保证：

```rust
use pin_project::pin_project;

#[pin_project]
struct MyFuture {
    #[pin]
    inner: SomeOtherFuture,  // 结构化固定
    count: usize,            // 不固定
}

impl Future for MyFuture {
    type Output = ();
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        let this = self.project();
        // this.inner: Pin<&mut SomeOtherFuture>  ← 保持固定
        // this.count: &mut usize                 ← 可自由使用
        this.inner.poll(cx)
    }
}
```

### 为什么不用其他方案

`Pin` 的设计者（without.boats）考虑并否定了：

- **移动构造函数**（C++ 风格）：无法修复所有自引用指针
- **偏移指针**：编译器无法判断哪些引用是自引用

---

## 12. 胖指针与 vtable

### 瘦指针 vs 胖指针（Fat Pointer）

**瘦指针（Thin Pointer）：** 一个 `usize`

```
&i32, &String, Box<Vec<i32>>
┌──────────┐
│ data_ptr │ → 指向具体类型的数据
└──────────┘
  8 字节
```

**胖指针（Fat Pointer）：** 两个 `usize`

```
切片引用 &[T]：
┌──────────┐
│ data_ptr │ → 指向第一个元素
│ length   │ → 元素个数
└──────────┘
  16 字节

字符串切片 &str：
┌──────────┐
│ data_ptr │ → 指向 UTF-8 字节
│ byte_len │ → 字节长度
└──────────┘
  16 字节

trait 对象 &dyn Trait：
┌──────────┐
│ data_ptr │ → 指向具体类型实例
│ vtable   │ → 指向虚函数表
└──────────┘
  16 字节
```

### vtable（虚函数表）

对于每个 `(具体类型, Trait)` 组合，编译器生成一个**全局唯一的静态 vtable**：

```
Circle 实现 Shape trait 的 vtable：
┌──────────────────────────────┐
│ drop:      fn(*mut Circle)   │ → 析构函数
│ size:      usize             │ → sizeof(Circle)
│ alignment: usize             │ → alignof(Circle)
│ area:      fn(&Circle) → f64 │ → Shape::area 的实现
│ perimeter: fn(&Circle) → f64 │ → Shape::perimeter 的实现
└──────────────────────────────┘
```

```rust
trait Shape {
    fn area(&self) -> f64;
    fn perimeter(&self) -> f64;
}

struct Circle { radius: f64 }
struct Square { side: f64 }

// 编译器为 (Circle, Shape) 和 (Square, Shape) 各生成一个 vtable
impl Shape for Circle { /* ... */ }
impl Shape for Square { /* ... */ }

fn print_area(shape: &dyn Shape) {
    // 通过 vtable 查找 area 的函数指针，间接调用
    println!("面积: {}", shape.area());
}
```

### Rust vs C++ 的 vtable 策略

- **C++**：vtable 指针是对象的隐藏成员（每个对象内部携带 vptr）
- **Rust**：vtable 指针存在胖指针中，不存在对象内部

Rust 的方式意味着对象的内存布局不受是否用作 trait 对象的影响。同一个 `Circle` 实例，既可以直接使用（无 vtable 开销），也可以作为 `&dyn Shape` 使用（只在指针处增加 vtable）。

### 对象安全（dyn 兼容性）

不是所有 trait 都能作为 trait 对象使用。要求：

- 方法不能返回 `Self`（运行时大小未知）
- 方法不能有泛型类型参数（无法生成 vtable）
- trait 不能要求 `Self: Sized`

---

## 13. 静态分发与动态分发

### 静态分发（泛型 / 单态化）

编译器为每个使用的具体类型**生成专门的函数副本**（monomorphization），方法调用在**编译时解析**。

```rust
// 编译器会为 area::<Circle> 和 area::<Square> 生成两份代码
fn area<T: Shape>(shape: &T) -> f64 {
    shape.area()  // 编译时已知具体类型，可以内联
}
```

**优点：**

- 零运行时开销（无 vtable 查找）
- 编译器可内联方法体
- 充分优化机会

**缺点：**

- 二进制体积更大（每个类型一份函数副本）
- 不能存储异构集合

### 动态分发（dyn Trait）

方法调用在**运行时**通过 vtable 查找解析。

```rust
fn area(shape: &dyn Shape) -> f64 {
    shape.area()  // 运行时 vtable 查找
}

// 异构集合成为可能
let shapes: Vec<Box<dyn Shape>> = vec![
    Box::new(Circle { radius: 1.0 }),
    Box::new(Square { side: 2.0 }),
];
```

**优点：**

- 二进制体积更小（只有一份函数代码）
- 支持异构集合
- 运行时决定类型（插件架构等）

**缺点：**

- 每次方法调用有 vtable 间接开销
- 编译器无法内联（看不穿 vtable）
- 胖指针开销（每个引用两个 `usize`）

### 对比总结

| 方面 | 静态分发（泛型） | 动态分发（`dyn Trait`） |
|------|-----------------|----------------------|
| 解析时机 | 编译时 | 运行时 |
| 机制 | 单态化 | vtable 查找 |
| 内联 | 可以 | 不可以 |
| 二进制大小 | 更大 | 更小 |
| 异构集合 | 不支持 | 支持 |
| 每次调用开销 | 零 | ~2 次指针解引用 |

### 选择建议

- **库代码**：优先泛型（静态分发），把选择权留给调用者
- **应用代码**：需要灵活性时可用动态分发，性能差异在多数场景可忽略
- **热路径**：优先静态分发

---

## 14. 借用规则：编译器的铁律

### 核心规则

在任意给定时刻，要么：

- **任意数量的不可变引用** `&T`（共享读取）
- **恰好一个可变引用** `&mut T`（独占修改）

**二者不能共存。** 且所有引用必须有效（不能悬垂）。

### 为什么这样设计

这条规则直接**消灭数据竞争**。数据竞争需要三个条件同时成立：

1. 两个或更多指针访问同一内存
2. 至少一个在写入
3. 没有同步机制

Rust 的规则确保写入（`&mut T`）是**独占的**，从而在编译时消除数据竞争。

更广义的原则：**别名（aliasing）和可变性（mutation）永远不能同时存在。**

```
&T  → 允许别名，禁止修改
&mut T → 允许修改，禁止别名
```

### 非词法生命周期（NLL）

引用的作用域从创建延伸到**最后一次使用**，而非到包含块的末尾：

```rust
let mut s = String::from("hello");

let r1 = &s;           // 不可变借用开始
let r2 = &s;           // 另一个不可变借用 → OK
println!("{} {}", r1, r2);  // r1, r2 最后一次使用 → 借用到此结束

let r3 = &mut s;       // 可变借用 → OK，此时无活跃的不可变借用
r3.push_str(" world");
println!("{}", r3);
```

### 借用规则阻止的 Bug 类别

| Bug 类型 | 如何阻止 |
|----------|---------|
| 数据竞争 | 读写不能同时存在 |
| 悬垂指针 | 引用不能超过被引用数据的生命周期 |
| 迭代器失效 | 遍历集合时不能修改集合 |
| Use-after-free | 所有权系统确保值存活足够长 |

### 内部可变性：合法的"逃生舱"

当编译器的静态分析过于保守时，`RefCell<T>` 把借用检查推迟到运行时。它执行**同样的规则**（多个 `&T` 或一个 `&mut T`），但违规时 panic 而非编译错误。

```rust
use std::cell::RefCell;

let data = RefCell::new(5);

let r1 = data.borrow();      // 不可变借用
let r2 = data.borrow();      // OK：多个不可变借用
// let r3 = data.borrow_mut(); // panic！已有不可变借用时不能可变借用

println!("{}, {}", *r1, *r2);
```

---

## 15. 组合模式与最佳实践

### 模式一：`Rc<RefCell<T>>` —— 单线程共享可变状态

```rust
use std::rc::Rc;
use std::cell::RefCell;

let shared = Rc::new(RefCell::new(vec![1, 2, 3]));

let clone1 = Rc::clone(&shared);
clone1.borrow_mut().push(4);  // 通过克隆修改原始数据

let clone2 = Rc::clone(&shared);
println!("{:?}", clone2.borrow());  // [1, 2, 3, 4]
```

### 模式二：`Arc<Mutex<T>>` —— 多线程共享可变状态

```rust
use std::sync::{Arc, Mutex};
use std::thread;

let data = Arc::new(Mutex::new(vec![]));

let handles: Vec<_> = (0..5).map(|i| {
    let data = Arc::clone(&data);
    thread::spawn(move || {
        data.lock().unwrap().push(i);
    })
}).collect();

for h in handles { h.join().unwrap(); }
println!("{:?}", data.lock().unwrap());
```

### 模式三：Weak 打破树的循环引用

```rust
struct Node {
    children: Vec<Rc<Node>>,       // 强引用：拥有子节点
    parent: RefCell<Weak<Node>>,   // 弱引用：不拥有父节点
}
```

### 模式四：Cow 实现零拷贝优化

```rust
use std::borrow::Cow;

fn normalize_path(path: &str) -> Cow<str> {
    if path.contains("//") {
        Cow::Owned(path.replace("//", "/"))
    } else {
        Cow::Borrowed(path)  // 大多数路径不需要修改 → 零分配
    }
}
```

### 模式五：Newtype + Deref 实现类型安全包装

```rust
use std::ops::Deref;

struct Email(String);

impl Deref for Email {
    type Target = str;
    fn deref(&self) -> &str { &self.0 }
}

fn send_email(to: &Email, body: &str) {
    println!("发送到 {}: {}", &**to, body);
}
```

### 最佳实践总结

1. **优先栈分配**。只在需要时使用堆（`Box`、`Vec` 等）
2. **优先静态分发**（泛型），除非需要异构集合或运行时多态
3. **谨慎使用 `Rc`/`Arc`**。它们增加开销，且可能通过循环引用泄漏内存
4. **`RefCell` 是最后手段**。运行时 panic 比编译期错误更危险。优先重构代码满足借用检查器
5. **`Cow<T>` 用于常借偶拥的场景**。函数通常返回借用数据但偶尔需要分配时使用
6. **`Weak` 打破循环引用**。图或树中的回指引用用 `Weak`
7. **只在持有外部资源时实现 `Drop`**。Rust 自动处理嵌套 drop
8. **只在透明包装时实现 `Deref`**。不要用作通用类型转换
9. **简单 Copy 类型用 `Cell` 而非 `RefCell`**。无运行时借用追踪开销
10. **`Pin` 只在处理 `!Unpin` 类型时使用**。大多数代码不需要直接处理

---

## 16. 智能指针选型决策树

```
需要堆分配？
├── 是 → 只需单一所有权？
│        ├── 是 → Box<T>
│        └── 否 → 需要跨线程？
│                 ├── 是 → Arc<T>
│                 └── 否 → Rc<T>
└── 否 → 直接使用栈上的值或引用

需要内部可变性？
├── 是 → 数据是 Copy 类型？
│        ├── 是 → Cell<T>
│        └── 否 → 需要跨线程？
│                 ├── 是 → Mutex<T> 或 RwLock<T>
│                 └── 否 → RefCell<T>
└── 否 → 使用正常的 &T / &mut T

多所有权 + 可变性？
├── 单线程 → Rc<RefCell<T>>
└── 多线程 → Arc<Mutex<T>> 或 Arc<RwLock<T>>

需要条件性修改（大多数时候只读）？
└── Cow<T>

需要防止值移动（async / 自引用）？
└── Pin<Box<T>> 或 pin!()

有循环引用风险？
└── 用 Weak<T> 打破循环
```

---

## 参考资料

- [The Rust Programming Language -- Chapter 15: Smart Pointers](https://doc.rust-lang.org/book/ch15-00-smart-pointers.html)
- [Rust Standard Library -- std::cell](https://doc.rust-lang.org/std/cell/)
- [Rust Standard Library -- std::pin](https://doc.rust-lang.org/std/pin/index.html)
- [Rust Standard Library -- Deref trait](https://doc.rust-lang.org/std/ops/trait.Deref.html)
- [Rust Standard Library -- Drop trait](https://doc.rust-lang.org/std/ops/trait.Drop.html)
- [Rust Standard Library -- Rc](https://doc.rust-lang.org/std/rc/index.html)
- [Rust Standard Library -- Arc](https://doc.rust-lang.org/std/sync/struct.Arc.html)
- [Rust Standard Library -- Cow](https://doc.rust-lang.org/std/borrow/enum.Cow.html)
- [The Rust Book -- References and Borrowing](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html)
- [Rust By Example -- RAII](https://doc.rust-lang.org/rust-by-example/scope/raii.html)
- [Effective Rust -- Item 11: Implement the Drop trait for RAII patterns](https://effective-rust.com/raii.html)
- [Cloudflare Blog -- Pin, Unpin, and why Rust needs them](https://blog.cloudflare.com/pin-and-unpin-in-rust/)
- [RFC 2349 -- Pin](https://rust-lang.github.io/rfcs/2349-pin.html)
