# 第二章 设计基础 - 习题答案

（注：习题见 `../exercises/exercises.md`）

## 一、选择题答案

根据第二章习题内容提供答案。以下基于课程内容给出参考答案。

### 1. 关于单一职责原则（SRP）
**答案：B** — 一个类应该只有一个引起它变化的原因。SRP的核心不是"只做一件事"，而是"只有一个变化的原因"，即只对一个角色负责。

### 2. 关于开闭原则（OCP）
**答案：A** — 对扩展开放，对修改关闭。通过抽象和多态实现，新增功能时添加新类而非修改已有代码。

### 3. 关于依赖倒置原则（DIP）
**答案：C** — 高层模块不应该依赖低层模块，两者都应该依赖抽象。这是DIP的核心定义。

### 4. 关于工厂模式
**答案：B** — 工厂模式将对象的创建逻辑封装起来，调用方不需要知道具体创建哪个类的实例。

### 5. 关于整洁架构
**答案：D** — 依赖方向必须从外层指向内层，内层不知道外层的存在。实体层不依赖任何外部框架。

---

## 二、简答题答案

### 6. 里氏替换原则（LSP）

里氏替换原则要求：子类对象必须能够替换父类对象，且程序的行为不会发生变化。

**经典反例——正方形继承矩形：**

```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def set_width(self, w):
        self.width = w

    def set_height(self, h):
        self.height = h

    def area(self):
        return self.width * self.height

class Square(Rectangle):
    def set_width(self, w):
        self.width = w
        self.height = w  # 正方形宽高必须相等

    def set_height(self, h):
        self.width = h
        self.height = h
```

问题：当使用 `Rectangle` 类型的变量引用 `Square` 对象时：
```python
def test_area(rect: Rectangle):
    rect.set_width(5)
    rect.set_height(4)
    assert rect.area() == 20  # 对Rectangle成立，对Square失败（结果是16）
```

正方形替换矩形后行为发生了变化，违反了LSP。正确做法是不让Square继承Rectangle，而是让它们都实现一个Shape接口。

### 7. 策略模式 vs 模板方法模式

| 特性 | 策略模式 | 模板方法模式 |
|------|---------|-------------|
| 实现方式 | 组合（持有策略对象） | 继承（子类重写方法） |
| 变化点 | 整个算法可替换 | 算法的某些步骤可替换 |
| 运行时切换 | 支持 | 不支持（编译时确定） |
| 耦合度 | 低（通过接口解耦） | 高（子类依赖父类） |

策略模式适合算法整体可替换的场景（如不同的排序算法、不同的支付方式）。模板方法适合算法骨架固定、部分步骤可变的场景（如数据处理流程中的解析步骤不同）。

### 8. 六边形架构

六边形架构（端口与适配器架构）的核心思想是将业务逻辑放在中心，通过端口（接口）与外部交互，适配器负责将外部技术适配到端口上。

**与传统分层架构的区别：**
- 分层架构：依赖方向自上而下（表现层→业务层→数据层），业务层依赖数据层
- 六边形架构：业务逻辑不依赖任何外部技术，数据库、Web框架都是外部适配器

**优势：**
- 业务逻辑完全独立，可以脱离框架测试
- 更换数据库或Web框架只需更换适配器
- 驱动端口（左侧）和被驱动端口（右侧）的对称设计

---

## 三、设计题答案

### 9. 通知系统设计（策略模式 + 工厂模式）

```python
from abc import ABC, abstractmethod

# 策略接口
class NotificationStrategy(ABC):
    @abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        pass

# 具体策略
class EmailStrategy(NotificationStrategy):
    def send(self, recipient: str, message: str) -> bool:
        print(f"发送邮件到 {recipient}: {message}")
        return True

class SmsStrategy(NotificationStrategy):
    def send(self, recipient: str, message: str) -> bool:
        print(f"发送短信到 {recipient}: {message}")
        return True

class PushStrategy(NotificationStrategy):
    def send(self, recipient: str, message: str) -> bool:
        print(f"发送推送到 {recipient}: {message}")
        return True

# 工厂
class NotificationFactory:
    _strategies = {
        "email": EmailStrategy,
        "sms": SmsStrategy,
        "push": PushStrategy,
    }

    @classmethod
    def create(cls, channel: str) -> NotificationStrategy:
        strategy_cls = cls._strategies.get(channel)
        if not strategy_cls:
            raise ValueError(f"不支持的渠道: {channel}")
        return strategy_cls()

# 通知服务（支持多渠道、优先级、降级）
class NotificationService:
    def __init__(self, channels: list[str]):
        self.strategies = [NotificationFactory.create(ch) for ch in channels]

    def notify(self, recipient: str, message: str) -> bool:
        for strategy in self.strategies:
            try:
                if strategy.send(recipient, message):
                    return True
            except Exception:
                continue  # 当前渠道失败，尝试下一个（降级）
        return False

# 使用
service = NotificationService(["push", "sms", "email"])
service.notify("user_123", "您的订单已发货")
```

### 10. RESTful API设计

```
# 图书管理系统API设计

## 图书资源
GET    /api/v1/books                    获取图书列表
GET    /api/v1/books?category=tech&page=1&size=20&sort=created_at:desc
GET    /api/v1/books/{id}               获取单本图书详情
POST   /api/v1/books                    创建图书
PUT    /api/v1/books/{id}               全量更新图书
PATCH  /api/v1/books/{id}               部分更新图书
DELETE /api/v1/books/{id}               删除图书

## 借阅资源
GET    /api/v1/books/{id}/borrows       获取图书的借阅记录
POST   /api/v1/borrows                  创建借阅记录（借书）
PATCH  /api/v1/borrows/{id}/return      归还图书
GET    /api/v1/users/{id}/borrows       获取用户的借阅记录

## 响应格式
成功响应：
{
    "data": { "id": 1, "title": "设计模式", ... },
    "meta": { "page": 1, "size": 20, "total": 100 }
}

错误响应：
{
    "error": {
        "code": "BOOK_NOT_FOUND",
        "message": "图书不存在",
        "request_id": "req_abc123"
    }
}

## 幂等性设计
POST /api/v1/borrows
Header: Idempotency-Key: borrow_user1_book1_20240115
Body: { "user_id": 1, "book_id": 1 }
服务端根据Idempotency-Key去重，避免重复借阅
```
