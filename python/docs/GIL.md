## Python GIL 介绍及最新变化

### 什么是 GIL？

GIL（Global Interpreter Lock，全局解释器锁）是 CPython 解释器中的一个互斥锁，确保同一时刻只有一个线程执行 Python 字节码。这意味着即使在多核 CPU 上，Python 的多线程也无法实现真正的并行计算（CPU 密集型任务）。

GIL 存在的原因主要是简化 CPython 的内存管理（引用计数），但它一直是 Python 在多线程并发性能上的最大瓶颈。

### PEP 703：让 GIL 成为可选项

2023 年 10 月，PEP 703 被正式接受，提出通过 `--disable-gil` 编译选项让 GIL 变为可选。

### 各版本进展

| 版本 | 状态 |
|------|------|
| Python 3.13 | 首次引入实验性 free-threaded 构建，可通过 `--disable-gil` 编译或安装 `python3.13t` 使用 |
| Python 3.14 | free-threaded 构建从实验性升级为正式支持（PEP 779），Windows/macOS 官方安装器提供可选的 free-threaded 二进制文件 |
| Python 3.15/3.16（预计） | 可能将 no-GIL 设为默认，但取决于生态兼容性 |

### 性能影响

- 多线程 CPU 密集型任务：提速约 3.1 ~ 3.5 倍
- 单线程代码：可能慢 10% ~ 40%（因为新增了线程安全机制，如偏向引用计数）

### 当前挑战

- C 扩展兼容性：现有 C-API 扩展需要重新编译甚至修改才能线程安全。如果扩展未标记为 free-thread-safe，GIL 会被自动重新启用
- 隐式依赖 GIL 的代码可能暴露竞态条件
- NumPy 等核心库正在积极适配中
- GIL 目前仍然是默认启用的，no-GIL 是 opt-in

### 总结

Python 正处于从"有 GIL"到"无 GIL"的过渡期。3.14 是一个重要里程碑（正式支持），但要成为默认行为还需要整个生态系统的跟进，预计最早也要到 2026-2027 年。

### 参考

- [PEP 703 - Making the Global Interpreter Lock Optional](https://peps.python.org/pep-0703/)
- [Real Python - Free-threaded Python](https://realpython.com)
- [Python 3.14 Release](https://python.org)
