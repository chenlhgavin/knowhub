# 领域驱动设计（Domain-Driven Design）

## 概述

领域驱动设计（DDD）是 Eric Evans 在 2003 年提出的一套软件设计方法论。它的核心思想是：软件的复杂性不在于技术本身，而在于业务领域。DDD 通过将业务领域知识融入代码设计，让软件模型与业务模型保持一致，从而降低系统的认知复杂度。

### 为什么需要 DDD

传统开发模式的典型问题：

- 开发人员按数据库表结构写代码，业务逻辑散落在 Service 层的各种方法中
- 产品经理说"订单"，开发人员想的是 `order` 表的 CRUD
- 业务规则被 `if-else` 淹没，新人接手时完全无法理解业务含义
- 系统越做越大，模块边界模糊，改一处牵动全身

DDD 解决的核心问题：**让代码说业务的语言，让架构反映业务的边界。**

### 战略设计 vs 战术设计

DDD 分为两个层次：

| 层次 | 关注点 | 核心概念 |
|------|--------|----------|
| 战略设计 | 系统如何拆分，团队如何协作 | 限界上下文、上下文映射、通用语言 |
| 战术设计 | 单个上下文内部如何建模 | 实体、值对象、聚合、领域服务、领域事件、仓储 |

> 战略设计决定做对的事，战术设计决定把事做对。很多团队只学了战术设计的"术语"，却忽略了战略设计，这是 DDD 落地失败的首要原因。

---

## 一、战略设计

### 1.1 限界上下文（Bounded Context）

限界上下文是 DDD 中最重要的概念。它定义了一个模型的适用边界——在这个边界内，每个术语都有明确且唯一的含义。

**为什么需要限界上下文？**

同一个词在不同业务场景下含义不同。以"商品"为例：

```
商品目录上下文：商品 = 名称 + 描述 + 图片 + 分类
库存上下文：    商品 = SKU + 库存数量 + 仓库位置
订单上下文：    商品 = 商品快照 + 购买数量 + 成交价格
物流上下文：    商品 = 包裹项 + 重量 + 体积
```

如果把这些含义塞进一个 `Product` 类，这个类会变成一个无所不包的"上帝对象"。限界上下文的作用就是划清边界，让每个上下文内的模型保持简洁和一致。

**划分方法：**

1. 按业务能力划分：每个上下文对应一个独立的业务能力
2. 按团队结构划分：康威定律——系统结构反映组织结构
3. 按语言边界划分：当同一个词在不同场景下含义不同时，就是边界

**电商系统的限界上下文划分：**

```
┌─────────────────────────────────────────────────┐
│                   电商系统                        │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ 商品目录  │  │ 订单管理  │  │ 库存管理  │      │
│  │ Context  │  │ Context  │  │ Context  │      │
│  │          │  │          │  │          │      │
│  │ ·商品    │  │ ·订单    │  │ ·库存项  │      │
│  │ ·分类    │  │ ·订单项  │  │ ·仓库    │      │
│  │ ·品牌    │  │ ·收货地址│  │ ·调拨单  │      │
│  └──────────┘  └──────────┘  └──────────┘      │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ 支付结算  │  │ 用户账户  │  │ 物流配送  │      │
│  │ Context  │  │ Context  │  │ Context  │      │
│  │          │  │          │  │          │      │
│  │ ·支付单  │  │ ·用户    │  │ ·运单    │      │
│  │ ·退款单  │  │ ·地址簿  │  │ ·包裹    │      │
│  │ ·对账记录│  │ ·会员等级│  │ ·轨迹    │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
```

### 1.2 上下文映射（Context Map）

不同的限界上下文之间需要协作，上下文映射描述了它们之间的关系。

**常见的映射关系：**

| 关系类型 | 说明 | 典型场景 |
|----------|------|----------|
| 合作关系（Partnership） | 两个团队共同演进，同步发布 | 订单和库存紧密协作 |
| 客户-供应商（Customer-Supplier） | 上游提供服务，下游消费 | 商品目录(上游) → 订单(下游) |
| 防腐层（Anti-Corruption Layer） | 下游通过转换层隔离上游模型 | 对接第三方支付 |
| 开放主机服务（Open Host Service） | 上游提供标准化协议供多方消费 | 用户服务提供统一 API |
| 共享内核（Shared Kernel） | 两个上下文共享一小部分模型 | 共享基础的 Money 类型 |
| 各行其道（Separate Ways） | 两个上下文完全独立，不集成 | 内部工具与核心业务 |

**上下文映射图示例：**

```
┌──────────┐   开放主机服务    ┌──────────┐
│ 用户账户  │ ──────────────→ │ 订单管理  │
│          │   (REST API)    │          │
└──────────┘                  └────┬─────┘
                                   │
                              客户-供应商
                                   │
┌──────────┐    防腐层        ┌────▼─────┐
│ 第三方支付 │ ◄─────────────  │ 支付结算  │
│ (支付宝)  │  ACL 转换隔离   │          │
└──────────┘                  └──────────┘
                                   │
                               合作关系
                                   │
                              ┌────▼─────┐
                              │ 库存管理  │
                              └──────────┘
```

**防腐层（ACL）代码示例：**

```python
from dataclasses import dataclass
from abc import ABC, abstractmethod


# === 第三方支付的模型（外部，我们无法控制）===
class AlipayResponse:
    """支付宝返回的数据结构"""
    def __init__(self, trade_no: str, status: str, amount_cents: int):
        self.trade_no = trade_no
        self.status = status          # "TRADE_SUCCESS" | "TRADE_CLOSED"
        self.amount_cents = amount_cents


# === 我们领域内的模型 ===
@dataclass
class PaymentResult:
    """支付结算上下文内部的支付结果"""
    transaction_id: str
    success: bool
    amount: float


# === 防腐层：隔离外部模型对内部的污染 ===
class PaymentGateway(ABC):
    @abstractmethod
    def pay(self, order_id: str, amount: float) -> PaymentResult:
        pass


class AlipayAdapter(PaymentGateway):
    """防腐层实现：将支付宝的模型转换为内部模型"""

    def __init__(self, alipay_client):
        self._client = alipay_client

    def pay(self, order_id: str, amount: float) -> PaymentResult:
        # 调用支付宝 SDK（外部模型）
        response: AlipayResponse = self._client.create_trade(
            out_trade_no=order_id,
            total_amount=int(amount * 100)
        )
        # 转换为内部模型（防腐层的核心职责）
        return PaymentResult(
            transaction_id=response.trade_no,
            success=response.status == "TRADE_SUCCESS",
            amount=response.amount_cents / 100.0,
        )
```

### 1.3 通用语言（Ubiquitous Language）

通用语言是指在一个限界上下文内，开发团队和业务专家共同使用的一套术语。这套术语必须在代码、文档、日常沟通中保持一致。

**反面案例：**
- 产品经理说"下单"，代码里叫 `createOrder`，数据库字段叫 `insert_record`
- 业务说"优惠券核销"，代码里叫 `updateCouponStatus`

**正面做法：**
- 业务说"提交订单"，代码里就是 `order.submit()`
- 业务说"取消订单"，代码里就是 `order.cancel()`
- 业务说"申请退款"，代码里就是 `order.request_refund()`

通用语言不是文档，而是活在代码中的业务词汇表。

---

## 二、战术设计

### 2.1 实体（Entity）vs 值对象（Value Object）

**实体：** 有唯一标识，生命周期内标识不变，即使属性完全相同也是不同的对象。

**值对象：** 没有唯一标识，通过属性值来判断相等性，不可变。

```python
from dataclasses import dataclass, field
from typing import Optional
import uuid


# === 值对象：通过属性判断相等，不可变 ===
@dataclass(frozen=True)
class Money:
    """金额值对象"""
    amount: float
    currency: str = "CNY"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("金额不能为负数")

    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("币种不同，无法相加")
        return Money(self.amount + other.amount, self.currency)

    def multiply(self, factor: float) -> 'Money':
        return Money(round(self.amount * factor, 2), self.currency)


@dataclass(frozen=True)
class Address:
    """地址值对象"""
    province: str
    city: str
    district: str
    street: str
    zip_code: str


# === 实体：有唯一标识 ===
class Order:
    """订单实体"""
    def __init__(self, order_id: str, customer_id: str):
        self.order_id = order_id        # 唯一标识
        self.customer_id = customer_id
        self.items: list = []
        self.status: str = "CREATED"

    def __eq__(self, other):
        """实体通过 ID 判断相等"""
        if not isinstance(other, Order):
            return False
        return self.order_id == other.order_id

    def __hash__(self):
        return hash(self.order_id)


# 两个 Money(100, "CNY") 是相等的（值对象）
m1 = Money(100, "CNY")
m2 = Money(100, "CNY")
print(m1 == m2)  # True

# 两个 Order 即使属性相同，ID 不同就不相等（实体）
o1 = Order("ORD-001", "C-100")
o2 = Order("ORD-002", "C-100")
print(o1 == o2)  # False
```

### 2.2 聚合（Aggregate）与聚合根（Aggregate Root）

聚合是一组相关对象的集合，作为数据修改的基本单元。外部只能通过聚合根来访问聚合内部的对象。

```
聚合的规则：
  1. 每个聚合有且仅有一个聚合根
  2. 外部对象只能引用聚合根，不能直接引用内部对象
  3. 聚合内部保证业务规则的一致性（事务边界）
  4. 聚合之间通过 ID 引用，而非对象引用

┌─────────────────────────────────┐
│         Order 聚合               │
│  ┌───────────────────────────┐  │
│  │ Order（聚合根）             │  │
│  │  - order_id               │  │
│  │  - status                 │  │
│  │  - submit()               │  │
│  │  - add_item()             │  │
│  └─────────┬─────────────────┘  │
│            │ 包含                │
│  ┌─────────▼─────────────────┐  │
│  │ OrderItem（内部实体）       │  │
│  │  - product_id             │  │
│  │  - quantity               │  │
│  │  - price                  │  │
│  └───────────────────────────┘  │
│                                  │
│  ┌───────────────────────────┐  │
│  │ ShippingAddress（值对象）   │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

### 2.3 领域服务（Domain Service）

当一个业务操作不自然地属于任何一个实体或值对象时，使用领域服务。

```python
class PricingService:
    """定价领域服务：跨多个对象的业务逻辑"""

    def calculate_order_total(
        self, items: list, member_level: str
    ) -> 'Money':
        subtotal = Money(0)
        for item in items:
            subtotal = subtotal.add(item.price.multiply(item.quantity))

        # 会员折扣规则
        discount_map = {"GOLD": 0.9, "SILVER": 0.95, "NORMAL": 1.0}
        discount = discount_map.get(member_level, 1.0)

        return subtotal.multiply(discount)
```

### 2.4 领域事件（Domain Event）

领域事件表示领域中发生的有业务意义的事情。它是过去时态的，不可变的。

```python
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass(frozen=True)
class DomainEvent:
    """领域事件基类"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class OrderSubmitted(DomainEvent):
    """订单已提交事件"""
    order_id: str = ""
    customer_id: str = ""
    total_amount: float = 0.0


@dataclass(frozen=True)
class OrderCancelled(DomainEvent):
    """订单已取消事件"""
    order_id: str = ""
    reason: str = ""
```

### 2.5 仓储（Repository）

仓储为聚合提供持久化的抽象，让领域层不依赖具体的存储技术。

```python
from abc import ABC, abstractmethod
from typing import Optional


class OrderRepository(ABC):
    """订单仓储接口（定义在领域层）"""

    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional['Order']:
        pass

    @abstractmethod
    def save(self, order: 'Order') -> None:
        pass

    @abstractmethod
    def next_id(self) -> str:
        pass


class MySQLOrderRepository(OrderRepository):
    """MySQL 实现（定义在基础设施层）"""

    def __init__(self, db_session):
        self._session = db_session

    def find_by_id(self, order_id: str) -> Optional['Order']:
        row = self._session.execute(
            "SELECT * FROM orders WHERE order_id = %s", (order_id,)
        )
        if not row:
            return None
        return self._to_entity(row)

    def save(self, order: 'Order') -> None:
        self._session.execute(
            "INSERT INTO orders (...) VALUES (...) ON DUPLICATE KEY UPDATE ...",
            self._to_row(order),
        )

    def next_id(self) -> str:
        return f"ORD-{uuid.uuid4().hex[:12].upper()}"

    def _to_entity(self, row) -> 'Order':
        """数据行 → 领域对象"""
        ...

    def _to_row(self, order: 'Order') -> dict:
        """领域对象 → 数据行"""
        ...
```

---

## 三、DDD 实战：电商订单领域建模

下面用一个完整的 Python 示例展示订单限界上下文的领域模型。

```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
from abc import ABC, abstractmethod
import uuid


# ============================================================
# 值对象
# ============================================================

@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "CNY"

    def add(self, other: Money) -> Money:
        assert self.currency == other.currency
        return Money(round(self.amount + other.amount, 2), self.currency)

    def multiply(self, factor: float) -> Money:
        return Money(round(self.amount * factor, 2), self.currency)

    def __ge__(self, other: Money) -> bool:
        return self.amount >= other.amount


@dataclass(frozen=True)
class ShippingAddress:
    receiver: str
    phone: str
    province: str
    city: str
    detail: str


# ============================================================
# 领域事件
# ============================================================

@dataclass(frozen=True)
class DomainEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class OrderSubmitted(DomainEvent):
    order_id: str = ""
    customer_id: str = ""
    total_amount: float = 0.0


@dataclass(frozen=True)
class OrderCancelled(DomainEvent):
    order_id: str = ""
    reason: str = ""


# ============================================================
# 实体与聚合
# ============================================================

class OrderStatus(Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


@dataclass
class OrderItem:
    """订单项（聚合内部实体）"""
    product_id: str
    product_name: str
    price: Money
    quantity: int

    def subtotal(self) -> Money:
        return self.price.multiply(self.quantity)


class Order:
    """
    订单聚合根

    所有对订单的修改都必须通过 Order 的方法进行，
    以保证业务规则的一致性。
    """

    def __init__(self, order_id: str, customer_id: str):
        self.order_id = order_id
        self.customer_id = customer_id
        self.items: List[OrderItem] = []
        self.status = OrderStatus.DRAFT
        self.shipping_address: Optional[ShippingAddress] = None
        self.created_at = datetime.now()
        self._events: List[DomainEvent] = []

    # --- 业务行为 ---

    def add_item(self, product_id: str, name: str,
                 price: Money, quantity: int) -> None:
        if self.status != OrderStatus.DRAFT:
            raise ValueError("只有草稿状态的订单可以添加商品")
        if quantity <= 0:
            raise ValueError("数量必须大于0")
        self.items.append(OrderItem(product_id, name, price, quantity))

    def set_shipping_address(self, address: ShippingAddress) -> None:
        if self.status != OrderStatus.DRAFT:
            raise ValueError("只有草稿状态的订单可以修改地址")
        self.shipping_address = address

    def submit(self) -> None:
        """提交订单"""
        if self.status != OrderStatus.DRAFT:
            raise ValueError("只有草稿状态的订单可以提交")
        if not self.items:
            raise ValueError("订单中没有商品")
        if not self.shipping_address:
            raise ValueError("未设置收货地址")

        self.status = OrderStatus.SUBMITTED
        self._events.append(OrderSubmitted(
            order_id=self.order_id,
            customer_id=self.customer_id,
            total_amount=self.total_amount().amount,
        ))

    def cancel(self, reason: str) -> None:
        """取消订单"""
        if self.status in (OrderStatus.SHIPPED, OrderStatus.CANCELLED):
            raise ValueError(f"状态为 {self.status.value} 的订单无法取消")

        self.status = OrderStatus.CANCELLED
        self._events.append(OrderCancelled(
            order_id=self.order_id,
            reason=reason,
        ))

    def total_amount(self) -> Money:
        total = Money(0)
        for item in self.items:
            total = total.add(item.subtotal())
        return total

    def pull_events(self) -> List[DomainEvent]:
        """取出并清空待发布的领域事件"""
        events = self._events.copy()
        self._events.clear()
        return events


# ============================================================
# 仓储接口（领域层定义，基础设施层实现）
# ============================================================

class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]:
        pass

    @abstractmethod
    def save(self, order: Order) -> None:
        pass

    @abstractmethod
    def next_id(self) -> str:
        pass


# ============================================================
# 应用服务（编排领域对象，不包含业务逻辑）
# ============================================================

class OrderApplicationService:
    def __init__(self, repo: OrderRepository, event_publisher):
        self._repo = repo
        self._publisher = event_publisher

    def create_order(self, customer_id: str, items: list,
                     address: dict) -> str:
        order_id = self._repo.next_id()
        order = Order(order_id, customer_id)

        for item in items:
            order.add_item(
                product_id=item["product_id"],
                name=item["name"],
                price=Money(item["price"]),
                quantity=item["quantity"],
            )

        order.set_shipping_address(ShippingAddress(**address))
        order.submit()

        self._repo.save(order)

        for event in order.pull_events():
            self._publisher.publish(event)

        return order_id
```

---

## 四、DDD 与微服务的关系

### 4.1 限界上下文 = 微服务边界

限界上下文是微服务拆分的最佳指导原则。一个限界上下文通常对应一个微服务。

```
DDD 限界上下文                    微服务架构

┌──────────┐                  ┌──────────┐
│ 商品目录  │    ──────────→   │ 商品服务  │ → 商品数据库
│ Context  │                  └──────────┘
└──────────┘
                              ┌──────────┐
┌──────────┐                  │ 订单服务  │ → 订单数据库
│ 订单管理  │    ──────────→   └──────────┘
│ Context  │
└──────────┘                  ┌──────────┐
                              │ 支付服务  │ → 支付数据库
┌──────────┐                  └──────────┘
│ 支付结算  │    ──────────→
│ Context  │
└──────────┘

每个微服务：
  - 拥有独立的数据库（数据自治）
  - 内部使用自己的领域模型
  - 通过 API 或事件与其他服务通信
```

### 4.2 防腐层在微服务间的应用

当微服务 A 调用微服务 B 时，A 不应该直接使用 B 的数据模型。防腐层在微服务间起到模型隔离的作用。

```python
# === 订单服务调用商品服务 ===

# 商品服务返回的 DTO（外部模型）
# {"sku_id": "SKU001", "title": "...", "price_cents": 9900, ...}

@dataclass(frozen=True)
class ProductSnapshot:
    """订单上下文内部的商品快照（内部模型）"""
    product_id: str
    name: str
    price: Money


class ProductAntiCorruptionLayer:
    """防腐层：将商品服务的模型转换为订单上下文的模型"""

    def __init__(self, product_service_client):
        self._client = product_service_client

    def get_product_snapshot(self, sku_id: str) -> ProductSnapshot:
        # 调用商品服务 API
        data = self._client.get(f"/api/products/{sku_id}")

        # 转换为内部模型，隔离外部变化
        return ProductSnapshot(
            product_id=data["sku_id"],
            name=data["title"],
            price=Money(data["price_cents"] / 100.0),
        )
```

防腐层的价值：当商品服务修改了返回字段（比如 `title` 改为 `product_name`），订单服务只需要修改防腐层的转换逻辑，内部领域模型完全不受影响。

---

## 五、DDD 的常见误区

### 误区一：DDD = 写很多类

DDD 不是让你把简单的 CRUD 包装成一堆类。如果业务本身就是简单的增删改查，用不着 DDD。DDD 适用于业务规则复杂、领域知识丰富的场景。

### 误区二：先建数据库表，再写领域模型

DDD 的建模方向是从业务到代码，再到数据库。先和业务专家讨论领域概念，建立领域模型，最后才考虑持久化方案。数据库表结构应该服务于领域模型，而非反过来。

### 误区三：聚合设计得太大

一个聚合应该尽量小。常见错误是把整个订单（包含用户信息、商品详情、物流信息）塞进一个聚合。正确做法是：订单聚合只包含订单本身的数据，通过 ID 引用其他聚合。

```
错误：Order 聚合包含 Customer 对象和 Product 对象
正确：Order 聚合只持有 customer_id 和 product_id
```

### 误区四：忽略战略设计，只用战术设计的术语

很多团队学了 Entity、Value Object、Repository 这些术语，但从未认真划分限界上下文。结果是在一个巨大的单体中使用 DDD 的战术模式，代码反而更复杂了。

### 误区五：所有项目都用 DDD

DDD 有学习成本和实施成本。以下场景不适合 DDD：
- 简单的 CRUD 应用（用 Django Admin 就够了）
- 技术驱动的项目（如中间件、基础设施工具）
- 团队对 DDD 完全没有经验，且项目工期紧张

**判断是否需要 DDD 的简单标准：** 如果你的业务专家能和你聊两个小时的业务规则而不重复，那这个领域值得用 DDD。
