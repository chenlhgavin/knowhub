# Claude Agent SDK Python — 架构设计解析

## 一、整体架构：四层分层设计

SDK 采用经典的分层架构，自上而下分为四层：

```
┌─────────────────────────────────────────────────────┐
│            用户应用层 (User Code)                      │
│       query() / ClaudeSDKClient / @tool decorator    │
├─────────────────────────────────────────────────────┤
│            公共 API 层 (Public API)                    │
│     client.py    query.py    types.py    __init__.py │
├─────────────────────────────────────────────────────┤
│            内部实现层 (_internal)                       │
│   InternalClient    Query(控制协议)    MessageParser   │
├─────────────────────────────────────────────────────┤
│            传输层 (Transport)                          │
│   Transport (ABC)  ←→  SubprocessCLITransport        │
├─────────────────────────────────────────────────────┤
│            Claude Code CLI 进程                       │
│         (stdin/stdout/stderr 通信)                    │
└─────────────────────────────────────────────────────┘
```

每一层只与相邻层交互，职责边界清晰。上层不感知下层的实现细节，下层不依赖上层的业务逻辑。

### 模块职责

| 模块 | 文件 | 职责 |
|------|------|------|
| 公共 Client | `client.py` | `ClaudeSDKClient` — 有状态的双向交互客户端 |
| 公共 Query | `query.py` | `query()` — 无状态的一次性查询函数 |
| 类型定义 | `types.py` | 所有数据类型、消息类型、配置选项、控制协议类型 |
| 包入口 | `__init__.py` | 公共 API 导出 + `@tool` 装饰器 + `create_sdk_mcp_server()` |
| 错误类型 | `_errors.py` | 异常层次结构 |
| 内部 Client | `_internal/client.py` | `InternalClient` — 编排 Transport 和 Query |
| 控制协议 | `_internal/query.py` | `Query` — 双向控制协议处理器 |
| 消息解析 | `_internal/message_parser.py` | JSON → 强类型 Message 对象的转换 |
| 传输抽象 | `_internal/transport/__init__.py` | `Transport` ABC — 可扩展的传输接口 |
| 子进程传输 | `_internal/transport/subprocess_cli.py` | `SubprocessCLITransport` — CLI 子进程管理 |

---

## 二、接口设计：双模式 API

SDK 提供两种截然不同的使用模式，覆盖从简单到复杂的全部场景：

### 模式 A：`query()` — 无状态单次查询

输入 prompt，输出异步消息流。每次调用独立，无会话概念，适合批处理、CI/CD 自动化、简单问答。设计上是"发射后不管"（fire-and-forget）的语义。

```
用户代码 → query() → InternalClient.process_query()
    → SubprocessCLITransport.connect() (启动 CLI 子进程)
    → Query.start() + Query.initialize()
    → 写入 user message → 关闭 stdin
    → 异步迭代 parse_message(data) → yield Message
    → Query.close()
```

### 模式 B：`ClaudeSDKClient` — 有状态交互式会话

通过 `connect()` 建立持久连接，支持多轮 `query()`、中途打断（`interrupt()`）、动态切换模型（`set_model()`）、文件状态回退（`rewind_files()`）等操作。支持 `async with` 上下文管理器，确保资源自动释放。适合聊天 UI、复杂多轮编排场景。

```
用户代码 → ClaudeSDKClient(options)
    → client.connect() (或 async with)
        → SubprocessCLITransport.connect()
        → Query.start() + Query.initialize()
    → client.query("prompt")  (可多次调用)
    → async for msg in client.receive_response()
    → client.interrupt() / client.set_model() / ...
    → client.disconnect()
```

### 设计思想

双模式设计的核心是**渐进式复杂度**——简单场景用简单 API，复杂场景才引入状态管理，用户不需要为用不到的能力付出认知成本。

---

## 三、核心设计原则

### 1. 依赖倒置 + 策略模式

上层 `Query` 类依赖抽象的 `Transport` 接口，而非具体的 `SubprocessCLITransport`：

```
Query → Transport (抽象) ← SubprocessCLITransport (具体)
```

- 扩展新传输方式（如 WebSocket、HTTP）只需实现 `Transport` 的 6 个方法，上层代码零修改
- 测试时可以注入 mock transport，无需启动真实子进程
- 高层模块和低层模块都依赖抽象，符合 SOLID 中的依赖倒置原则

### 2. 接口最小化（ISP）

`Transport` 抽象仅定义 6 个方法：`connect`、`write`、`read_messages`、`close`、`is_ready`、`end_input`。

CLI 查找、命令构建、版本检查等子进程特有逻辑全部作为 `SubprocessCLITransport` 的私有方法，不污染抽象接口。未来的 WebSocket 实现无需处理与自身无关的方法。

### 3. 异步优先 + 运行时无关

整个 SDK 基于 `async/await` 构建，但底层选择 `anyio` 而非直接使用 `asyncio`。`anyio` 是异步运行时的抽象层，同时兼容 `asyncio` 和 `trio`，SDK 使用者不被锁定在特定运行时。消息流通过 `anyio` 的内存对象流（memory object stream）传递，天然支持背压控制。

### 4. 关注点分离

每个模块只做一件事：

| 层次 | 职责 |
|------|------|
| `Transport` 抽象 | 定义通信契约 |
| `SubprocessCLITransport` | 子进程生命周期 + 流式 I/O |
| `Query` | 双向控制协议的路由和调度 |
| `MessageParser` | JSON 到强类型对象的转换 |
| `InternalClient` | 编排 Transport 和 Query 的协作 |

包结构本身也体现了这一原则：`transport/__init__.py` 定义接口契约（是什么），`subprocess_cli.py` 提供具体实现（怎么做），新增传输方式只需添加文件，无需修改现有代码。

### 5. 并发安全设计（TOCTOU 防护）

`write()` 和 `close()` 共享同一把 `_write_lock`，将"检查状态 + 使用资源"封装为原子操作。如果不加锁，`close()` 可能在 `write()` 检查完 `_ready` 之后、实际写入之前关闭 stdin，导致写入已关闭的流。锁消除了 TOCTOU（Time-of-check to time-of-use）竞态条件。`end_input()` 同样共用此锁，保护 stdin 关闭与写入之间的互斥。

### 6. 投机式 JSON 解析

`_read_messages_impl()` 不依赖换行符或长度前缀界定消息边界，而是利用 JSON 自身的语法完整性进行投机式解析：

```
收到文本片段 → 追加到 buffer → 尝试 json.loads()
├─ 成功 → yield 解析结果，清空 buffer
├─ 失败 → 继续累积（可能是被截断的长行）
└─ 超过 1MB → 抛出 SDKJSONDecodeError
```

`TextReceiveStream` 可能在任意位置截断长行，无法保证每次收到完整的一行 JSON。buffer 上限（默认 1MB，可通过 `max_buffer_size` 配置）兜底防止异常数据撑爆内存。

### 7. 优雅降级（Graceful Degradation）

辅助功能的失败不阻断核心功能：

- 版本检查失败仅输出 warning，不阻断连接
- stderr 读取中的异常全部静默吞掉，不影响主流程
- `close()` 中每一步都用 `suppress(Exception)` 包裹，确保清理过程不因某一步失败而中断后续清理
- CLI 查找有多级 fallback：bundled → PATH → 硬编码常见路径

---

## 四、技术栈选型

| 技术 | 角色 | 选型理由 |
|------|------|----------|
| `anyio` | 异步运行时抽象 | 兼容 asyncio/trio，不锁定运行时 |
| `mcp` | MCP 协议支持 | 官方 MCP SDK，支持进程内 MCP Server |
| `dataclass` | 配置建模 | 轻量、类型安全、IDE 友好 |
| `TypedDict` | 协议类型 | 精确描述 JSON 结构，兼顾类型检查和运行时灵活性 |
| `Union` 判别联合 | 消息类型 | 通过 `type` 字段区分消息种类，类型安全的多态 |
| `PEP 561 py.typed` | 类型标记 | 让 MyPy 等工具识别包的类型信息 |

---

## 五、数据流设计

### 5.1 三方协作模型

SDK 的数据流本质上是一个三方协作模型：

```
Python 程序 (SDK)  ←→  Claude CLI (本地子进程)  ←→  Claude LLM (远程 API)
```

| 角色 | 是什么 | 运行位置 |
|------|--------|----------|
| Python 程序 (SDK) | SDK 客户端，负责发消息、接消息、执行回调 | 用户进程 |
| Claude CLI | 本地子进程，管理会话、编排工具调用 | 本地子进程 |
| Claude LLM | Anthropic 云端大模型，负责推理和决策 | 远程 API |

### 5.2 完整数据流

```
Python 程序 (SDK)               Claude CLI (子进程)           Claude LLM (远程)
     |                              |                           |
1.   | --- query("prompt") -------> |                           |
     |    (通过 stdin 发送)           |                           |
     |                              |                           |
2.   |                              | --- API 请求 ------------> |
     |                              |    (prompt + 工具定义)      |
     |                              |                           |
3.   |                              | <-- API 响应 ------------ |
     |                              |    (模型决定调用某工具)      |
     |                              |                           |
4.   | <-- control_request -------- |                           |
     |    (CLI 询问: 是否允许?)       |                           |
     |                              |                           |
5.   | 执行 can_use_tool 回调        |                           |
     | (在用户进程中做权限决策)        |                           |
     |                              |                           |
6.   | --- Allow/Deny ------------> |                           |
     |    (SDK 把决策发回 CLI)        |                           |
     |                              |                           |
7.   |                              | 执行工具 (若允许)           |
     |                              |                           |
8.   |                              | --- API 请求 ------------> |
     |                              |    (工具执行结果发给模型)     |
     |                              |                           |
9.   |                              | <-- API 响应 ------------ |
     |                              |    (模型生成最终回复)        |
     |                              |                           |
10.  | <-- AssistantMessage ------  |                           |
     | <-- ResultMessage ---------  |                           |
```

### 5.3 消息路由

`Query._read_messages()` 是核心消息路由器，根据消息类型分发：

```
收到消息 → 判断 type
├── control_response → 匹配 pending_control_responses[request_id]，唤醒等待的 Event
├── control_request  → 启动异步任务处理
│   ├── can_use_tool   → 调用权限回调
│   ├── hook_callback  → 调用注册的 hook 回调函数
│   └── mcp_message    → 路由到进程内 MCP Server
├── result           → 设置 _first_result_event，转发到消息流
└── 其他             → 直接转发到用户可见的消息流
```

### 5.4 Hook 回调数据流

```
Claude Code CLI                    SDK Query                 用户 Hook 函数
     │                                │                               │
     │  control_request               │                               │
     │  {subtype:"hook_callback",     │                               │
     │   callback_id, input}          │                               │
     │───────────────────────────────→│                               │
     │                                │  callback(input, context)     │
     │                                │──────────────────────────────→│
     │                                │              HookJSONOutput   │
     │                                │←──────────────────────────────│
     │  control_response              │                               │
     │  {subtype:"success",           │                               │
     │   response:{...}}              │                               │
     │←──────────────────────────────│                               │
```

### 5.5 进程内 MCP Server 数据流

```
Claude Code CLI                    SDK Query              进程内 MCP Server
     │                                │                               │
     │  control_request               │                               │
     │  {subtype:"mcp_message",       │                               │
     │   server_name, message}        │                               │
     │───────────────────────────────→│                               │
     │                                │  _handle_sdk_mcp_request()    │
     │                                │──────────────────────────────→│
     │                                │         JSONRPC response      │
     │                                │←──────────────────────────────│
     │  control_response              │                               │
     │  {mcp_response:{jsonrpc:"2.0", │                               │
     │   result:{content:[...]}}}     │                               │
     │←──────────────────────────────│                               │
```

---

## 六、扩展性设计

SDK 提供了三个主要的扩展点：

### Hook 系统

10 种事件类型（PreToolUse、PostToolUse、Stop、Notification 等），通过 matcher 模式匹配工具名，支持异步回调。开发者可以在工具执行前后注入自定义逻辑，比如拦截危险命令、记录审计日志。

### 进程内 MCP Server

通过 `@tool` 装饰器定义工具，`create_sdk_mcp_server()` 创建进程内 MCP 服务器。相比外部 MCP 进程：
- 无需额外子进程开销
- 可直接访问应用状态
- 部署更简单，调试更方便

### 自定义 Agent

通过 `AgentDefinition` 定义专用子 Agent，限定其可用工具、模型和系统提示词，实现 Orchestrator-Worker 编排模式。

---

## 七、核心数据结构

### 消息类型层次

```
Message (Union)
├── UserMessage          # 用户消息
│   ├── content: str | list[ContentBlock]
│   ├── uuid, parent_tool_use_id, tool_use_result
│
├── AssistantMessage      # 助手消息
│   ├── content: list[ContentBlock]
│   ├── model, parent_tool_use_id, error
│
├── SystemMessage         # 系统消息
│   ├── subtype, data
│
├── ResultMessage         # 结果消息 (会话结束标志)
│   ├── duration_ms, is_error, num_turns
│   ├── session_id, total_cost_usd, usage
│   └── result, structured_output
│
└── StreamEvent           # 流式事件 (部分消息)
    ├── uuid, session_id, event
    └── parent_tool_use_id
```

### 内容块类型

```
ContentBlock (Union)
├── TextBlock         { text }
├── ThinkingBlock     { thinking, signature }
├── ToolUseBlock      { id, name, input }
└── ToolResultBlock   { tool_use_id, content, is_error }
```

### 错误层次

```
ClaudeSDKError (Base)
├── CLIConnectionError        # 连接失败
│   └── CLINotFoundError      # CLI 未找到
├── ProcessError              # 进程执行失败 (exit_code, stderr)
├── CLIJSONDecodeError        # JSON 解析失败
└── MessageParseError         # 消息解析失败
```

---

## 八、架构优点总结

**低门槛、高上限**：`query()` 一行代码即可完成简单查询，`ClaudeSDKClient` 支撑复杂的多轮交互和工具编排，同一套 SDK 覆盖全场景。

**可测试性强**：Transport 抽象使得单元测试可以完全脱离真实 CLI 进程，注入 mock 即可验证控制协议逻辑。

**面向未来的扩展性**：Transport 层的抽象设计意味着未来切换到 WebSocket、HTTP 等传输方式时，上层代码完全不需要改动。

**安全性内建**：权限回调和 Hook 系统不是事后补丁，而是架构级的一等公民。LLM 不知道权限系统的存在，CLI 不会执行被拒绝的操作，SDK 在用户进程中做决策——三方各司其职，形成纵深防御。

**并发安全**：写锁消除了 TOCTOU 竞态条件，投机式 JSON 解析应对流式传输中的消息截断，stderr 后台读取通过 TaskGroup 管理生命周期——这些细节体现了对生产环境并发场景的充分考量。

**优雅降级**：版本检查失败只是 warning、stderr 异常静默处理、`close()` 中每一步都用 `suppress(Exception)` 包裹——辅助功能的失败不会阻断核心功能，提升了整体鲁棒性。
