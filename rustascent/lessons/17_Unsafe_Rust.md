# 第17课：Unsafe Rust

## 17.1 什么是 Unsafe Rust

Rust 的安全保证依赖编译器检查。有些正确的代码编译器无法验证，这时需要 `unsafe`。

`unsafe` 让你可以：
1. 解引用原始指针
2. 调用 unsafe 函数
3. 访问或修改可变静态变量
4. 实现 unsafe trait
5. 访问 union 的字段

**重要**：`unsafe` 不会关闭借用检查器或其他安全检查，只是允许上述五种操作。

## 17.2 原始指针

```rust
fn main() {
    let mut num = 5;

    // 创建原始指针（安全）
    let r1 = &num as *const i32;      // 不可变原始指针
    let r2 = &mut num as *mut i32;    // 可变原始指针

    // 解引用（需要 unsafe）
    unsafe {
        println!("r1 is: {}", *r1);
        println!("r2 is: {}", *r2);
    }
}
```

### 原始指针 vs 引用

| 特性 | 引用 | 原始指针 |
|------|------|----------|
| 可以为空 | 否 | 是 |
| 必须有效 | 是 | 否 |
| 自动解引用 | 是 | 否 |
| 借用规则 | 编译时检查 | 无检查 |

### 可能无效的指针

```rust
fn main() {
    // 创建指向任意地址的指针（不安全！）
    let address = 0x012345usize;
    let r = address as *const i32;

    // 解引用可能导致段错误
    // unsafe {
    //     println!("Value: {}", *r);  // 危险！
    // }
}
```

## 17.3 Unsafe 函数

```rust
unsafe fn dangerous() {
    println!("This is an unsafe function");
}

fn main() {
    // 调用 unsafe 函数需要 unsafe 块
    unsafe {
        dangerous();
    }
}
```

### 安全抽象

在 unsafe 代码外部提供安全接口：

```rust
fn split_at_mut(values: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    let len = values.len();
    let ptr = values.as_mut_ptr();

    assert!(mid <= len);

    unsafe {
        (
            std::slice::from_raw_parts_mut(ptr, mid),
            std::slice::from_raw_parts_mut(ptr.add(mid), len - mid),
        )
    }
}

fn main() {
    let mut v = vec![1, 2, 3, 4, 5, 6];
    let (left, right) = split_at_mut(&mut v, 3);

    println!("left: {:?}", left);   // [1, 2, 3]
    println!("right: {:?}", right); // [4, 5, 6]
}
```

## 17.4 extern 函数（FFI）

### 调用 C 函数

```rust
extern "C" {
    fn abs(input: i32) -> i32;
}

fn main() {
    unsafe {
        println!("abs(-3) = {}", abs(-3));
    }
}
```

### 导出函数给 C

```rust
#[no_mangle]  // 防止名称修饰
pub extern "C" fn call_from_c() {
    println!("Called from C!");
}
```

## 17.5 可变静态变量

```rust
static mut COUNTER: u32 = 0;

fn add_to_count(inc: u32) {
    unsafe {
        COUNTER += inc;
    }
}

fn main() {
    add_to_count(3);

    unsafe {
        println!("COUNTER: {}", COUNTER);
    }
}
```

### 静态变量 vs 常量

| 特性 | static | const |
|------|--------|-------|
| 内存位置 | 固定 | 内联 |
| 可以是 mut | 是（unsafe）| 否 |
| 生命周期 | 'static | 'static |

## 17.6 Unsafe Trait

```rust
unsafe trait Dangerous {
    fn dangerous_method(&self);
}

unsafe impl Dangerous for i32 {
    fn dangerous_method(&self) {
        println!("Called on {}", self);
    }
}

fn main() {
    let x: i32 = 42;
    x.dangerous_method();  // 调用不需要 unsafe
}
```

### Send 和 Sync

最常见的 unsafe trait：

```rust
// 标记类型可以跨线程转移
unsafe impl Send for MyType {}

// 标记类型可以跨线程共享引用
unsafe impl Sync for MyType {}
```

## 17.7 Union

```rust
#[repr(C)]
union IntOrFloat {
    i: i32,
    f: f32,
}

fn main() {
    let mut u = IntOrFloat { i: 42 };

    // 访问 union 字段需要 unsafe
    unsafe {
        println!("i: {}", u.i);
        u.f = 3.14;
        println!("f: {}", u.f);
        // 注意：现在读取 u.i 会得到 f 的位模式
        println!("i (as bits of f): {}", u.i);
    }
}
```

## 17.8 内存操作

### 手动内存管理

```rust
use std::alloc::{alloc, dealloc, Layout};

fn main() {
    unsafe {
        // 分配内存
        let layout = Layout::new::<u32>();
        let ptr = alloc(layout) as *mut u32;

        if ptr.is_null() {
            panic!("Allocation failed");
        }

        // 写入
        *ptr = 42;
        println!("Value: {}", *ptr);

        // 释放
        dealloc(ptr as *mut u8, layout);
    }
}
```

### ptr 模块

```rust
use std::ptr;

fn main() {
    let mut x = 5;
    let y = 10;

    unsafe {
        // 读取
        let val = ptr::read(&x);
        println!("Read: {}", val);

        // 写入
        ptr::write(&mut x, 20);
        println!("After write: {}", x);

        // 复制
        ptr::copy_nonoverlapping(&y, &mut x, 1);
        println!("After copy: {}", x);
    }
}
```

## 17.9 内联汇编

```rust
use std::arch::asm;

fn main() {
    let x: u64;

    unsafe {
        asm!(
            "mov {}, 42",
            out(reg) x,
        );
    }

    println!("x = {}", x);
}
```

## 17.10 安全使用 Unsafe 的原则

### 1. 最小化 unsafe 范围

```rust
// 不好：整个函数都是 unsafe
unsafe fn bad_example(ptr: *const i32) -> i32 {
    let value = *ptr;
    value + 1
}

// 好：只在必要处使用 unsafe
fn good_example(ptr: *const i32) -> i32 {
    let value = unsafe { *ptr };
    value + 1  // 安全代码
}
```

### 2. 文档化安全假设

```rust
/// 解引用原始指针
///
/// # Safety
///
/// - `ptr` 必须是有效的、已对齐的指针
/// - `ptr` 指向的内存必须已初始化
/// - 调用期间指向的内存不能被其他代码修改
unsafe fn deref_ptr(ptr: *const i32) -> i32 {
    *ptr
}
```

### 3. 封装为安全接口

```rust
pub struct SafeWrapper {
    ptr: *mut i32,
}

impl SafeWrapper {
    pub fn new(value: i32) -> Self {
        let boxed = Box::new(value);
        SafeWrapper {
            ptr: Box::into_raw(boxed),
        }
    }

    pub fn get(&self) -> i32 {
        // 内部使用 unsafe，对外提供安全接口
        unsafe { *self.ptr }
    }
}

impl Drop for SafeWrapper {
    fn drop(&mut self) {
        unsafe {
            drop(Box::from_raw(self.ptr));
        }
    }
}
```

### 4. 使用 Miri 检测未定义行为

```bash
# 安装 Miri
rustup +nightly component add miri

# 运行测试
cargo +nightly miri test
```

## 17.11 常见陷阱

### 悬垂指针

```rust
fn dangling() -> *const i32 {
    let x = 42;
    &x as *const i32  // 危险！x 将被释放
}
```

### 数据竞争

```rust
static mut DATA: i32 = 0;

// 多线程同时访问可变静态变量 = 数据竞争
fn bad_concurrent_access() {
    unsafe {
        DATA += 1;  // 不是原子操作！
    }
}
```

### 类型双关（Type Punning）

```rust
fn bad_transmute() {
    // 危险：不同大小类型之间转换
    let x: u64 = unsafe { std::mem::transmute([0u8; 8]) };

    // 更危险：任意类型转换
    // let s: String = unsafe { std::mem::transmute(42u64) };
}
```

## 知识要点总结

1. **unsafe** 允许 5 种操作，不关闭其他安全检查
2. **原始指针**可以为空、无效，解引用需要 unsafe
3. **extern** 用于 FFI，调用外部代码需要 unsafe
4. **可变静态变量**访问需要 unsafe（可能数据竞争）
5. **unsafe trait** 实现时需要保证安全不变量
6. 提供**安全抽象**封装 unsafe 代码
7. 文档化安全假设，最小化 unsafe 范围
