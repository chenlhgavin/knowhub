# 常用设计模式

## 概述

设计模式是前人在大量实践中总结出的可复用解决方案。本章聚焦于架构设计中最常用的几种模式，不追求面面俱到，而是深入理解每种模式的本质和适用场景。

---

## 一、创建型模式

### 1.1 工厂方法模式（Factory Method）

工厂方法的核心思想是将对象的创建延迟到子类，让子类决定实例化哪个类。

**问题场景：** 系统需要根据不同条件创建不同类型的对象，但调用方不应该关心具体的创建逻辑。

```python
from abc import ABC, abstractmethod


class Notification(ABC):
    @abstractmethod
    def send(self, message: str):
        pass


class EmailNotification(Notification):
    def send(self, message: str):
        print(f"发送邮件: {message}")


class SmsNotification(Notification):
    def send(self, message: str):
        print(f"发送短信: {message}")


class PushNotification(Notification):
    def send(self, message: str):
        print(f"发送推送: {message}")


class NotificationFactory:
    _creators = {
        "email": EmailNotification,
        "sms": SmsNotification,
        "push": PushNotification,
    }

    @classmethod
    def create(cls, channel: str) -> Notification:
        creator = cls._creators.get(channel)
        if not creator:
            raise ValueError(f"不支持的通知渠道: {channel}")
        return creator()


# 使用：调用方不关心具体实现
notification = NotificationFactory.create("email")
notification.send("你的订单已发货")
```

**在架构中的应用：**
- 数据库驱动的动态创建（根据配置选择 MySQL/PostgreSQL）
- 消息队列客户端的创建（根据环境选择 Kafka/RabbitMQ）
- 日志处理器的创建（根据级别选择不同的输出方式）

### 1.2 单例模式（Singleton）

确保一个类只有一个实例，并提供全局访问点。

```python
class ConnectionPool:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, max_connections: int = 10):
        if self._initialized:
            return
        self._initialized = True
        self.max_connections = max_connections
        self._connections = []
        print(f"初始化连接池，最大连接数: {max_connections}")

    def get_connection(self):
        return f"connection_{len(self._connections)}"


# 两次创建得到同一个实例
pool1 = ConnectionPool(10)
pool2 = ConnectionPool(20)
print(pool1 is pool2)  # True
```

**注意事项：**
- 单例在多线程环境下需要加锁保护
- 单例使得单元测试困难（全局状态难以隔离）
- 现代框架通常用依赖注入容器管理单例生命周期，而非手写单例

---

## 二、结构型模式

### 2.1 代理模式（Proxy）

为另一个对象提供一个替身或占位符，以控制对这个对象的访问。

```python
from abc import ABC, abstractmethod
import time


class DataService(ABC):
    @abstractmethod
    def query(self, sql: str) -> list:
        pass


class MySQLService(DataService):
    def query(self, sql: str) -> list:
        time.sleep(0.1)  # 模拟数据库查询
        return [{"id": 1, "name": "Alice"}]


class CachingProxy(DataService):
    """缓存代理：在真实服务前增加缓存层"""
    def __init__(self, real_service: DataService):
        self._real_service = real_service
        self._cache = {}

    def query(self, sql: str) -> list:
        if sql in self._cache:
            print(f"缓存命中: {sql}")
            return self._cache[sql]
        print(f"缓存未命中，查询数据库: {sql}")
        result = self._real_service.query(sql)
        self._cache[sql] = result
        return result


class LoggingProxy(DataService):
    """日志代理：记录每次查询"""
    def __init__(self, real_service: DataService):
        self._real_service = real_service

    def query(self, sql: str) -> list:
        start = time.time()
        result = self._real_service.query(sql)
        elapsed = time.time() - start
        print(f"[LOG] SQL: {sql}, 耗时: {elapsed:.3f}s, 结果数: {len(result)}")
        return result


# 代理可以嵌套组合
service = CachingProxy(LoggingProxy(MySQLService()))
service.query("SELECT * FROM users")  # 缓存未命中 → 日志 → 数据库
service.query("SELECT * FROM users")  # 缓存命中
```

**在架构中的应用：**
- Nginx 反向代理
- RPC 框架的客户端代理（Dubbo、gRPC）
- ORM 的延迟加载代理
- API 网关（认证、限流、日志）

### 2.2 装饰器模式（Decorator）

动态地给对象添加额外的职责，比继承更灵活。

```python
from abc import ABC, abstractmethod
from functools import wraps
import time


# Python 中装饰器模式最自然的表达就是函数装饰器
def retry(max_retries: int = 3, delay: float = 1.0):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"第{attempt + 1}次失败: {e}, {delay}秒后重试")
                    time.sleep(delay)
        return wrapper
    return decorator


def timing(func):
    """计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时: {time.time() - start:.3f}s")
        return result
    return wrapper


@retry(max_retries=3, delay=0.5)
@timing
def call_external_api(url: str):
    print(f"请求 {url}")
    # 模拟偶尔失败
    import random
    if random.random() < 0.5:
        raise ConnectionError("连接超时")
    return {"status": "ok"}
```

**在架构中的应用：**
- Java I/O 流（BufferedInputStream 装饰 FileInputStream）
- 中间件链（Gin/Express 的中间件就是装饰器思想）
- 限流、熔断、日志等横切关注点

### 2.3 适配器模式（Adapter）

将一个类的接口转换为客户端期望的另一个接口。

```python
# 旧系统的支付接口
class LegacyPaymentSystem:
    def make_payment(self, amount_in_cents: int, currency_code: str) -> dict:
        return {"success": True, "transaction_id": "TXN_001"}


# 新系统期望的接口
class PaymentGateway(ABC):
    @abstractmethod
    def pay(self, amount: float, currency: str) -> str:
        pass


# 适配器：让旧系统适配新接口
class LegacyPaymentAdapter(PaymentGateway):
    def __init__(self, legacy_system: LegacyPaymentSystem):
        self._legacy = legacy_system

    def pay(self, amount: float, currency: str) -> str:
        amount_in_cents = int(amount * 100)
        result = self._legacy.make_payment(amount_in_cents, currency)
        if result["success"]:
            return result["transaction_id"]
        raise PaymentError("支付失败")


# 使用：新代码只依赖 PaymentGateway 接口
gateway: PaymentGateway = LegacyPaymentAdapter(LegacyPaymentSystem())
txn_id = gateway.pay(99.99, "CNY")
```

**在架构中的应用：**
- 对接第三方 SDK（统一不同支付渠道的接口）
- 数据格式转换（XML ↔ JSON）
- 新旧系统迁移的过渡层

---

## 三、行为型模式

### 3.1 策略模式（Strategy）

定义一系列算法，将每个算法封装起来，使它们可以互相替换。

```python
from abc import ABC, abstractmethod
from typing import List


class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: List[int]) -> List[int]:
        pass


class QuickSort(SortStrategy):
    def sort(self, data: List[int]) -> List[int]:
        if len(data) <= 1:
            return data
        pivot = data[0]
        left = [x for x in data[1:] if x <= pivot]
        right = [x for x in data[1:] if x > pivot]
        return self.sort(left) + [pivot] + self.sort(right)


class MergeSort(SortStrategy):
    def sort(self, data: List[int]) -> List[int]:
        if len(data) <= 1:
            return data
        mid = len(data) // 2
        left = self.sort(data[:mid])
        right = self.sort(data[mid:])
        return self._merge(left, right)

    def _merge(self, left, right):
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result


class Sorter:
    def __init__(self, strategy: SortStrategy):
        self._strategy = strategy

    def sort(self, data: List[int]) -> List[int]:
        return self._strategy.sort(data)


# 运行时切换策略
data = [5, 2, 8, 1, 9]
sorter = Sorter(QuickSort())
print(sorter.sort(data))

sorter = Sorter(MergeSort())
print(sorter.sort(data))
```

**在架构中的应用：**
- 负载均衡策略（轮询、随机、最少连接、一致性哈希）
- 限流策略（固定窗口、滑动窗口、令牌桶、漏桶）
- 序列化策略（JSON、Protobuf、MessagePack）

### 3.2 观察者模式（Observer）

定义对象间的一对多依赖关系，当一个对象状态改变时，所有依赖它的对象都会收到通知。

```python
from abc import ABC, abstractmethod
from typing import List


class EventListener(ABC):
    @abstractmethod
    def on_event(self, event_type: str, data: dict):
        pass


class EventBus:
    def __init__(self):
        self._listeners: dict[str, List[EventListener]] = {}

    def subscribe(self, event_type: str, listener: EventListener):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    def publish(self, event_type: str, data: dict):
        for listener in self._listeners.get(event_type, []):
            listener.on_event(event_type, data)


class OrderLogger(EventListener):
    def on_event(self, event_type: str, data: dict):
        print(f"[日志] 事件: {event_type}, 数据: {data}")


class InventoryService(EventListener):
    def on_event(self, event_type: str, data: dict):
        if event_type == "order_created":
            print(f"[库存] 扣减商品 {data['product_id']} 库存 {data['quantity']}")


class NotificationService(EventListener):
    def on_event(self, event_type: str, data: dict):
        if event_type == "order_created":
            print(f"[通知] 发送订单确认给用户 {data['user_id']}")


# 使用
bus = EventBus()
bus.subscribe("order_created", OrderLogger())
bus.subscribe("order_created", InventoryService())
bus.subscribe("order_created", NotificationService())

bus.publish("order_created", {
    "order_id": "ORD_001",
    "user_id": "U_100",
    "product_id": "P_200",
    "quantity": 2
})
```

**在架构中的应用：**
- 事件驱动架构（Event-Driven Architecture）
- 消息队列的发布/订阅模式
- React/Vue 的响应式数据绑定
- Webhook 回调机制

### 3.3 责任链模式（Chain of Responsibility）

将请求沿着处理者链传递，每个处理者决定是否处理请求或传递给下一个处理者。

```python
from abc import ABC, abstractmethod


class Handler(ABC):
    def __init__(self):
        self._next: Handler = None

    def set_next(self, handler: 'Handler') -> 'Handler':
        self._next = handler
        return handler

    def handle(self, request: dict) -> dict:
        if self._next:
            return self._next.handle(request)
        return request


class AuthHandler(Handler):
    def handle(self, request: dict) -> dict:
        token = request.get("token")
        if not token:
            return {"error": "未认证", "code": 401}
        if token != "valid_token":
            return {"error": "token无效", "code": 403}
        request["user_id"] = "U_100"
        print("[认证] 通过")
        return super().handle(request)


class RateLimitHandler(Handler):
    def __init__(self):
        super().__init__()
        self._request_count = {}

    def handle(self, request: dict) -> dict:
        user_id = request.get("user_id", "anonymous")
        count = self._request_count.get(user_id, 0)
        if count >= 100:
            return {"error": "请求过于频繁", "code": 429}
        self._request_count[user_id] = count + 1
        print(f"[限流] 用户 {user_id} 请求次数: {count + 1}")
        return super().handle(request)


class BusinessHandler(Handler):
    def handle(self, request: dict) -> dict:
        print(f"[业务] 处理请求: {request.get('action')}")
        return {"result": "success", "code": 200}


# 构建责任链
auth = AuthHandler()
rate_limit = RateLimitHandler()
business = BusinessHandler()

auth.set_next(rate_limit).set_next(business)

# 请求沿链传递
result = auth.handle({"token": "valid_token", "action": "get_user"})
print(result)
```

**在架构中的应用：**
- Web 框架的中间件链（Django Middleware、Gin Middleware）
- Netty 的 ChannelPipeline
- 审批流程引擎
- 日志过滤器链

---

## 四、架构级模式

### 4.1 发布-订阅模式（Pub/Sub）

观察者模式的分布式版本，通过消息中间件解耦发布者和订阅者。

```
发布者 ──→ [消息中间件(Kafka/RabbitMQ)] ──→ 订阅者A
                                          ──→ 订阅者B
                                          ──→ 订阅者C

与观察者模式的区别：
- 观察者模式：发布者直接持有订阅者引用，同步调用
- 发布-订阅：通过中间件解耦，异步通信，可跨进程/跨机器
```

### 4.2 CQRS（命令查询职责分离）

将系统的读操作和写操作分离为不同的模型。

```
写路径（Command）：
  客户端 → API → Command Handler → 写数据库（MySQL主库）
                                        ↓ 同步/异步
读路径（Query）：                    读数据库（MySQL从库/ES/Redis）
  客户端 → API → Query Handler → 读数据库

适用场景：
- 读写比例悬殊（读远大于写）
- 读写模型差异大（写入是范式化的，查询需要反范式化）
- 需要独立扩展读写能力
```

### 4.3 Sidecar 模式

将辅助功能（日志、监控、服务发现、安全）部署为独立的进程，与主应用进程并行运行。

```
┌─────────────────────────────┐
│          Pod / VM           │
│                             │
│  ┌──────────┐ ┌──────────┐ │
│  │ 主应用    │ │ Sidecar  │ │
│  │ (业务)   │←→│ (Envoy)  │ │
│  └──────────┘ └──────────┘ │
│                             │
└─────────────────────────────┘

Sidecar 负责：
- 服务发现与负载均衡
- 流量管理（限流、熔断、重试）
- 安全（mTLS、认证）
- 可观测性（指标、日志、追踪）

代表实现：Istio + Envoy（Service Mesh）
```

---

## 五、模式选择原则

1. **不要为了用模式而用模式**：先写最简单的代码，当发现重复或变化点时再引入模式
2. **优先组合而非继承**：策略模式、装饰器模式都是组合优于继承的体现
3. **识别变化点**：模式的本质是封装变化，找到系统中最可能变化的部分
4. **考虑团队认知**：选择团队成员都能理解的模式，过于复杂的模式反而增加维护成本
5. **模式可以组合**：实际系统中往往是多种模式的组合使用
