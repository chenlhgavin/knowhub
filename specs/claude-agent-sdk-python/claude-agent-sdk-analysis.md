# Claude Agent SDK Python — 项目全面分析

## 1. 项目概述

`claude-agent-sdk` 是 Anthropic 官方提供的 Python SDK，用于以编程方式与 Claude Code CLI 进行交互。它通过子进程管理 Claude Code CLI，并在其上构建了双向控制协议，支持一次性查询、多轮对话、工具权限控制、Hook 回调、自定义 Agent 和进程内 MCP 服务器等能力。

- 版本: 0.1.35 (Alpha)
- Python: ≥ 3.10
- 核心依赖: `anyio` (异步运行时), `mcp` (MCP 协议)
- 许可: MIT

---

## 2. 架构设计

### 2.1 分层架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户应用层 (User Code)                  │
│         query() / ClaudeSDKClient / @tool decorator      │
├─────────────────────────────────────────────────────────┤
│                   公共 API 层 (Public API)                │
│   client.py    query.py    types.py    __init__.py       │
├─────────────────────────────────────────────────────────┤
│                 内部实现层 (_internal)                     │
│   InternalClient    Query (控制协议)    MessageParser     │
├─────────────────────────────────────────────────────────┤
│                  传输层 (Transport)                       │
│   Transport (ABC)  ←→  SubprocessCLITransport            │
├─────────────────────────────────────────────────────────┤
│                 Claude Code CLI 进程                      │
│          (通过 stdin/stdout/stderr 通信)                   │
└─────────────────────────────────────────────────────────┘
```

### 2.2 模块职责

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

## 3. 详细设计

### 3.1 两种使用模式

**模式 A: `query()` — 一次性查询 (Stateless)**

```
用户代码 → query() → InternalClient.process_query()
    → SubprocessCLITransport.connect() (启动 CLI 子进程)
    → Query.start() + Query.initialize()
    → 写入 user message → 关闭 stdin
    → 异步迭代 parse_message(data) → yield Message
    → Query.close()
```

**模式 B: `ClaudeSDKClient` — 交互式会话 (Stateful)**

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

### 3.2 控制协议 (Control Protocol)

SDK 与 CLI 之间通过 stdin/stdout 上的 JSON 行协议进行双向通信:

```
SDK → CLI (stdin):
  ┌──────────────────────────────────────┐
  │ {"type":"control_request",           │  初始化/中断/权限设置
  │  "request_id":"req_1_xxxx",          │
  │  "request":{"subtype":"initialize"}} │
  ├──────────────────────────────────────┤
  │ {"type":"user",                      │  用户消息
  │  "message":{"role":"user",           │
  │  "content":"Hello"}}                 │
  ├──────────────────────────────────────┤
  │ {"type":"control_response",          │  对 CLI 请求的响应
  │  "response":{"subtype":"success",    │  (权限决策/Hook结果/MCP响应)
  │  "request_id":"..."}}                │
  └──────────────────────────────────────┘

CLI → SDK (stdout):
  ┌──────────────────────────────────────┐
  │ {"type":"control_response", ...}     │  对 SDK 请求的响应
  ├──────────────────────────────────────┤
  │ {"type":"control_request",           │  CLI 发起的请求
  │  "request":{"subtype":"can_use_tool" │  (权限询问/Hook回调/MCP调用)
  │  | "hook_callback" | "mcp_message"}} │
  ├──────────────────────────────────────┤
  │ {"type":"assistant", ...}            │  常规消息流
  │ {"type":"user", ...}                 │
  │ {"type":"system", ...}               │
  │ {"type":"result", ...}               │
  │ {"type":"stream_event", ...}         │
  └──────────────────────────────────────┘
```

### 3.3 Query 类的消息路由

`Query._read_messages()` 是核心消息路由器:

```python
async for message in transport.read_messages():
    match message.type:
        "control_response" → 匹配 pending_control_responses[request_id]，唤醒等待的 Event
        "control_request"  → 启动 _handle_control_request() 任务
            match subtype:
                "can_use_tool"   → 调用 can_use_tool 回调
                "hook_callback"  → 调用注册的 hook 回调函数
                "mcp_message"    → 路由到进程内 MCP Server
        "control_cancel_request" → (TODO: 取消支持)
        "result"           → 设置 _first_result_event，转发到消息流
        其他               → 转发到 _message_send 内存通道
```

---

## 4. 接口设计

### 4.1 公共 API

```python
# ===== 一次性查询 =====
async def query(
    *,
    prompt: str | AsyncIterable[dict],     # 提示词或消息流
    options: ClaudeAgentOptions | None,     # 配置选项
    transport: Transport | None,           # 自定义传输层
) -> AsyncIterator[Message]: ...

# ===== 交互式客户端 =====
class ClaudeSDKClient:
    def __init__(options, transport): ...
    async def connect(prompt=None): ...
    async def query(prompt, session_id="default"): ...
    async def receive_messages() -> AsyncIterator[Message]: ...
    async def receive_response() -> AsyncIterator[Message]: ...  # 到 ResultMessage 为止
    async def interrupt(): ...
    async def set_permission_mode(mode): ...
    async def set_model(model): ...
    async def rewind_files(user_message_id): ...
    async def get_mcp_status() -> dict: ...
    async def get_server_info() -> dict | None: ...
    async def disconnect(): ...
    # 支持 async with 上下文管理器

# ===== MCP 工具定义 =====
@tool(name, description, input_schema, annotations=None)
def decorator(handler) -> SdkMcpTool: ...

def create_sdk_mcp_server(name, version, tools) -> McpSdkServerConfig: ...
```

### 4.2 配置选项 (`ClaudeAgentOptions`)

```python
@dataclass
class ClaudeAgentOptions:
    # 工具控制
    tools: list[str] | ToolsPreset | None          # 基础工具集
    allowed_tools: list[str]                        # 允许的工具
    disallowed_tools: list[str]                     # 禁止的工具

    # 提示与模型
    system_prompt: str | SystemPromptPreset | None  # 系统提示
    model: str | None                               # 模型选择
    fallback_model: str | None                      # 备用模型

    # MCP 服务器
    mcp_servers: dict[str, McpServerConfig] | str | Path

    # 权限
    permission_mode: PermissionMode | None          # "default"|"acceptEdits"|"plan"|"bypassPermissions"
    can_use_tool: CanUseTool | None                 # 权限回调函数

    # Hook
    hooks: dict[HookEvent, list[HookMatcher]] | None

    # Agent
    agents: dict[str, AgentDefinition] | None       # 自定义子 Agent

    # 会话控制
    max_turns: int | None
    max_budget_usd: float | None
    continue_conversation: bool
    resume: str | None
    fork_session: bool

    # 思考控制
    thinking: ThinkingConfig | None
    effort: Literal["low","medium","high","max"] | None

    # 输出
    output_format: dict | None                      # JSON Schema 结构化输出
    include_partial_messages: bool                   # 流式部分消息

    # 环境
    cwd: str | Path | None
    cli_path: str | Path | None
    env: dict[str, str]
    settings: str | None
    sandbox: SandboxSettings | None
    plugins: list[SdkPluginConfig]
    # ... 更多
```

### 4.3 Transport 抽象接口

```python
class Transport(ABC):
    async def connect() -> None: ...
    async def write(data: str) -> None: ...
    def read_messages() -> AsyncIterator[dict]: ...
    async def close() -> None: ...
    def is_ready() -> bool: ...
    async def end_input() -> None: ...
```

---

## 5. 数据流图

### 5.1 一次性查询数据流

```
┌──────────┐    prompt     ┌────────────────┐   process_query   ┌──────────────┐
│ 用户代码  │──────────────→│  query()       │─────────────────→│InternalClient│
└──────────┘               └────────────────┘                   └──────┬───────┘
     ↑                                                                 │
     │ yield Message                                                   │
     │                                                                 ↓
     │                    ┌──────────────────────────────────────────────────┐
     │                    │              Query (控制协议层)                    │
     │                    │                                                  │
     │  parse_message()   │  ┌─────────┐    stdin (JSON)    ┌────────────┐  │
     │←──────────────────←│←─│ message  │←──── stdout ──────│            │  │
     │                    │  │ stream   │                    │ Transport  │  │
     │                    │  └─────────┘    ┌──────────────→│(Subprocess)│  │
     │                    │                 │ control_req    │            │  │
     │                    │  ┌──────────┐   │ control_resp   └─────┬──────┘  │
     │                    │  │ control  │───┘                      │         │
     │                    │  │ router   │←── hook_callback         │         │
     │                    │  │          │←── can_use_tool          │         │
     │                    │  │          │←── mcp_message           │         │
     │                    │  └──────────┘                          │         │
     │                    └───────────────────────────────────────────────────┘
     │                                                             │
     │                                                             ↓
     │                                                    ┌──────────────┐
     │                                                    │ Claude Code  │
     │                                                    │   CLI 进程    │
     │                                                    └──────────────┘
```

### 5.2 Hook 回调数据流

```
Claude Code CLI                    SDK Query                 用户 Hook 函数
     │                                │                               │
     │  control_request               │                               │
     │  {subtype:"hook_callback",     │                               │
     │   callback_id:"hook_0",        │                               │
     │   input:{tool_name,tool_input}}│                               │
     │───────────────────────────────→│                               │
     │                                │  callback(input, tool_use_id) │
     │                                │──────────────────────────────→│
     │                                │              HookJSONOutput   │
     │                                │  {permissionDecision:"deny",  │
     │                                │   reason:"..."}               │
     │                                │←──────────────────────────────│
     │  control_response              │                               │
     │  {subtype:"success",           │                               │
     │   response:{...}}              │                               │
     │←──────────────────────────────│                               │
```

### 5.3 SDK MCP Server 数据流

```
Claude Code CLI                    SDK Query              进程内 MCP Server
     │                                │                               │
     │  control_request               │                               │
     │  {subtype:"mcp_message",       │                               │
     │   server_name:"calc",          │                               │
     │   message:{method:"tools/call",│                               │
     │   params:{name:"add",...}}}    │                               │
     │───────────────────────────────→│                               │
     │                                │  _handle_sdk_mcp_request()    │
     │                                │  构造 CallToolRequest          │
     │                                │──────────────────────────────→│
     │                                │                               │ handler(args)
     │                                │  JSONRPC response             │
     │                                │←──────────────────────────────│
     │  control_response              │                               │
     │  {mcp_response:{jsonrpc:"2.0", │                               │
     │   result:{content:[...]}}}     │                               │
     │←──────────────────────────────│                               │
```

### 5.4 工具权限回调数据流 (can_use_tool)

三个角色：

| 角色 | 是什么 | 运行位置 |
|------|--------|----------|
| Python 程序 (SDK) | SDK 客户端，负责发消息、接消息、执行回调 | 用户进程 |
| Claude CLI | 本地子进程，管理会话、编排工具调用 | 本地子进程 |
| Claude LLM | Anthropic 云端大模型，负责推理和决策 | 远程 API |

```
Python 程序 (SDK)               Claude CLI (子进程)           Claude LLM (远程)
     |                              |                           |
1.   | --- query("Run echo...") --> |                           |
     |    (通过 stdin 发送给子进程)    |                           |
     |                              |                           |
2.   |                              | --- API 请求 ------------> |
     |                              |    (把 prompt + 工具定义    |
     |                              |     发给云端模型)           |
     |                              |                           |
3.   |                              | <-- API 响应 ------------ |
     |                              |    (模型决定: 调用 Bash     |
     |                              |     tool, command="echo   |
     |                              |     'hello...'")          |
     |                              |                           |
4.   | <-- tool_use 事件 ---------- |                           |
     |    (CLI 通过 stdout 告诉 SDK: |                           |
     |     模型想用 Bash 工具)        |                           |
     |                              |                           |
5.   | permission_handler() 执行    |                           |
     | (用户的 Python 回调在用户进程   |                           |
     |  里判断: echo 命令安全，允许)   |                           |
     |                              |                           |
6.   | --- Allow ----------------> |                           |
     |    (SDK 把允许结果发回给 CLI)   |                           |
     |                              |                           |
7.   |                              | 执行 Bash: echo 'hello..' |
     |                              | (CLI 在本地执行命令)        |
     |                              |                           |
8.   |                              | --- API 请求 ------------> |
     |                              |    (把工具执行结果发给模型)   |
     |                              |                           |
9.   |                              | <-- API 响应 ------------ |
     |                              |    (模型生成最终文本回复)     |
     |                              |                           |
10.  | <-- AssistantMessage ------  |                           |
     | <-- ResultMessage ---------  |                           |
     |    (SDK 收到流式消息)          |                           |
```

权限被拒绝时，流程在第 6 步分叉：

```
5.   | permission_handler() 执行
     | 检测到 "rm "，拒绝
     |
6.   | --- Deny(message=...) ----> |
     |                              |
7.   |                              | --- API 请求 ------------> |
     |                              |    (告诉模型: 工具被拒绝，    |
     |                              |     原因是 "Dangerous...")  |
     |                              |                           |
8.   |                              | <-- API 响应 ------------ |
     |                              |    (模型换个方式回复，       |
     |                              |     或尝试其他工具)         |
```

关键点：
- 回调在用户的 Python 进程中执行，不是 CLI 也不是 LLM
- Claude CLI 是中间人，通过 stdin/stdout 与 SDK 通信，同时负责调用远程 API 和本地执行工具
- Claude LLM 只做决策（调用什么工具、传什么参数），不执行任何东西，也不知道权限回调的存在
- CLI 不会执行被拒绝的命令，而是把拒绝原因反馈给 LLM，让它自行调整

---

## 6. 传输层实现 — CLI 子进程管理

SDK 的本质是一个 Claude CLI 子进程管理器。核心逻辑集中在 `_internal/transport/subprocess_cli.py` 的 `_find_cli()` 和 `_build_command()` 两个方法中。

### 6.1 CLI 查找顺序

SDK 通过 `_find_cli()` 方法按以下优先级查找 `claude` 可执行文件：

**优先级 1：SDK 内置 CLI（bundled）**

```python
bundled_path = Path(__file__).parent.parent.parent / "_bundled" / "claude"
```

检查 SDK 包自身的 `_bundled/` 目录下是否存在预打包的 CLI 二进制。当前该目录为空，不会命中。

**优先级 2：系统 PATH 查找**

```python
if cli := shutil.which("claude"):
    return cli
```

等价于终端执行 `which claude`，从 `$PATH` 环境变量中查找。

**优先级 3：常见安装位置逐一探测**

```python
locations = [
    ~/.npm-global/bin/claude        # npm global 自定义目录
    /usr/local/bin/claude           # 系统全局安装
    ~/.local/bin/claude             # 用户本地安装
    ~/node_modules/.bin/claude      # 项目级 npm install
    ~/.yarn/bin/claude              # yarn global 安装
    ~/.claude/local/claude          # Claude 自身安装目录
]
```

按顺序检查文件是否存在，命中第一个即返回。

**全部未找到：抛出异常**

```python
raise CLINotFoundError(
    "Claude Code not found. Install with:\n"
    "  npm install -g @anthropic-ai/claude-code\n"
    "\nOr provide the path via ClaudeAgentOptions:\n"
    "  ClaudeAgentOptions(cli_path='/path/to/claude')"
)
```

### 6.2 自定义 CLI 路径

通过 `ClaudeAgentOptions.cli_path` 直接指定路径，跳过所有自动查找逻辑：

```python
options = ClaudeAgentOptions(
    cli_path="/home/ubuntu/.nvm/versions/node/v24.13.0/bin/claude"
)
```

对应源码（`SubprocessCLITransport.__init__`）：

```python
self._cli_path = (
    str(options.cli_path) if options.cli_path is not None else self._find_cli()
)
```

设置了 `cli_path` 则直接使用，未设置才走 `_find_cli()` 自动查找。

### 6.3 CLI 调用方式

`_build_command()` 将 Python 配置项翻译为 CLI 命令行参数，最终构造的命令形如：

```bash
claude \
  --output-format stream-json \
  --verbose \
  --input-format stream-json \
  --system-prompt "You are a pirate." \
  --allowedTools "Bash,Read" \
  --max-turns 3 \
  --permission-mode bypassPermissions \
  --setting-sources ""
```

通过 `anyio.open_process()` 以子进程方式启动，stdin/stdout 均为 PIPE：

```python
self._process = await anyio.open_process(
    cmd,
    stdin=PIPE,      # SDK → CLI：写入 JSON 消息
    stdout=PIPE,     # CLI → SDK：返回 JSON 消息
    stderr=stderr_dest,
    cwd=self._cwd,
    env=process_env,
)
```

通信协议为 stdin/stdout 上的 JSON 行格式（每行一个 JSON 对象），双向通信：

```
SDK  →  stdin   →  CLI    (用户消息、控制请求)
SDK  ←  stdout  ←  CLI    (助手回复、控制响应、结果)
```

### 6.4 配置项到 CLI 参数的映射

| ClaudeAgentOptions 字段 | CLI 参数 | 说明 |
|---|---|---|
| `cli_path` | — | 决定调用哪个 CLI 二进制 |
| `cwd` | 进程工作目录 | 传递给 `open_process(cwd=...)` |
| `system_prompt` (str) | `--system-prompt "..."` | 自定义系统提示词 |
| `system_prompt` (preset+append) | `--append-system-prompt "..."` | 在预设提示词后追加 |
| `tools` | `--tools "Read,Bash"` / `--tools ""` | 基础工具集 |
| `allowed_tools` | `--allowedTools "Bash,Read"` | 允许的工具白名单 |
| `disallowed_tools` | `--disallowedTools "Write"` | 禁止的工具黑名单 |
| `model` | `--model claude-sonnet-4-5` | 指定模型 |
| `fallback_model` | `--fallback-model ...` | 备用模型 |
| `max_turns` | `--max-turns 3` | 最大对话轮次 |
| `max_budget_usd` | `--max-budget-usd 0.10` | 费用上限 |
| `permission_mode` | `--permission-mode bypassPermissions` | 权限模式 |
| `mcp_servers` | `--mcp-config '{...}'` | MCP 服务器配置 |
| `output_format` | `--json-schema '{...}'` | 结构化输出 Schema |
| `include_partial_messages` | `--include-partial-messages` | 启用流式部分消息 |
| `thinking` | `--max-thinking-tokens 32000` | 思考 token 预算 |
| `effort` | `--effort high` | 推理努力程度 |
| `setting_sources` | `--setting-sources "user,project"` | 设置源控制 |
| `env` | — | 合并到子进程环境变量 |
| `extra_args` | `--flag value` | 透传额外 CLI 参数 |

### 6.5 版本检查

连接前 SDK 会执行 `claude -v` 检查 CLI 版本：

```python
MINIMUM_CLAUDE_CODE_VERSION = "2.0.0"
```

低于最低版本会输出 warning 到 stderr。可通过环境变量跳过检查：

```bash
export CLAUDE_AGENT_SDK_SKIP_VERSION_CHECK=1
```

### 6.6 Transport 包架构设计优点

#### 6.6.1 策略模式 + 依赖倒置（DIP）

上层 `Query` 类依赖抽象的 `Transport` 接口，而非具体的 `SubprocessCLITransport`：

```
Query → Transport (抽象) ← SubprocessCLITransport (具体)
```

高层模块不依赖低层模块，两者都依赖抽象。扩展新的传输方式（如 WebSocket）只需实现 `Transport` 接口，`Query` 无需修改。测试时可注入 mock transport，无需启动真实子进程。

#### 6.6.2 异步优先（async-native）+ 运行时无关

整个接口基于 `async/await` 定义，底层选择 `anyio` 而非直接使用 `asyncio`：

- `anyio` 是异步运行时抽象层，同时兼容 `asyncio` 和 `trio`，SDK 使用者不被锁定在特定运行时
- `TextReceiveStream` / `TextSendStream` 提供类型安全的文本流封装，无需手动处理字节编解码
- stderr 后台读取通过 `TaskGroup` 管理，生命周期跟随 transport，不会泄漏协程

#### 6.6.3 接口最小化（ISP）

`Transport` 抽象类仅定义 6 个方法：`connect`、`write`、`read_messages`、`close`、`is_ready`、`end_input`。

`_build_command()`、`_find_cli()`、`_check_claude_version()` 等子进程特有逻辑全部作为 `SubprocessCLITransport` 的私有方法，不污染抽象接口。未来的 WebSocket 实现无需处理与自身无关的方法。

#### 6.6.4 并发安全设计（TOCTOU 防护）

`write()` 和 `close()` 共享同一把 `_write_lock`，将"检查状态 + 使用资源"封装为原子操作：

```python
# write() — 检查和使用在同一临界区内
async with self._write_lock:
    if not self._ready or not self._stdin_stream:  # 检查
        raise ...
    await self._stdin_stream.send(data)             # 使用

# close() — 状态修改也在同一把锁内
async with self._write_lock:
    self._ready = False
    await self._stdin_stream.aclose()
```

如果不加锁，`close()` 可能在 `write()` 检查完 `_ready` 之后、实际写入之前关闭 stdin，导致写入已关闭的流。锁消除了 TOCTOU（Time-of-check to time-of-use）竞态条件。`end_input()` 同样共用此锁，保护 stdin 关闭与写入之间的互斥。

#### 6.6.5 投机式 JSON 解析

`_read_messages_impl()` 不依赖换行符或长度前缀界定消息边界，而是利用 JSON 自身的语法完整性进行投机式解析：

```
收到文本片段 → 追加到 buffer → 尝试 json.loads()
├─ 成功 → yield 解析结果，清空 buffer
├─ 失败 → 继续累积（可能是被截断的长行）
└─ 超过 1MB → 抛出 SDKJSONDecodeError
```

这种设计的原因是 `TextReceiveStream` 可能在任意位置截断长行，无法保证每次收到完整的一行 JSON。buffer 上限（默认 1MB，可通过 `max_buffer_size` 配置）兜底防止异常数据撑爆内存。

#### 6.6.6 优雅降级（Graceful Degradation）

辅助功能的失败不阻断核心功能：

- 版本检查失败仅输出 warning，不阻断连接
- stderr 读取中的异常全部静默吞掉，不影响主流程
- `close()` 中每一步都用 `suppress(Exception)` 包裹，确保清理过程不因某一步失败而中断后续清理
- CLI 查找有多级 fallback：bundled → PATH → 硬编码常见路径

#### 6.6.7 关注点分离

职责划分清晰，每个方法只做一件事：

| 层次 | 职责 |
|------|------|
| `Transport` 抽象 | 定义通信契约 |
| `SubprocessCLITransport` | 子进程生命周期 + 流式 I/O |
| `_build_command()` | 配置到 CLI 参数的映射 |
| `_build_settings_value()` | settings/sandbox 的合并逻辑 |
| `_find_cli()` / `_find_bundled_cli()` | CLI 二进制的发现策略 |
| `_check_claude_version()` | 版本兼容性检查 |
| `_handle_stderr()` | stderr 流的异步消费 |

包结构本身也体现了这一原则：`__init__.py` 定义接口契约（是什么），`subprocess_cli.py` 提供具体实现（怎么做），新增传输方式只需添加文件，无需修改现有代码。

---

## 7. 核心数据结构

### 7.1 消息类型层次

```
Message (Union)
├── UserMessage          # 用户消息
│   ├── content: str | list[ContentBlock]
│   ├── uuid: str | None
│   ├── parent_tool_use_id: str | None
│   └── tool_use_result: dict | None
│
├── AssistantMessage      # 助手消息
│   ├── content: list[ContentBlock]
│   ├── model: str
│   ├── parent_tool_use_id: str | None
│   └── error: AssistantMessageError | None
│
├── SystemMessage         # 系统消息
│   ├── subtype: str
│   └── data: dict
│
├── ResultMessage         # 结果消息 (会话结束标志)
│   ├── subtype, duration_ms, duration_api_ms
│   ├── is_error, num_turns, session_id
│   ├── total_cost_usd, usage, result
│   └── structured_output
│
└── StreamEvent           # 流式事件 (部分消息)
    ├── uuid, session_id
    ├── event: dict       # 原始 Anthropic API 流事件
    └── parent_tool_use_id
```

### 7.2 内容块类型

```
ContentBlock (Union)
├── TextBlock         { text: str }
├── ThinkingBlock     { thinking: str, signature: str }
├── ToolUseBlock      { id: str, name: str, input: dict }
└── ToolResultBlock   { tool_use_id: str, content: str|list|None, is_error: bool|None }
```

### 7.3 错误层次

```
ClaudeSDKError (Base)
├── CLIConnectionError        # 连接失败
│   └── CLINotFoundError      # CLI 未找到
├── ProcessError              # 进程执行失败 (exit_code, stderr)
├── CLIJSONDecodeError        # JSON 解析失败
└── MessageParseError         # 消息解析失败
```

### 7.4 控制协议类型

```
SDKControlRequest
├── request_id: str
└── request:
    ├── SDKControlInitializeRequest       {subtype:"initialize", hooks, agents}
    ├── SDKControlInterruptRequest        {subtype:"interrupt"}
    ├── SDKControlPermissionRequest       {subtype:"can_use_tool", tool_name, input}
    ├── SDKControlSetPermissionModeRequest {subtype:"set_permission_mode", mode}
    ├── SDKHookCallbackRequest            {subtype:"hook_callback", callback_id, input}
    ├── SDKControlMcpMessageRequest       {subtype:"mcp_message", server_name, message}
    └── SDKControlRewindFilesRequest      {subtype:"rewind_files", user_message_id}

SDKControlResponse
└── response:
    ├── ControlResponse      {subtype:"success", request_id, response}
    └── ControlErrorResponse {subtype:"error", request_id, error}
```

### 7.5 Hook 类型体系

```
HookEvent = "PreToolUse" | "PostToolUse" | "PostToolUseFailure" |
            "UserPromptSubmit" | "Stop" | "SubagentStop" |
            "PreCompact" | "Notification" | "SubagentStart" | "PermissionRequest"

HookMatcher { matcher: str|None, hooks: list[HookCallback], timeout: float|None }

HookCallback = (HookInput, tool_use_id, HookContext) → Awaitable[HookJSONOutput]

HookJSONOutput = AsyncHookJSONOutput | SyncHookJSONOutput

SyncHookJSONOutput:
    continue_: bool          # 是否继续执行
    stopReason: str          # 停止原因
    decision: "block"        # 阻止决策
    reason: str              # 反馈给 Claude 的原因
    systemMessage: str       # 显示给用户的消息
    hookSpecificOutput: ...  # 事件特定输出 (permissionDecision 等)
```

---

## 8. 使用场景

| 场景 | 推荐 API | 说明 |
|------|----------|------|
| 简单问答 / 批处理 | `query()` | 无状态，fire-and-forget |
| 多轮对话 / 聊天 UI | `ClaudeSDKClient` | 有状态，支持 follow-up |
| 自定义工具 | `@tool` + `create_sdk_mcp_server` | 进程内 MCP Server |
| 工具权限控制 | `can_use_tool` 回调 | 动态允许/拒绝/修改工具调用 |
| 工具执行拦截 | Hooks (`PreToolUse`/`PostToolUse`) | 确定性的前置/后置处理 |
| 自定义子 Agent | `AgentDefinition` | 定义专用 Agent (限定工具/模型/提示) |
| CI/CD 自动化 | `query()` + `permission_mode="bypassPermissions"` | 全自动执行 |
| 结构化输出 | `output_format={"type":"json_schema",...}` | JSON Schema 约束输出 |
| 沙箱执行 | `SandboxSettings` | 隔离 bash 命令的文件/网络访问 |

---

## 9. 使用方法

### 9.1 最简用法

```python
import anyio
from claude_agent_sdk import query, AssistantMessage, TextBlock

async def main():
    async for msg in query(prompt="What is 2 + 2?"):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(block.text)

anyio.run(main)
```

### 9.2 多轮对话

```python
from claude_agent_sdk import ClaudeSDKClient

async with ClaudeSDKClient() as client:
    await client.query("What's the capital of France?")
    async for msg in client.receive_response():
        print(msg)

    await client.query("What's the population?")
    async for msg in client.receive_response():
        print(msg)
```

### 9.3 自定义工具 (进程内 MCP)

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions, ClaudeSDKClient

@tool("add", "Add two numbers", {"a": float, "b": float})
async def add(args):
    return {"content": [{"type": "text", "text": str(args["a"] + args["b"])}]}

server = create_sdk_mcp_server("calc", tools=[add])
options = ClaudeAgentOptions(
    mcp_servers={"calc": server},
    allowed_tools=["mcp__calc__add"],
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("What is 3 + 5?")
    async for msg in client.receive_response():
        print(msg)
```

### 9.4 Hook 拦截

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, HookMatcher

async def block_dangerous_commands(input_data, tool_use_id, context):
    if "rm -rf" in input_data.get("tool_input", {}).get("command", ""):
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Dangerous command blocked",
            }
        }
    return {}

options = ClaudeAgentOptions(
    hooks={"PreToolUse": [HookMatcher(matcher="Bash", hooks=[block_dangerous_commands])]}
)
```

### 9.5 工具权限回调

```python
from claude_agent_sdk import (
    ClaudeAgentOptions, ClaudeSDKClient,
    PermissionResultAllow, PermissionResultDeny,
)

async def permission_handler(tool_name, input_data, context):
    if tool_name in ["Read", "Glob"]:
        return PermissionResultAllow()
    if tool_name == "Bash" and "rm" in input_data.get("command", ""):
        return PermissionResultDeny(message="Destructive commands not allowed")
    return PermissionResultAllow()

options = ClaudeAgentOptions(can_use_tool=permission_handler)
```

### 9.6 自定义 Agent

```python
from claude_agent_sdk import ClaudeAgentOptions, AgentDefinition, query

options = ClaudeAgentOptions(
    agents={
        "reviewer": AgentDefinition(
            description="Reviews code for best practices",
            prompt="You are a code reviewer...",
            tools=["Read", "Grep"],
            model="sonnet",
        ),
    },
)

async for msg in query(prompt="Use the reviewer agent to review main.py", options=options):
    print(msg)
```
