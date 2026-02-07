# 第8课：泛型与 Trait

## 8.1 泛型函数

```rust
// 不使用泛型：需要为每种类型写一个函数
fn largest_i32(list: &[i32]) -> &i32 {
    let mut largest = &list[0];
    for item in list {
        if item > largest {
            largest = item;
        }
    }
    largest
}

fn largest_char(list: &[char]) -> &char {
    let mut largest = &list[0];
    for item in list {
        if item > largest {
            largest = item;
        }
    }
    largest
}

// 使用泛型：一个函数适用多种类型
fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut largest = &list[0];
    for item in list {
        if item > largest {
            largest = item;
        }
    }
    largest
}

fn main() {
    let numbers = vec![34, 50, 25, 100, 65];
    println!("最大数: {}", largest(&numbers));

    let chars = vec!['y', 'm', 'a', 'q'];
    println!("最大字符: {}", largest(&chars));
}
```

## 8.2 泛型结构体

```rust
// 单个类型参数
struct Point<T> {
    x: T,
    y: T,
}

// 多个类型参数
struct Pair<T, U> {
    first: T,
    second: U,
}

fn main() {
    let integer_point = Point { x: 5, y: 10 };
    let float_point = Point { x: 1.0, y: 4.0 };

    // 错误：x 和 y 必须是相同类型
    // let wrong = Point { x: 5, y: 4.0 };

    // 使用 Pair 可以有不同类型
    let pair = Pair { first: 5, second: "hello" };
}
```

## 8.3 泛型枚举

```rust
// 标准库中的 Option 和 Result 就是泛型枚举
enum Option<T> {
    Some(T),
    None,
}

enum Result<T, E> {
    Ok(T),
    Err(E),
}

// 自定义泛型枚举
enum Tree<T> {
    Leaf(T),
    Node {
        value: T,
        left: Box<Tree<T>>,
        right: Box<Tree<T>>,
    },
}
```

## 8.4 泛型方法

```rust
struct Point<T> {
    x: T,
    y: T,
}

impl<T> Point<T> {
    fn x(&self) -> &T {
        &self.x
    }

    fn y(&self) -> &T {
        &self.y
    }
}

// 只为特定类型实现方法
impl Point<f64> {
    fn distance_from_origin(&self) -> f64 {
        (self.x.powi(2) + self.y.powi(2)).sqrt()
    }
}

fn main() {
    let p = Point { x: 5, y: 10 };
    println!("x = {}", p.x());

    let p2 = Point { x: 3.0, y: 4.0 };
    println!("距离原点: {}", p2.distance_from_origin());

    // 错误：Point<i32> 没有 distance_from_origin 方法
    // let p3 = Point { x: 3, y: 4 };
    // p3.distance_from_origin();
}
```

## 8.5 Trait 定义

Trait 定义共享行为，类似其他语言的接口。

```rust
// 定义 trait
trait Summary {
    fn summarize(&self) -> String;
}

struct NewsArticle {
    headline: String,
    location: String,
    author: String,
    content: String,
}

// 为类型实现 trait
impl Summary for NewsArticle {
    fn summarize(&self) -> String {
        format!("{}, by {} ({})", self.headline, self.author, self.location)
    }
}

struct Tweet {
    username: String,
    content: String,
}

impl Summary for Tweet {
    fn summarize(&self) -> String {
        format!("{}: {}", self.username, self.content)
    }
}

fn main() {
    let article = NewsArticle {
        headline: String::from("重大新闻"),
        location: String::from("北京"),
        author: String::from("张三"),
        content: String::from("..."),
    };

    println!("{}", article.summarize());
}
```

## 8.6 默认实现

```rust
trait Summary {
    fn summarize_author(&self) -> String;

    // 默认实现
    fn summarize(&self) -> String {
        format!("(阅读更多来自 {} 的内容...)", self.summarize_author())
    }
}

struct Tweet {
    username: String,
    content: String,
}

impl Summary for Tweet {
    fn summarize_author(&self) -> String {
        format!("@{}", self.username)
    }
    // 使用默认的 summarize 实现
}

fn main() {
    let tweet = Tweet {
        username: String::from("rust_lang"),
        content: String::from("Hello Rustaceans!"),
    };

    println!("{}", tweet.summarize());
    // 输出: (阅读更多来自 @rust_lang 的内容...)
}
```

## 8.7 Trait 作为参数

```rust
// 方式1：impl Trait 语法
fn notify(item: &impl Summary) {
    println!("新消息: {}", item.summarize());
}

// 方式2：Trait Bound 语法
fn notify_bound<T: Summary>(item: &T) {
    println!("新消息: {}", item.summarize());
}

// 多个参数，相同类型
fn notify_both<T: Summary>(item1: &T, item2: &T) {
    println!("{}", item1.summarize());
    println!("{}", item2.summarize());
}

// 多个参数，可以不同类型
fn notify_different(item1: &impl Summary, item2: &impl Summary) {
    println!("{}", item1.summarize());
    println!("{}", item2.summarize());
}
```

## 8.8 多个 Trait Bound

```rust
use std::fmt::Display;

// 方式1：+ 语法
fn notify(item: &(impl Summary + Display)) {
    println!("{}", item.summarize());
    println!("{}", item);
}

// 方式2：泛型形式
fn notify_generic<T: Summary + Display>(item: &T) {
    println!("{}", item.summarize());
    println!("{}", item);
}

// 使用 where 子句（更清晰）
fn some_function<T, U>(t: &T, u: &U) -> i32
where
    T: Summary + Clone,
    U: Clone + std::fmt::Debug,
{
    // ...
    0
}
```

## 8.9 返回实现 Trait 的类型

```rust
// 返回实现了 Summary 的类型
fn returns_summarizable() -> impl Summary {
    Tweet {
        username: String::from("rust_lang"),
        content: String::from("Hello!"),
    }
}

// 注意：只能返回单一类型
// 以下代码不能编译：
// fn returns_summarizable(switch: bool) -> impl Summary {
//     if switch {
//         NewsArticle { ... }  // 类型 A
//     } else {
//         Tweet { ... }        // 类型 B
//     }
// }
```

## 8.10 使用 Trait Bound 有条件地实现方法

```rust
use std::fmt::Display;

struct Pair<T> {
    x: T,
    y: T,
}

// 所有 Pair<T> 都有的方法
impl<T> Pair<T> {
    fn new(x: T, y: T) -> Self {
        Self { x, y }
    }
}

// 只有 T 实现了 Display + PartialOrd 才有的方法
impl<T: Display + PartialOrd> Pair<T> {
    fn cmp_display(&self) {
        if self.x >= self.y {
            println!("最大值是 x = {}", self.x);
        } else {
            println!("最大值是 y = {}", self.y);
        }
    }
}
```

## 8.11 常用标准库 Trait

### Debug

```rust
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p = Point { x: 1, y: 2 };
    println!("{:?}", p);   // Point { x: 1, y: 2 }
    println!("{:#?}", p);  // 美化输出
}
```

### Clone 和 Copy

```rust
#[derive(Clone)]
struct Container {
    data: Vec<i32>,
}

#[derive(Clone, Copy)]
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let c1 = Container { data: vec![1, 2, 3] };
    let c2 = c1.clone();  // 必须显式 clone

    let p1 = Point { x: 1, y: 2 };
    let p2 = p1;  // 自动 copy
    println!("{:?}", p1);  // p1 仍然有效
}
```

### PartialEq 和 Eq

```rust
#[derive(PartialEq, Eq)]
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p1 = Point { x: 1, y: 2 };
    let p2 = Point { x: 1, y: 2 };
    let p3 = Point { x: 3, y: 4 };

    println!("{}", p1 == p2);  // true
    println!("{}", p1 != p3);  // true
}
```

### PartialOrd 和 Ord

```rust
#[derive(PartialEq, Eq, PartialOrd, Ord)]
struct Score {
    value: i32,
}

fn main() {
    let s1 = Score { value: 100 };
    let s2 = Score { value: 90 };

    println!("{}", s1 > s2);  // true

    let mut scores = vec![
        Score { value: 85 },
        Score { value: 92 },
        Score { value: 78 },
    ];
    scores.sort();
}
```

### Default

```rust
#[derive(Default)]
struct Config {
    debug: bool,
    max_connections: u32,
    timeout: u64,
}

fn main() {
    let config = Config::default();
    // debug: false, max_connections: 0, timeout: 0

    // 部分自定义
    let config2 = Config {
        debug: true,
        ..Default::default()
    };
}
```

### From 和 Into

```rust
#[derive(Debug)]
struct Number {
    value: i32,
}

impl From<i32> for Number {
    fn from(item: i32) -> Self {
        Number { value: item }
    }
}

fn main() {
    let num1 = Number::from(42);
    let num2: Number = 100.into();  // Into 自动实现

    println!("{:?}, {:?}", num1, num2);
}
```

## 8.12 Trait 对象

当需要运行时多态时使用 trait 对象。

```rust
trait Draw {
    fn draw(&self);
}

struct Circle {
    radius: f64,
}

impl Draw for Circle {
    fn draw(&self) {
        println!("画一个半径为 {} 的圆", self.radius);
    }
}

struct Rectangle {
    width: f64,
    height: f64,
}

impl Draw for Rectangle {
    fn draw(&self) {
        println!("画一个 {}x{} 的矩形", self.width, self.height);
    }
}

fn main() {
    // 使用 dyn Trait 创建 trait 对象
    let shapes: Vec<Box<dyn Draw>> = vec![
        Box::new(Circle { radius: 5.0 }),
        Box::new(Rectangle { width: 10.0, height: 20.0 }),
    ];

    for shape in shapes {
        shape.draw();
    }
}
```

### 泛型 vs Trait 对象

| 特性 | 泛型 | Trait 对象 |
|------|------|------------|
| 多态方式 | 编译时（静态分发）| 运行时（动态分发）|
| 性能 | 更快（内联优化）| 有虚表开销 |
| 代码大小 | 可能膨胀（单态化）| 更小 |
| 类型限制 | 必须在编译时已知 | 可以运行时决定 |

## 知识要点总结

1. **泛型**让代码适用于多种类型
2. **Trait**定义共享行为
3. **Trait Bound**限制泛型必须实现特定 trait
4. **impl Trait**简化语法，用于参数和返回值
5. **where 子句**让复杂的 trait bound 更清晰
6. **derive**可以自动实现常用 trait
7. **Trait 对象**（dyn Trait）提供运行时多态
