# 分层架构与API设计

## 一、分层架构

### 1.1 为什么要分层

分层架构的核心目的是**关注点分离**：每一层只关心自己的职责，通过定义清晰的层间接口来降低耦合。

分层的好处：
- 每层可以独立变化，不影响其他层
- 每层可以独立测试
- 团队可以按层分工协作
- 技术选型可以按层替换（如更换数据库只影响数据访问层）

### 1.2 经典三层架构

```
┌─────────────────────────────┐
│     表现层（Presentation）    │  处理用户交互、参数校验、响应格式化
├─────────────────────────────┤
│     业务层（Business Logic）  │  核心业务规则、流程编排、事务管理
├─────────────────────────────┤
│     数据访问层（Data Access）  │  数据库操作、缓存操作、外部API调用
└─────────────────────────────┘

依赖方向：表现层 → 业务层 → 数据访问层（自上而下单向依赖）
```

### 1.3 MVC / MVP / MVVM

**MVC（Model-View-Controller）：**
```
用户操作 → Controller → 更新 Model
                          ↓
              View ← 监听 Model 变化

- Model：数据和业务逻辑
- View：界面展示
- Controller：接收用户输入，协调 Model 和 View
```

**MVP（Model-View-Presenter）：**
```
用户操作 → View → Presenter → Model
                    ↓
              View ← Presenter

- View 和 Model 完全解耦
- Presenter 持有 View 的接口引用
- 便于单元测试（可以 mock View）
```

**MVVM（Model-View-ViewModel）：**
```
用户操作 → View ⇄ ViewModel → Model

- View 和 ViewModel 通过数据绑定自动同步
- 代表框架：Vue.js、React（单向数据流变体）、WPF
```

### 1.4 整洁架构（Clean Architecture）

Robert C. Martin 提出的整洁架构，核心思想是**依赖规则**：源代码依赖只能指向内层，内层不知道外层的存在。

```
┌──────────────────────────────────────┐
│          框架与驱动（Frameworks）       │  Web框架、数据库、UI
│  ┌──────────────────────────────┐    │
│  │     接口适配器（Adapters）     │    │  Controller、Gateway、Presenter
│  │  ┌──────────────────────┐   │    │
│  │  │   用例（Use Cases）    │   │    │  应用业务规则
│  │  │  ┌──────────────┐   │   │    │
│  │  │  │ 实体（Entity） │   │   │    │  核心业务规则
│  │  │  └──────────────┘   │   │    │
│  │  └──────────────────────┘   │    │
│  └──────────────────────────────┘    │
└──────────────────────────────────────┘

依赖方向：外层 → 内层（永远不能反向）
```

**关键原则：**
- 实体层不依赖任何外部框架
- 用例层定义输入/输出端口（接口），由外层实现
- 数据库、Web框架等都是"细节"，可以随时替换

### 1.5 六边形架构（Hexagonal Architecture）

也叫端口与适配器架构（Ports and Adapters），由 Alistair Cockburn 提出。

```
          ┌─────────────────────────────┐
 HTTP ──→ │ Port                        │
          │   ┌─────────────────────┐   │ ──→ MySQL
 gRPC ──→ │   │                     │   │
          │   │   核心业务逻辑        │   │ ──→ Redis
 CLI  ──→ │   │   (Domain)          │   │
          │   │                     │   │ ──→ Kafka
 Test ──→ │   └─────────────────────┘   │
          │                        Port │ ──→ Mock
          └─────────────────────────────┘

左侧：驱动端口（Driving Ports）—— 外部如何调用系统
右侧：被驱动端口（Driven Ports）—— 系统如何调用外部
```

**核心思想：** 业务逻辑不依赖任何外部技术，通过端口（接口）与外部交互。适配器负责将外部技术适配到端口上。

---

## 二、RESTful API 设计

### 2.1 REST 核心原则

REST（Representational State Transfer）由 Roy Fielding 在 2000 年的博士论文中提出。

**六大约束：**
1. 客户端-服务器分离
2. 无状态：每个请求包含所有必要信息
3. 可缓存：响应必须标明是否可缓存
4. 统一接口：资源通过 URI 标识，通过表述操作资源
5. 分层系统：客户端不知道是否直接连接到服务器
6. 按需代码（可选）：服务器可以返回可执行代码

### 2.2 URL 设计规范

```
好的设计：
GET    /api/v1/users              获取用户列表
GET    /api/v1/users/123          获取单个用户
POST   /api/v1/users              创建用户
PUT    /api/v1/users/123          全量更新用户
PATCH  /api/v1/users/123          部分更新用户
DELETE /api/v1/users/123          删除用户
GET    /api/v1/users/123/orders   获取用户的订单列表

坏的设计：
GET    /api/getUser?id=123        动词不应出现在URL中
POST   /api/deleteUser            应该用DELETE方法
GET    /api/v1/user               单复数不一致
```

**URL 设计原则：**
- 使用名词复数表示资源集合
- 使用 HTTP 方法表示操作（GET/POST/PUT/PATCH/DELETE）
- 层级关系用路径表示（`/users/123/orders`）
- 过滤、排序、分页用查询参数（`?page=1&size=20&sort=created_at:desc`）
- 版本号放在 URL 路径中（`/api/v1/`）

### 2.3 HTTP 状态码

```
2xx 成功：
  200 OK              请求成功
  201 Created         资源创建成功
  204 No Content      删除成功，无返回体

3xx 重定向：
  301 Moved Permanently   永久重定向
  302 Found               临时重定向
  304 Not Modified        资源未修改（缓存有效）

4xx 客户端错误：
  400 Bad Request         请求参数错误
  401 Unauthorized        未认证
  403 Forbidden           无权限
  404 Not Found           资源不存在
  409 Conflict            资源冲突
  429 Too Many Requests   请求过于频繁

5xx 服务端错误：
  500 Internal Server Error   服务器内部错误
  502 Bad Gateway             网关错误
  503 Service Unavailable     服务不可用
  504 Gateway Timeout         网关超时
```

### 2.4 幂等性设计

幂等性是指同一个操作执行一次和执行多次的效果相同。

```
天然幂等的方法：
  GET    —— 读取操作，天然幂等
  PUT    —— 全量替换，天然幂等
  DELETE —— 删除操作，天然幂等

非天然幂等的方法：
  POST   —— 创建操作，多次调用会创建多条记录

实现 POST 幂等的方法：
  1. 客户端生成唯一请求ID（Idempotency-Key）
  2. 服务端用请求ID做去重检查
  3. 相同请求ID直接返回之前的结果
```

```python
# 幂等性实现示例
def create_order(idempotency_key: str, order_data: dict):
    # 检查是否已处理过
    existing = db.query(
        "SELECT * FROM idempotency_keys WHERE key = ?",
        idempotency_key
    )
    if existing:
        return existing.response  # 直接返回之前的结果

    # 执行业务逻辑
    order = OrderService.create(order_data)

    # 记录幂等键
    db.execute(
        "INSERT INTO idempotency_keys (key, response) VALUES (?, ?)",
        idempotency_key, serialize(order)
    )
    return order
```

### 2.5 分页设计

```
方式一：偏移量分页（Offset Pagination）
  GET /api/v1/users?page=2&size=20
  优点：简单直观
  缺点：深分页性能差（OFFSET 10000 需要扫描前10000条）

方式二：游标分页（Cursor Pagination）
  GET /api/v1/users?cursor=eyJpZCI6MTAwfQ&size=20
  优点：性能稳定，不受页深影响
  缺点：不能跳页，只能前后翻页
  适用：无限滚动、时间线（Twitter、微信朋友圈）

方式三：键集分页（Keyset Pagination）
  GET /api/v1/users?after_id=100&size=20
  SQL: SELECT * FROM users WHERE id > 100 ORDER BY id LIMIT 20
  优点：性能好，实现简单
  缺点：依赖排序字段的唯一性
```

### 2.6 错误响应格式

```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "请求参数校验失败",
        "details": [
            {
                "field": "email",
                "message": "邮箱格式不正确"
            },
            {
                "field": "age",
                "message": "年龄必须大于0"
            }
        ],
        "request_id": "req_abc123"
    }
}
```

**错误响应设计原则：**
- 使用业务错误码（不仅依赖 HTTP 状态码）
- 提供人类可读的错误消息
- 包含请求ID便于排查
- 字段级别的校验错误要具体到字段

---

## 三、认证与授权

### 3.1 认证方式对比

| 方式 | 原理 | 适用场景 |
|------|------|---------|
| Session | 服务端存储会话状态 | 传统Web应用 |
| JWT | 客户端持有签名令牌 | 无状态API、微服务 |
| OAuth 2.0 | 授权框架，委托第三方认证 | 第三方登录、开放平台 |
| API Key | 简单的密钥认证 | 服务间调用、开放API |

### 3.2 JWT 结构

```
Header.Payload.Signature

Header（头部）：
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload（载荷）：
{
  "sub": "user_123",
  "name": "Alice",
  "role": "admin",
  "iat": 1704067200,
  "exp": 1704153600
}

Signature（签名）：
HMACSHA256(base64(header) + "." + base64(payload), secret)
```

**JWT 的优缺点：**
- 优点：无状态、可跨域、自包含用户信息
- 缺点：无法主动失效（除非引入黑名单）、载荷不加密（只签名）、token 较大

### 3.3 OAuth 2.0 授权码流程

```
用户 → 客户端 → 授权服务器（获取授权码）
                    ↓
用户登录并授权 → 重定向回客户端（携带授权码）
                    ↓
客户端 → 授权服务器（用授权码换取 access_token）
                    ↓
客户端 → 资源服务器（携带 access_token 访问资源）
```

---

## 本章小结

分层架构和 API 设计是构建可维护系统的基础。关键要点：

1. 分层的本质是关注点分离，依赖方向必须单向
2. 整洁架构和六边形架构的核心是让业务逻辑不依赖外部技术
3. RESTful API 设计要遵循资源导向、正确使用 HTTP 方法和状态码
4. 幂等性是分布式系统中 API 设计的关键考量
5. 认证方案的选择取决于系统架构（单体 vs 微服务）和安全需求
