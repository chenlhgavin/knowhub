# 缓存与消息队列

## 一、缓存

### 1.1 为什么需要缓存

```
数据库查询：磁盘I/O，延迟通常在 1-10ms
缓存查询：内存访问，延迟通常在 0.1-1ms

典型场景：
  - 热点数据读取（用户信息、商品详情）
  - 计算结果缓存（排行榜、统计数据）
  - 会话缓存（Session、Token）
  - 页面缓存（HTML片段、API响应）
```

### 1.2 缓存模式

**Cache-Aside（旁路缓存）：** 最常用的缓存模式。

```
读流程：
  1. 先查缓存
  2. 缓存命中 → 直接返回
  3. 缓存未命中 → 查数据库 → 写入缓存 → 返回

写流程：
  1. 更新数据库
  2. 删除缓存（而非更新缓存）

为什么删除而非更新缓存？
  - 避免并发写导致缓存与数据库不一致
  - 缓存值可能是复杂计算的结果，每次更新代价大
  - 删除是幂等操作，更安全
```

```python
class CacheAsideService:
    def __init__(self, cache, db):
        self.cache = cache
        self.db = db

    def get_user(self, user_id):
        # 1. 查缓存
        cache_key = f"user:{user_id}"
        user = self.cache.get(cache_key)
        if user:
            return user

        # 2. 缓存未命中，查数据库
        user = self.db.query("SELECT * FROM users WHERE id = %s", user_id)
        if user:
            # 3. 写入缓存，设置过期时间
            self.cache.set(cache_key, user, ex=3600)
        return user

    def update_user(self, user_id, data):
        # 1. 更新数据库
        self.db.execute("UPDATE users SET name = %s WHERE id = %s", data['name'], user_id)
        # 2. 删除缓存
        self.cache.delete(f"user:{user_id}")
```

**Read-Through / Write-Through：**

```
Read-Through：
  应用 → 缓存层（未命中时自动从数据库加载）
  应用不直接访问数据库，缓存层封装了数据库访问逻辑

Write-Through：
  应用 → 缓存层 → 同步写数据库
  写操作同时更新缓存和数据库，保证强一致

Write-Behind（Write-Back）：
  应用 → 缓存层 → 异步批量写数据库
  写操作只更新缓存，后台异步刷入数据库
  优点：写性能极高
  缺点：缓存宕机可能丢数据
```

### 1.3 缓存问题与解决方案

**缓存穿透：** 查询不存在的数据，请求直接打到数据库。

```
场景：恶意请求大量不存在的用户ID

解决方案1：缓存空值
  查询数据库返回空 → 缓存空值（设置较短过期时间）
  cache.set("user:999999", NULL, ex=60)

解决方案2：布隆过滤器
  在缓存前加一层布隆过滤器
  请求 → 布隆过滤器 → 不存在则直接返回
                    → 可能存在则查缓存/数据库

  布隆过滤器特点：
  - 判断不存在一定不存在
  - 判断存在可能不存在（有误判率）
  - 空间效率极高（1亿数据约120MB）
```

**缓存击穿：** 热点key过期瞬间，大量请求同时打到数据库。

```
场景：某明星微博热搜的缓存过期

解决方案1：互斥锁
  缓存未命中时，只允许一个线程查数据库并回填缓存
  其他线程等待或返回旧数据

解决方案2：热点key永不过期
  不设置过期时间，通过后台线程定期更新

解决方案3：逻辑过期
  缓存中存储逻辑过期时间
  发现逻辑过期后，后台异步更新，当前请求返回旧数据
```

```python
import threading
import time

class CacheWithMutex:
    def __init__(self, cache, db):
        self.cache = cache
        self.db = db
        self._locks = {}

    def get_with_mutex(self, key, query_func, ttl=3600):
        value = self.cache.get(key)
        if value is not None:
            return value

        # 获取分布式锁
        lock_key = f"lock:{key}"
        if self.cache.set(lock_key, "1", nx=True, ex=10):
            try:
                # 双重检查
                value = self.cache.get(key)
                if value is not None:
                    return value
                # 查数据库
                value = query_func()
                if value is not None:
                    self.cache.set(key, value, ex=ttl)
                return value
            finally:
                self.cache.delete(lock_key)
        else:
            # 未获取到锁，短暂等待后重试
            time.sleep(0.1)
            return self.get_with_mutex(key, query_func, ttl)
```

**缓存雪崩：** 大量缓存key同时过期，或缓存服务宕机。

```
场景：系统启动时批量加载缓存，所有key设置相同过期时间

解决方案1：过期时间加随机值
  ttl = base_ttl + random(0, 300)  # 基础过期时间 + 随机0-300秒

解决方案2：缓存集群高可用
  Redis Sentinel 或 Redis Cluster
  避免单点故障导致整个缓存层不可用

解决方案3：多级缓存
  本地缓存（Caffeine/Guava）→ 分布式缓存（Redis）→ 数据库
  即使Redis不可用，本地缓存仍可提供服务
```

### 1.4 Redis数据结构与应用

```
String：
  - 缓存对象（JSON序列化）
  - 计数器（INCR）
  - 分布式锁（SET NX EX）

Hash：
  - 存储对象的多个字段（HSET user:1 name "Alice" age 25）
  - 购物车（HSET cart:user1 product1 2 product2 1）

List：
  - 消息队列（LPUSH + BRPOP）
  - 最新消息列表（LPUSH + LRANGE）

Set：
  - 标签系统（SADD）
  - 共同好友（SINTER）
  - 去重（SISMEMBER）

Sorted Set：
  - 排行榜（ZADD + ZREVRANGE）
  - 延迟队列（score为执行时间）
  - 滑动窗口限流

HyperLogLog：
  - UV统计（基数估算，误差约0.81%）
  - 每个key只占12KB，可统计2^64个元素

Bitmap：
  - 用户签到（SETBIT sign:user1:202401 1 1）
  - 在线状态（SETBIT online 12345 1）
  - 布隆过滤器底层实现
```

### 1.5 Redis集群方案

```
Redis Sentinel（哨兵模式）：
  - 监控Master和Slave的运行状态
  - Master故障时自动故障转移
  - 适合数据量不大但需要高可用的场景
  - 不支持数据分片

Redis Cluster（集群模式）：
  - 数据自动分片到16384个槽位
  - 每个节点负责一部分槽位
  - 支持自动故障转移
  - 适合大数据量、高吞吐的场景

  数据分片：
    slot = CRC16(key) % 16384
    节点A: 槽位 0-5460
    节点B: 槽位 5461-10922
    节点C: 槽位 10923-16383
```

---

## 二、消息队列

### 2.1 消息队列的作用

```
1. 异步处理：
   同步：用户注册 → 写数据库 → 发邮件 → 发短信 → 返回（总耗时500ms）
   异步：用户注册 → 写数据库 → 发消息 → 返回（总耗时100ms）
                                  ↓
                            消费者发邮件
                            消费者发短信

2. 流量削峰：
   秒杀场景：瞬间10万请求 → 消息队列 → 消费者按能力处理（1000/s）
   消息队列充当缓冲区，保护下游系统

3. 系统解耦：
   订单服务 → [消息队列] → 库存服务
                         → 积分服务
                         → 通知服务
   订单服务不需要知道有多少下游消费者
```

### 2.2 消息模型

```
点对点（Queue）：
  生产者 → [Queue] → 消费者A
  每条消息只被一个消费者消费
  适用：任务分发、工作队列

发布订阅（Topic）：
  生产者 → [Topic] → 消费者组A（消费者A1, A2）
                   → 消费者组B（消费者B1, B2）
  每条消息被每个消费者组消费一次
  组内只有一个消费者处理该消息
  适用：事件广播、日志收集
```

### 2.3 Kafka核心概念

```
架构：
  Producer → [Broker集群] → Consumer Group
              Topic
            /   |   \
         P0    P1    P2    （Partition，分区）
         |     |     |
        副本   副本   副本   （Replica，副本）

核心概念：
  - Topic：消息的逻辑分类
  - Partition：Topic的物理分片，是并行度的基本单位
  - Offset：消息在Partition中的位置，单调递增
  - Consumer Group：消费者组，组内消费者分摊Partition
  - Broker：Kafka服务器节点

分区与消费者的关系：
  Topic有3个Partition，Consumer Group有2个消费者
  Consumer1 → P0, P1
  Consumer2 → P2
  注意：消费者数量不应超过Partition数量
```

### 2.4 消息可靠性

```
生产者可靠性（消息不丢失）：
  acks=0：不等待确认，可能丢消息
  acks=1：Leader确认即返回，Leader宕机可能丢消息
  acks=all：所有ISR副本确认，最可靠但延迟最高

Broker可靠性：
  - 多副本机制：每个Partition有多个副本
  - ISR（In-Sync Replicas）：与Leader保持同步的副本集合
  - min.insync.replicas=2：至少2个副本同步才允许写入

消费者可靠性（消息不重复消费）：
  - 手动提交Offset：处理完消息后再提交
  - 幂等消费：即使重复消费也不影响结果
```

```python
# Kafka生产者示例（Python）
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all',           # 等待所有副本确认
    retries=3,            # 失败重试3次
    max_in_flight_requests_per_connection=1,  # 保证顺序
)

# 发送消息
future = producer.send('order_topic', value={'order_id': '001', 'amount': 99.9})
result = future.get(timeout=10)  # 同步等待确认
print(f"消息发送成功: partition={result.partition}, offset={result.offset}")
```

```python
# Kafka消费者示例
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'order_topic',
    bootstrap_servers=['localhost:9092'],
    group_id='order_processor',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    enable_auto_commit=False,  # 手动提交offset
)

for message in consumer:
    try:
        order = message.value
        process_order(order)  # 业务处理
        consumer.commit()     # 处理成功后提交offset
    except Exception as e:
        log.error(f"处理失败: {e}")
        # 不提交offset，下次会重新消费
```

### 2.5 消息顺序性

```
全局有序：
  只使用一个Partition → 性能差，不推荐

分区有序（推荐）：
  相同key的消息发送到同一个Partition
  例：同一个订单的所有消息发到同一个Partition

  producer.send('order_topic',
      key=order_id.encode(),  # 按订单ID分区
      value=message)

  Partition内的消息严格有序
  不同Partition之间无顺序保证
```

### 2.6 消息积压处理

```
消息积压的原因：
  - 消费者处理速度跟不上生产速度
  - 消费者故障导致停止消费
  - 下游服务响应慢

处理方案：
  1. 紧急扩容：增加消费者实例（需要同时增加Partition）
  2. 跳过非关键消息：如果消息有时效性，跳过过期消息
  3. 转储：将积压消息转移到另一个Topic，慢慢消费
  4. 降级：临时关闭非核心消费逻辑

预防措施：
  - 监控消费延迟（Consumer Lag）
  - 设置告警阈值
  - 消费者做好性能优化（批量处理、异步I/O）
```

### 2.7 消息队列选型

```
| 特性        | Kafka          | RabbitMQ       | RocketMQ       |
|------------|----------------|----------------|----------------|
| 吞吐量      | 百万级/s       | 万级/s         | 十万级/s       |
| 延迟        | ms级           | μs级           | ms级           |
| 消息可靠性   | 高             | 高             | 高             |
| 消息顺序     | 分区有序       | 不保证         | 队列有序       |
| 事务消息     | 支持           | 支持           | 支持           |
| 延迟消息     | 不原生支持     | 支持（插件）    | 原生支持       |
| 适用场景     | 日志、大数据   | 业务消息       | 电商、金融     |
| 社区生态     | 非常活跃       | 活跃           | 国内活跃       |

选型建议：
  - 日志收集、流处理、大数据场景 → Kafka
  - 业务消息、需要灵活路由 → RabbitMQ
  - 电商、金融、需要事务消息和延迟消息 → RocketMQ
```

---

## 三、缓存与消息队列的协作

### 3.1 典型架构

```
用户请求 → API网关 → 业务服务 → 缓存（Redis）
                                    ↓ 未命中
                                 数据库（MySQL）
                        ↓
                   消息队列（Kafka）
                        ↓
              异步消费者（通知、统计、搜索索引更新）

数据更新流程：
  1. 业务服务更新数据库
  2. 业务服务删除缓存
  3. 业务服务发送变更消息到消息队列
  4. 消费者收到消息后更新搜索索引、统计数据等
```

### 3.2 缓存与数据库一致性的最终方案

```
方案：基于消息队列的缓存更新

  1. 业务服务更新数据库
  2. 业务服务发送缓存失效消息到MQ
  3. 缓存更新消费者收到消息后删除缓存
  4. 如果删除失败，消息会重新投递（重试机制）

优点：
  - 通过MQ的重试机制保证缓存最终被删除
  - 业务服务不需要关心缓存删除是否成功
  - 解耦了业务逻辑和缓存管理

进阶方案：监听数据库Binlog
  MySQL Binlog → Canal → 消息队列 → 缓存更新消费者
  完全不侵入业务代码，数据库变更自动同步到缓存
```

---

## 本章小结

缓存和消息队列是构建高性能、高可用系统的两大基础组件。关键要点：

1. 缓存的核心是用空间换时间，需要处理好穿透、击穿、雪崩三大问题
2. Cache-Aside是最常用的缓存模式，写操作应删除缓存而非更新缓存
3. 消息队列的三大作用：异步处理、流量削峰、系统解耦
4. 消息可靠性需要生产者、Broker、消费者三方共同保证
5. 选择合适的消息队列取决于业务场景：吞吐量、延迟、功能需求
