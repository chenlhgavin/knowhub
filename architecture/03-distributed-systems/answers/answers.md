# 第三章 分布式系统 - 习题答案

## 一、选择题

### 1. 答案：C
CAP定理指出，在网络分区发生时，系统必须在一致性（C）和可用性（A）之间做选择。分区容错性（P）在分布式系统中是必须保证的，因为网络分区是不可避免的。

### 2. 答案：D
2PC必须使用持久化日志（WAL）来保证正确性。协调者在做出Commit/Abort决定后必须先写入日志再发送决定，否则协调者宕机重启后无法恢复决定，参与者将永远阻塞。

### 3. 答案：B
空回滚是指Try请求由于网络原因未到达参与者，但协调者超时后发起了Cancel。参与者收到Cancel时并没有执行过Try，需要识别这种情况并直接返回成功。

### 4. 答案：D
Raft算法中节点只有三种状态：Follower（跟随者）、Candidate（候选人）、Leader（领导者）。Observer不是Raft的合法状态（Observer是ZooKeeper中的概念）。

### 5. 答案：C
Saga模式保证的是最终一致性而非强一致性。编排式Saga（Choreography）不需要中心协调器，协调式Saga（Orchestration）才需要。补偿事务必须是幂等的，因为网络问题可能导致重复调用。

### 6. 答案：B
Paxos的安全性保证：当Proposer收到的Promise中包含已接受的值时，必须使用编号最大的那个已接受值，而不能使用自己的值。这确保了一旦某个值被多数派接受，后续提案只能提议相同的值。

---

## 二、简答题

### 7. BASE理论

**BASE理论：**
- Basically Available（基本可用）：系统在出现故障时，允许损失部分可用性（如响应时间变长、功能降级）
- Soft State（软状态）：允许系统中的数据存在中间状态，即允许不同节点的数据副本之间存在短暂的不一致
- Eventually Consistent（最终一致性）：经过一段时间后，所有数据副本最终会达到一致状态

**与ACID的区别：**

| 特性 | ACID | BASE |
|------|------|------|
| 一致性 | 强一致性 | 最终一致性 |
| 可用性 | 可能牺牲可用性 | 优先保证可用性 |
| 适用场景 | 单机数据库、金融系统 | 分布式系统、互联网应用 |
| 设计理念 | 悲观（先保证正确） | 乐观（允许临时不一致） |

**实际例子：** 电商系统中，用户下单后库存的扣减。下单时先在订单服务创建订单（本地事务），然后通过消息队列异步通知库存服务扣减库存。在消息被消费之前，订单和库存数据是不一致的（软状态），但最终库存会被正确扣减（最终一致性）。

### 8. 2PC vs TCC

| 特性 | 2PC | TCC |
|------|-----|-----|
| 一致性 | 强一致 | 最终一致 |
| 性能 | 低（长时间持有锁） | 高（不长时间持有数据库锁） |
| 业务侵入 | 低（数据库层面） | 高（需要实现Try/Confirm/Cancel） |
| 实现复杂度 | 中等 | 高（需处理幂等、空回滚、悬挂） |
| 阻塞问题 | 协调者故障时参与者阻塞 | 无阻塞问题 |
| 适用场景 | 数据库层面的跨库事务 | 资金、库存等核心业务 |

**2PC适用场景：** 同一技术栈内的跨数据库事务，如MySQL XA事务。对一致性要求极高且能接受性能损失的场景。

**TCC适用场景：** 跨服务的分布式事务，特别是资金相关的业务。需要高性能且业务逻辑可以拆分为Try/Confirm/Cancel三步的场景。

### 9. Raft Leader选举流程

**选举流程：**
1. Follower在选举超时时间内未收到Leader心跳，转变为Candidate
2. Candidate增加当前任期号（Term），投票给自己
3. Candidate向所有其他节点发送RequestVote RPC
4. 等待结果：
   - 收到多数派投票 → 成为Leader，立即发送心跳
   - 收到合法Leader的消息（任期号≥自己）→ 转回Follower
   - 选举超时（无人获得多数票）→ 增加任期号，重新选举

**投票规则：** 每个节点在每个任期内最多投一票（先到先得），且候选人的日志必须至少和投票者一样新。

**为什么使用随机化超时：** 如果所有节点使用相同的超时时间，它们可能同时发起选举，导致选票被瓜分，没有人能获得多数票。随机化超时（如150ms-300ms）使得某个节点大概率最先超时并发起选举，在其他节点超时前就获得了多数票，避免了反复分票的问题。

### 10. 脑裂问题

**脑裂（Split Brain）** 是指在分布式系统中，由于网络分区，集群被分成两个或多个互相无法通信的子集，每个子集都认为自己是"正常"的，各自选举出Leader并独立提供服务，导致数据不一致。

```
正常状态：
  [A] [B] [C] [D] [E]  → Leader: A

网络分区后：
  [A] [B]  |  [C] [D] [E]
  Leader:A |  Leader:C（新选举）
  两个Leader同时接受写请求 → 数据不一致！
```

**避免方法：**
1. **多数派机制（Quorum）：** Raft/Paxos要求获得多数派投票才能成为Leader。5个节点中，只有包含3个以上节点的分区才能选出Leader。上例中[A][B]只有2个节点，无法选出Leader。
2. **Fencing Token：** 每次选举产生一个单调递增的token，旧Leader的请求会被拒绝。
3. **租约（Lease）：** Leader持有一个有时间限制的租约，租约过期前其他节点不能成为Leader。旧Leader在租约过期后自动放弃Leader身份。

---

## 三、设计题

### 11. 分布式锁设计

```python
import uuid
import time

class RedisDistributedLock:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.client_id = str(uuid.uuid4())

    def acquire(self, lock_name, expire_seconds=30):
        """加锁"""
        lock_key = f"lock:{lock_name}"
        # SET NX EX：只在key不存在时设置，同时设置过期时间
        # value存储client_id，用于解锁时验证身份
        result = self.redis.set(lock_key, self.client_id, nx=True, ex=expire_seconds)
        return result is not None

    def release(self, lock_name):
        """解锁 - 必须用Lua脚本保证原子性"""
        lock_key = f"lock:{lock_name}"
        # Lua脚本：检查value是否是自己的，是则删除
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        return self.redis.eval(lua_script, 1, lock_key, self.client_id)

    def acquire_with_retry(self, lock_name, expire_seconds=30, retry_times=3, retry_delay=0.5):
        """带重试的加锁"""
        for i in range(retry_times):
            if self.acquire(lock_name, expire_seconds):
                return True
            time.sleep(retry_delay)
        return False
```

**需要注意的问题：**
1. **解锁必须验证身份：** 只能释放自己加的锁，防止误删别人的锁。必须用Lua脚本保证"检查+删除"的原子性。
2. **过期时间设置：** 过期时间要大于业务执行时间，否则业务还没执行完锁就过期了。可以使用看门狗（Watchdog）机制自动续期。
3. **Redis主从切换：** 如果Master宕机，锁信息可能还没同步到Slave，新Master上锁丢失。可以使用RedLock算法（在多个独立Redis实例上加锁）。
4. **可重入实现：** 使用Hash结构存储锁，field为client_id，value为重入次数。

### 12. Saga模式设计

**正常流程：**
```
T1: 创建订单（状态：待确认）
  ↓ 成功
T2: 扣减库存
  ↓ 成功
T3: 扣减余额
  ↓ 成功
T4: 创建物流单
  ↓ 成功
T5: 更新订单状态为已完成
```

**补偿流程（假设T3扣减余额失败）：**
```
T1: 创建订单 ✓
T2: 扣减库存 ✓
T3: 扣减余额 ✗ → 触发补偿
  ↓
C2: 恢复库存（补偿T2）
C1: 取消订单（补偿T1）
```

**每个步骤的补偿操作：**

| 正向操作 | 补偿操作 |
|---------|---------|
| T1: 创建订单（待确认） | C1: 更新订单状态为已取消 |
| T2: 扣减库存 | C2: 恢复库存 |
| T3: 扣减余额 | C3: 恢复余额 |
| T4: 创建物流单 | C4: 取消物流单 |

**补偿失败处理：**
1. **重试：** 补偿操作失败后自动重试，设置最大重试次数（如5次），使用指数退避
2. **补偿操作必须幂等：** 即使重复执行也不会产生副作用
3. **人工介入：** 重试耗尽后记录到"异常事务表"，通知运维人员人工处理
4. **定时任务兜底：** 后台定时扫描超时未完成的Saga，触发补偿或人工告警
