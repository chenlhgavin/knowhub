# 第二章 设计基础 — 练习题

涵盖课程：SOLID原则 · 设计模式 · 分层架构与API设计

---

## 基础题（第1-5题）

### 题目1 [基础] 识别SRP违反

以下 `OrderProcessor` 类违反了单一职责原则，请指出它承担了哪些不同职责，并将其重构为多个各司其职的类。

```python
class OrderProcessor:
    def __init__(self, db_connection):
        self.db = db_connection

    def process_order(self, order_data: dict):
        # 校验订单数据
        if not order_data.get("items"):
            raise ValueError("订单必须包含商品")
        if order_data["total"] <= 0:
            raise ValueError("订单金额必须大于0")

        # 计算折扣
        total = order_data["total"]
        if order_data.get("coupon") == "VIP20":
            total *= 0.8
        elif order_data.get("coupon") == "NEW10":
            total *= 0.9

        # 保存到数据库
        self.db.execute(
            "INSERT INTO orders (user_id, total) VALUES (?, ?)",
            order_data["user_id"], total
        )

        # 发送确认邮件
        import smtplib
        server = smtplib.SMTP("smtp.example.com")
        server.sendmail(
            "noreply@example.com",
            order_data["email"],
            f"您的订单已确认，金额: {total}"
        )

        # 记录日志
        with open("orders.log", "a") as f:
            f.write(f"订单已处理: user={order_data['user_id']}, total={total}\n")
```

---

### 题目2 [基础] 开闭原则重构

以下日志系统每次新增输出方式都需要修改 `Logger` 类。请用开闭原则重构，使其支持在不修改已有代码的前提下扩展新的日志输出方式。

```python
class Logger:
    def log(self, message: str, target: str):
        if target == "console":
            print(f"[LOG] {message}")
        elif target == "file":
            with open("app.log", "a") as f:
                f.write(f"{message}\n")
        elif target == "database":
            # 假设有数据库连接
            db.execute("INSERT INTO logs (message) VALUES (?)", message)
```

---

### 题目3 [基础] 识别设计模式

阅读以下三段代码描述，分别判断它们使用了哪种设计模式，并说明理由。

场景A：系统根据配置文件中的 `cache_type` 字段，创建 `RedisCache` 或 `MemcachedCache` 实例，调用方只依赖 `Cache` 接口。

场景B：一个 HTTP 请求依次经过 `AuthMiddleware`、`RateLimitMiddleware`、`LoggingMiddleware`，每个中间件决定是否将请求传递给下一个。

场景C：用户下单后，`OrderService` 发出 `order_created` 事件，`InventoryService`、`NotificationService`、`PointsService` 分别监听该事件并执行各自的逻辑。

---

### 题目4 [基础] RESTful API纠错

以下API设计存在多处不符合RESTful规范的问题，请逐一指出并给出修正后的设计。

```
1. GET    /api/getUserById?id=42
2. POST   /api/deleteProduct/99
3. GET    /api/v1/article              （获取文章列表）
4. POST   /api/v1/users/login
5. PUT    /api/v1/users/123/updateEmail
```

---

### 题目5 [基础] 单例模式线程安全

以下单例实现在多线程环境下存在问题，请说明问题所在，并给出线程安全的实现方案。

```python
class AppConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.settings = {}

    def load(self, path: str):
        import json
        with open(path) as f:
            self.settings = json.load(f)
```

---

## 进阶题（第6-10题）

### 题目6 [进阶] 策略模式实战

电商系统需要支持多种运费计算策略：

- 标准快递：首重12元/kg，续重5元/kg
- 顺丰速运：首重22元/kg，续重13元/kg
- 免费包邮：满99元免运费，否则统一8元

请用策略模式实现运费计算，要求：
1. 定义抽象策略接口
2. 实现三种具体策略
3. 提供一个上下文类，支持运行时切换策略
4. 编写调用示例

---

### 题目7 [进阶] 装饰器模式组合

为一个数据查询函数添加以下横切关注点，要求使用Python装饰器实现，且装饰器之间可以自由组合：

1. `@cache(ttl=60)` — 结果缓存，ttl秒内直接返回缓存
2. `@retry(max_retries=3, delay=1.0)` — 失败自动重试
3. `@timing` — 打印函数执行耗时

请实现这三个装饰器，并展示如何将它们组合应用到同一个函数上。

---

### 题目8 [进阶] 里氏替换原则判断

判断以下两组继承关系是否违反里氏替换原则，说明理由，并给出修正方案。

组A：
```python
class FileReader:
    def read(self, path: str) -> str:
        with open(path) as f:
            return f.read()

class EncryptedFileReader(FileReader):
    def read(self, path: str) -> str:
        if not path.endswith(".enc"):
            raise ValueError("只支持.enc加密文件")
        content = super().read(path)
        return self._decrypt(content)

    def _decrypt(self, content: str) -> str:
        return content  # 简化的解密逻辑
```

组B：
```python
class Collection:
    def __init__(self):
        self._items = []

    def add(self, item):
        self._items.append(item)

    def size(self) -> int:
        return len(self._items)

class UniqueCollection(Collection):
    def add(self, item):
        if item not in self._items:
            self._items.append(item)
```

---

### 题目9 [进阶] 幂等性API设计

设计一个创建支付订单的API，要求：

1. 给出完整的RESTful接口定义（URL、方法、请求体、响应体）
2. 实现幂等性保证（防止网络重试导致重复支付）
3. 正确使用HTTP状态码
4. 设计错误响应格式
5. 用Python伪代码实现核心逻辑

---

### 题目10 [进阶] 适配器与代理模式辨析

公司需要对接两个不同的短信服务商（阿里云SMS和腾讯云SMS），它们的SDK接口完全不同。同时需要在发送短信前增加频率限制和日志记录。

请回答：
1. 统一两个服务商的接口差异应该使用什么模式？
2. 增加频率限制和日志记录应该使用什么模式？
3. 画出整体的类关系结构（用文字描述即可）
4. 用Python代码实现完整方案

---

## 架构设计题（第11-15题）

### 题目11 [架构设计] 分层架构重构

以下代码将所有逻辑混在一个函数中，请将其重构为三层架构（表现层、业务层、数据访问层），并说明每层的职责边界。

```python
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.json

    # 参数校验
    if not data.get("username") or len(data["username"]) < 3:
        return jsonify({"error": "用户名至少3个字符"}), 400
    if not data.get("email") or "@" not in data["email"]:
        return jsonify({"error": "邮箱格式不正确"}), 400

    # 业务逻辑：检查用户名是否已存在
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (data["username"],))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "用户名已存在"}), 409

    # 密码加密
    import hashlib
    password_hash = hashlib.sha256(data["password"].encode()).hexdigest()

    # 保存到数据库
    cursor.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (data["username"], data["email"], password_hash)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    # 发送欢迎邮件
    import smtplib
    server = smtplib.SMTP("smtp.example.com")
    server.sendmail("noreply@example.com", data["email"], "欢迎注册！")

    return jsonify({"id": user_id, "username": data["username"]}), 201
```

---

### 题目12 [架构设计] 六边形架构设计

为一个"图书借阅系统"设计六边形架构，要求：

1. 识别核心业务逻辑（领域层）
2. 定义驱动端口（Driving Ports）：哪些外部系统会调用本系统
3. 定义被驱动端口（Driven Ports）：本系统需要调用哪些外部系统
4. 为每个端口设计适配器
5. 用Python代码实现核心领域层和端口定义（接口），无需实现具体适配器

业务规则：
- 每位读者最多同时借阅5本书
- 借阅期限为30天，超期每天罚款0.5元
- 热门图书（借阅次数>100）不可续借

---

### 题目13 [架构设计] CQRS模式应用

一个电商商品系统面临以下挑战：
- 写入端：商家频繁更新商品信息（价格、库存、描述），数据存储在MySQL中，采用范式化设计
- 读取端：用户浏览商品需要聚合多张表的数据（商品基本信息+价格+库存+评价统计+店铺信息），查询量是写入量的100倍

请设计CQRS方案：
1. 画出读写分离的架构图（文字描述）
2. 写路径的数据模型设计
3. 读路径的数据模型设计（反范式化）
4. 读写模型之间的数据同步方案
5. 用Python伪代码实现Command Handler和Query Handler

---

### 题目14 [架构设计] 认证方案选型

为以下三个不同场景分别选择最合适的认证方案，并说明理由：

场景A：一个面向内部员工的单体Web管理后台，用户量约500人，需要支持"记住我"功能。

场景B：一个微服务架构的SaaS平台，包含用户服务、订单服务、支付服务等10+个微服务，需要支持移动端和Web端。

场景C：一个开放平台，允许第三方开发者调用API获取用户授权数据（类似微信开放平台）。

对于每个场景，请回答：
1. 推荐的认证方案（Session/JWT/OAuth 2.0/API Key）
2. 选择理由（至少3点）
3. 需要注意的安全风险及应对措施
4. 给出认证流程的时序描述

---

### 题目15 [架构设计] 综合设计：在线教育平台API

为一个在线教育平台设计API体系，平台包含以下核心功能：
- 课程管理（CRUD、分类、搜索）
- 用户报名（报名、取消、查看已报名课程）
- 学习进度（记录视频观看进度、完成章节标记）
- 评价系统（评分、评论、回复）

要求：
1. 设计完整的RESTful API列表（至少15个端点），包含URL、HTTP方法、简要说明
2. 设计分页、过滤、排序的查询参数规范
3. 设计统一的成功响应和错误响应格式
4. 选择合适的认证方案并说明理由
5. 识别哪些API需要幂等性保证，并说明实现方式
6. 指出该系统中可以应用的至少3种设计模式，说明应用位置和理由
