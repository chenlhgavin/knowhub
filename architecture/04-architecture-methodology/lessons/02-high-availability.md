# 高可用设计

## 一、高可用的度量

### 1.1 SLA与可用性等级

SLA（Service Level Agreement）是服务提供者与用户之间的服务质量约定，通常用"几个9"来衡量。

```
可用性等级：
  99%     (2个9)  → 年停机时间 3.65天    → 个人项目
  99.9%   (3个9)  → 年停机时间 8.76小时  → 普通业务系统
  99.99%  (4个9)  → 年停机时间 52.6分钟  → 核心业务系统
  99.999% (5个9)  → 年停机时间 5.26分钟  → 金融、电信核心系统
  99.9999%(6个9)  → 年停机时间 31.5秒    → 极端场景

计算公式：
  可用性 = (总时间 - 故障时间) / 总时间 × 100%
  可用性 = MTTF / (MTTF + MTTR)

  MTTF（Mean Time To Failure）：平均无故障时间
  MTTR（Mean Time To Recovery）：平均恢复时间
```

**提高可用性的两个方向：**
- 提高 MTTF：减少故障发生（冗余、容错）
- 降低 MTTR：加快故障恢复（监控、自动化）

### 1.2 故障分类

```
按影响范围：
  - 单点故障：单个节点或组件失效
  - 局部故障：某个服务或机房失效
  - 全局故障：整个系统不可用

按故障原因：
  - 硬件故障：磁盘损坏、网络中断、电源故障
  - 软件故障：Bug、内存泄漏、死锁
  - 人为故障：误操作、配置错误（占比最高，约70%）
  - 外部因素：DDoS攻击、第三方服务故障、自然灾害
```

---

## 二、冗余设计

### 2.1 无状态服务的冗余

无状态服务不保存任何会话数据，任何实例都可以处理任何请求。

```
负载均衡 + 多实例：
  客户端 → 负载均衡器 → 实例A
                      → 实例B
                      → 实例C

扩缩容策略：
  - 水平扩展：增加实例数量
  - 自动扩缩容：根据CPU/内存/QPS自动调整实例数
  - 预热扩容：大促前提前扩容

Kubernetes HPA示例：
  apiVersion: autoscaling/v2
  kind: HorizontalPodAutoscaler
  spec:
    minReplicas: 3
    maxReplicas: 20
    metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### 2.2 有状态服务的冗余

有状态服务（数据库、缓存）需要数据复制来实现冗余。

```
主从复制（Master-Slave）：
  写请求 → Master → 同步/异步复制 → Slave1
                                   → Slave2
  读请求 → Slave1 / Slave2

  优点：读写分离，提高读性能
  缺点：主从延迟，主节点单点

主主复制（Master-Master）：
  写请求 → Master1 ⇄ 双向复制 ⇄ Master2

  优点：两个节点都可写
  缺点：冲突处理复杂，一般只用于跨机房容灾

MySQL主从复制模式：
  - 异步复制：性能最好，但主库宕机可能丢数据
  - 半同步复制：至少一个从库确认后才返回，平衡性能和可靠性
  - 组复制（MGR）：基于Paxos的多数派确认，强一致
```

### 2.3 多机房部署

```
同城双活：
  机房A（主）  ←→  机房B（备）
  - 两个机房在同一城市，网络延迟 < 2ms
  - 正常时两个机房都处理流量
  - 一个机房故障时，流量全部切到另一个机房

异地多活：
  北京机房  ←→  上海机房  ←→  广州机房
  - 每个机房独立处理本地用户的请求
  - 数据通过消息队列异步同步
  - 核心挑战：数据一致性

异地多活的数据同步策略：
  - 按用户分片：用户A的数据只在北京机房，用户B的数据只在上海机房
  - 最终一致性：允许短暂的数据不一致，通过异步同步最终达到一致
  - 冲突解决：Last-Write-Wins、向量时钟、业务层合并
```

---

## 三、容错设计

### 3.1 超时控制

```
超时设置原则：
  - 连接超时：通常 1-3 秒
  - 读超时：根据接口的P99延迟设置，通常为P99的2-3倍
  - 写超时：根据业务需求，通常比读超时长

超时传递：
  客户端（总超时5s）→ 网关（超时4s）→ 服务A（超时3s）→ 服务B（超时2s）
  每一层的超时应该小于上一层，避免上游已经超时了下游还在处理
```

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 带超时和重试的HTTP客户端
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,  # 1s, 2s, 4s
    status_forcelist=[502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

response = session.get(
    "http://api.example.com/users",
    timeout=(3, 5)  # (连接超时, 读超时)
)
```

### 3.2 重试机制

```
重试策略：
  - 固定间隔：每次重试间隔相同（如每隔1秒）
  - 指数退避：间隔指数增长（1s, 2s, 4s, 8s...）
  - 指数退避+抖动：在指数退避基础上加随机偏移，避免重试风暴

重试的注意事项：
  1. 只对可重试的错误重试（超时、5xx），不对4xx重试
  2. 设置最大重试次数，避免无限重试
  3. 重试的接口必须是幂等的
  4. 注意重试放大效应：A→B→C，如果每层重试3次，最坏情况C会收到27次请求
```

```python
import random
import time

def retry_with_exponential_backoff(func, max_retries=3, base_delay=1.0):
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries:
                raise
            # 指数退避 + 抖动
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"第{attempt + 1}次失败: {e}, {delay:.1f}秒后重试")
            time.sleep(delay)
```

### 3.3 熔断器（Circuit Breaker）

熔断器模式防止故障级联传播，当下游服务故障时快速失败而不是等待超时。

```
熔断器三种状态：

  关闭（Closed）→ 失败率超过阈值 → 打开（Open）
       ↑                              |
       |                         超时后进入半开
       |                              ↓
       └── 探测成功 ←── 半开（Half-Open）
                        探测失败 → 回到打开

关闭状态：正常放行请求，统计失败率
打开状态：直接拒绝请求，返回降级结果
半开状态：放行少量探测请求，成功则关闭熔断器，失败则重新打开
```

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30, half_open_max=3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max = half_open_max
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.half_open_count = 0

    def call(self, func, fallback=None):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.half_open_count = 0
            else:
                return fallback() if fallback else None

        try:
            result = func()
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.state == CircuitState.HALF_OPEN or self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
            return fallback() if fallback else None
```

### 3.4 限流（Rate Limiting）

```
常用限流算法：

1. 固定窗口计数器：
   |----窗口1----|----窗口2----|
   每个窗口内最多允许N个请求
   问题：窗口边界处可能出现2N的突发流量

2. 滑动窗口计数器：
   将窗口细分为多个小窗口，滑动统计
   解决了固定窗口的边界问题

3. 漏桶算法（Leaky Bucket）：
   请求 → [漏桶] → 匀速流出
   特点：流出速率恒定，平滑流量
   缺点：无法应对突发流量

4. 令牌桶算法（Token Bucket）：
   [令牌桶] ← 匀速放入令牌
   请求到来时取一个令牌，没有令牌则拒绝
   特点：允许一定程度的突发流量（桶中积累的令牌）
   应用：Nginx限流、Guava RateLimiter
```

```python
import time
import threading

class TokenBucket:
    def __init__(self, rate, capacity):
        self.rate = rate          # 每秒放入的令牌数
        self.capacity = capacity  # 桶的容量
        self.tokens = capacity    # 当前令牌数
        self.last_time = time.time()
        self.lock = threading.Lock()

    def acquire(self):
        with self.lock:
            now = time.time()
            # 补充令牌
            self.tokens = min(
                self.capacity,
                self.tokens + (now - self.last_time) * self.rate
            )
            self.last_time = now
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False

# 使用：每秒100个请求，允许突发200个
limiter = TokenBucket(rate=100, capacity=200)
if limiter.acquire():
    # 处理请求
    pass
else:
    # 返回429 Too Many Requests
    pass
```

### 3.5 降级（Degradation）

```
降级策略：
  1. 功能降级：关闭非核心功能（推荐、评论），保证核心功能（下单、支付）
  2. 数据降级：返回缓存数据或默认数据，而非实时数据
  3. 体验降级：返回简化版页面，减少资源加载
  4. 写降级：将同步写改为异步写，先返回成功再后台处理

降级开关设计：
  - 手动降级：运维人员通过配置中心手动开启
  - 自动降级：根据系统指标（CPU、延迟、错误率）自动触发
  - 预案降级：大促前预设降级预案，一键执行
```

---

## 四、故障检测与恢复

### 4.1 健康检查

```
健康检查类型：
  1. 存活检查（Liveness）：进程是否还活着
     - TCP端口检查
     - HTTP GET /health 返回200
     - 进程是否存在

  2. 就绪检查（Readiness）：服务是否准备好接收流量
     - 数据库连接是否正常
     - 缓存是否可用
     - 依赖服务是否可达

  3. 启动检查（Startup）：服务是否完成初始化
     - 配置加载完成
     - 缓存预热完成
     - 连接池初始化完成

Kubernetes健康检查配置：
  livenessProbe:
    httpGet:
      path: /health/live
      port: 8080
    initialDelaySeconds: 10
    periodSeconds: 5
    failureThreshold: 3

  readinessProbe:
    httpGet:
      path: /health/ready
      port: 8080
    initialDelaySeconds: 5
    periodSeconds: 3
    failureThreshold: 2
```

### 4.2 故障转移（Failover）

```
主从切换：
  1. 检测到主节点故障（心跳超时）
  2. 选举新的主节点（从节点中选择数据最新的）
  3. 将流量切换到新主节点
  4. 通知其他从节点连接新主节点

Redis Sentinel故障转移流程：
  1. Sentinel检测到Master不可达（主观下线）
  2. 多个Sentinel确认Master不可达（客观下线）
  3. Sentinel选举Leader
  4. Leader Sentinel选择最优Slave提升为Master
  5. 通知其他Slave复制新Master
  6. 通知客户端新Master地址

MySQL MHA故障转移：
  1. MHA Manager检测到Master故障
  2. 从所有Slave中选择数据最新的
  3. 对比relay log，补齐差异数据
  4. 将选中的Slave提升为新Master
  5. 其他Slave指向新Master
```

### 4.3 混沌工程

混沌工程通过主动注入故障来验证系统的容错能力。

```
Netflix的混沌工程实践：
  - Chaos Monkey：随机终止生产环境的实例
  - Chaos Kong：模拟整个区域（Region）故障
  - Latency Monkey：注入网络延迟

常见故障注入类型：
  - 进程级：杀死进程、CPU满载、内存耗尽
  - 网络级：网络延迟、丢包、分区
  - 存储级：磁盘满、I/O延迟
  - 依赖级：下游服务不可用、响应慢

实施原则：
  1. 先在测试环境验证
  2. 从小范围开始（单个实例→单个机房→跨机房）
  3. 有完善的监控和快速回滚能力
  4. 建立故障注入的自动化流程
```

---

## 五、发布策略

### 5.1 滚动发布（Rolling Update）

```
逐步替换旧版本实例：
  时刻1: [v1] [v1] [v1] [v1]
  时刻2: [v2] [v1] [v1] [v1]
  时刻3: [v2] [v2] [v1] [v1]
  时刻4: [v2] [v2] [v2] [v1]
  时刻5: [v2] [v2] [v2] [v2]

优点：零停机，资源利用率高
缺点：发布过程中新旧版本共存，需要兼容
```

### 5.2 蓝绿发布（Blue-Green Deployment）

```
准备两套完全相同的环境：
  蓝环境（当前生产）: [v1] [v1] [v1]  ← 流量
  绿环境（新版本）:   [v2] [v2] [v2]

验证绿环境无问题后，切换流量：
  蓝环境: [v1] [v1] [v1]
  绿环境: [v2] [v2] [v2]  ← 流量

优点：切换快速，回滚简单（切回蓝环境）
缺点：需要双倍资源
```

### 5.3 金丝雀发布（Canary Release）

```
先将少量流量导向新版本：
  阶段1: v1(95%) / v2(5%)   观察指标
  阶段2: v1(80%) / v2(20%)  观察指标
  阶段3: v1(50%) / v2(50%)  观察指标
  阶段4: v1(0%)  / v2(100%) 发布完成

如果任何阶段发现问题，立即将流量全部切回v1

优点：风险可控，可以逐步验证
缺点：发布周期长，需要流量调度能力
```

### 5.4 灰度发布

```
按特定规则将部分用户路由到新版本：
  - 按用户ID：user_id % 100 < 10 → 新版本
  - 按地域：北京用户 → 新版本
  - 按设备：iOS用户 → 新版本
  - 按白名单：内部员工 → 新版本

与金丝雀的区别：
  金丝雀是随机分配流量比例
  灰度是按规则精确控制哪些用户使用新版本
```

---

## 六、高可用架构模式总结

```
核心原则：
  1. 消除单点故障：任何组件都应该有冗余
  2. 故障隔离：一个组件的故障不应该影响其他组件
  3. 快速恢复：故障发生后能快速自动恢复
  4. 优雅降级：在部分故障时仍能提供核心服务

设计检查清单：
  □ 服务是否无状态？能否水平扩展？
  □ 数据库是否有主从复制？故障转移是否自动？
  □ 是否有超时、重试、熔断机制？
  □ 是否有限流保护？
  □ 是否有降级预案？
  □ 是否有完善的监控和告警？
  □ 是否做过故障演练？
  □ 发布是否支持快速回滚？
```
