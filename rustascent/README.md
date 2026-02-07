# Rust 从零到精通学习计划

欢迎学习 Rust 编程语言！本教程将带你从零基础到精通 Rust 的核心概念。

## 学习路线概览

```
第一阶段：基础入门（2-4周）
    ↓
第二阶段：核心概念深入（4-6周）
    ↓
第三阶段：并发与异步（3-4周）
    ↓
第四阶段：系统编程（4-6周）
    ↓
第五阶段：工程实践（4-6周）
    ↓
第六阶段：专业领域（持续）
```

---

## 第一阶段：基础入门（2-4周）

### 学习目标
掌握 Rust 基本语法，能够编写简单程序。

### 课程内容
| 课程 | 文件 | 关键概念 |
|------|------|----------|
| 第1课 | `01_环境搭建与第一个程序.md` | rustup, cargo, main 函数 |
| 第2课 | `02_变量与基本数据类型.md` | let, mut, 标量/复合类型 |
| 第3课 | `03_函数.md` | fn, 参数, 返回值, 闭包 |
| 第4课 | `04_控制流.md` | if, loop, while, for, match |

### 实践项目
- 猜数字游戏
- 温度转换器
- FizzBuzz

---

## 第二阶段：核心概念深入（4-6周）

### 学习目标
理解 Rust 独特的所有权系统和类型系统。

### 课程内容
| 课程 | 文件 | 关键概念 |
|------|------|----------|
| 第5课 | `05_所有权系统.md` | ★ ownership, borrowing, 引用, 切片 |
| 第6课 | `06_结构体与枚举.md` | struct, enum, impl, Option, Result |
| 第7课 | `07_错误处理.md` | panic!, Result, ?, 自定义错误 |
| 第8课 | `08_泛型与Trait.md` | 泛型, trait, trait bound |
| 第9课 | `09_生命周期.md` | 'a, 借用检查器, 省略规则 |
| 第10课 | `10_常用集合.md` | Vec, String, HashMap |
| 第11课 | `11_模式匹配深入.md` | 模式语法, 解构, 守卫 |
| 第12课 | `12_模块系统与包管理.md` | mod, use, Cargo |
| 第13课 | `13_迭代器与函数式编程.md` | Iterator, map, filter, fold |

### 实践项目
- minigrep（简化版 grep）
- JSON 解析器
- 链表/二叉树实现

---

## 第三阶段：并发与异步（3-4周）

### 学习目标
掌握 Rust 并发编程模型。

### 课程内容
| 课程 | 文件 | 关键概念 |
|------|------|----------|
| 第14课 | `14_智能指针.md` | Box, Rc, Arc, RefCell, Mutex |
| 第15课 | `15_并发编程基础.md` | thread, channel, 共享状态 |
| 第16课 | `16_异步编程.md` | async/await, tokio, Future |

### 实践项目
- 多线程 Web 爬虫
- 线程池实现
- 异步 HTTP 服务器

---

## 第四阶段：系统编程（4-6周）

### 学习目标
理解底层系统编程和 unsafe Rust。

### 课程内容
| 课程 | 文件 | 关键概念 |
|------|------|----------|
| 第17课 | `17_Unsafe_Rust.md` | 原始指针, FFI, unsafe trait |
| 第18课 | `18_宏.md` | macro_rules!, 过程宏 |

### 实践项目
- 实现自己的智能指针
- 编写过程宏
- 封装 C 库

---

## 第五阶段：工程实践（4-6周）

### 学习目标
掌握专业 Rust 开发技能。

### 课程内容
| 课程 | 文件 | 关键概念 |
|------|------|----------|
| 第19课 | `19_测试.md` | 单元测试, 集成测试, 基准测试 |
| 第20课 | `20_项目实战.md` | 完整项目示例 |

### 实践项目
- 发布 crate 到 crates.io
- 为开源项目贡献代码
- 性能优化实战

---

## 第六阶段：专业领域深入（持续）

根据兴趣选择方向：

| 方向 | 关键库/框架 | 项目建议 |
|------|-------------|----------|
| **Web 后端** | Axum, Actix-web, SQLx | REST API 服务 |
| **WebAssembly** | wasm-bindgen, Yew | 前端应用 |
| **嵌入式** | embedded-hal, no_std | 裸机程序 |
| **游戏开发** | Bevy, macroquad | 2D/3D 游戏 |
| **CLI 工具** | clap, ratatui | 终端应用 |
| **网络编程** | tokio, quinn | 高性能服务 |

---

## 目录结构

```
rustascent/
├── README.md                    # 本文件
├── lessons/                     # 20 课详细讲义
│   ├── 01_环境搭建与第一个程序.md
│   ├── 02_变量与基本数据类型.md
│   ├── ...
│   └── 20_项目实战.md
├── exercises/                   # 习题（按课程拆分）
│   ├── Cargo.toml               # Workspace 配置
│   ├── ex02_变量与类型/
│   │   └── src/main.rs          # 带 TODO + 单元测试
│   ├── ex03_函数/
│   ├── ex04_控制流/
│   ├── ex05_所有权/             # ★ 最重要
│   ├── ex06_结构体与枚举/
│   ├── ex07_错误处理/
│   ├── ex08_泛型与trait/
│   ├── ex09_生命周期/
│   ├── ex10_集合/
│   ├── ex13_迭代器/
│   └── ex15_并发/
└── answers/                     # 答案（按课程拆分）
    ├── Cargo.toml               # Workspace 配置
    ├── ans02_变量与类型/
    ├── ans03_函数/
    ├── ...
    └── ans15_并发/
```

---

## 快速开始

### 1. 安装 Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### 2. 验证安装

```bash
rustc --version
cargo --version
```

### 3. 开始学习

```bash
# 阅读课程
cat lessons/01_环境搭建与第一个程序.md

# 做习题（按课程逐个完成）
cd exercises

# 运行单个课程的测试
cargo test -p ex02_变量与类型
cargo test -p ex05_所有权

# 运行所有习题测试
cargo test

# 编辑对应课程的习题
# 打开 ex02_变量与类型/src/main.rs 完成 TODO

# 查看答案
cd ../answers
cargo run -p ans02_变量与类型
cargo test -p ans05_所有权
```

---

## 学习建议

### 每天坚持
- 每天学习 1-2 小时
- 代码一定要亲手敲，不要只看

### 理解所有权
第5课是 Rust 的灵魂，务必彻底理解：
- 每个值只有一个所有者
- 值在所有者离开作用域时被释放
- 使用引用进行借用

### 善用编译器
Rust 编译器的错误提示非常详细：
```
error[E0382]: borrow of moved value: `s1`
 --> src/main.rs:5:20
  |
3 |     let s2 = s1;
  |              -- value moved here
4 |
5 |     println!("{}", s1);
  |                    ^^ value borrowed here after move
  |
  = note: move occurs because `s1` has type `String`
```

### 循序渐进
- 不要跳过基础章节
- 确保每课都理解后再进入下一课
- 多做习题巩固

---

## 常见问题

**Q: 为什么我的代码无法编译？**
A: 仔细阅读编译器错误信息，它通常会告诉你如何修复。

**Q: 什么时候用 `&` 什么时候用 `clone()`？**
A: 优先使用引用 `&`，只在确实需要拥有数据副本时使用 `clone()`。

**Q: `Option` 和 `Result` 有什么区别？**
A: `Option` 表示可能不存在的值，`Result` 表示可能失败的操作。

**Q: 生命周期标注什么时候需要写？**
A: 当函数有多个引用参数且返回引用时，编译器无法推断时需要标注。

**Q: async/await 和多线程怎么选？**
A: I/O 密集型用 async，CPU 密集型用多线程。

---

祝你学习愉快！Rust 虽然学习曲线较陡，但掌握后会让你成为更好的程序员。

🦀 Happy Rusting!
