# 分布式事务

## 1. 本地事务的局限性

### 1.1 什么是本地事务

本地事务是指在单个数据库实例上执行的事务，由数据库的ACID特性保证。例如在MySQL中：

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE user_id = 1;
UPDATE accounts SET balance = balance + 100 WHERE user_id = 2;
COMMIT;
```

这个转账操作在单个数据库中可以通过本地事务轻松保证原子性和一致性。

### 1.2 为什么本地事务不够用

当系统演进到微服务架构或分库分表后，一个业务操作可能涉及多个数据库或多个服务：

```
电商下单流程：
1. 订单服务 → 订单数据库：创建订单
2. 库存服务 → 库存数据库：扣减库存
3. 账户服务 → 账户数据库：扣减余额
4. 积分服务 → 积分数据库：增加积分
```

每个服务有自己的数据库，本地事务无法跨数据库保证ACID。如果订单创建成功但库存扣减失败，系统就会处于不一致状态。

### 1.3 分布式事务的核心挑战

- **网络不可靠**：服务之间的调用可能超时、丢失或重复
- **节点可能故障**：任何参与者或协调者都可能在任意时刻宕机
- **没有全局时钟**：无法精确判断各节点操作的先后顺序
- **部分失败**：部分操作成功、部分失败是常态

## 2. 2PC（两阶段提交）

### 2.1 协议流程

两阶段提交（Two-Phase Commit）是最经典的分布式事务协议，由Jim Gray在1978年提出。

**第一阶段：准备阶段（Prepare/Vote）**

```
协调者（Coordinator）                    参与者（Participants）
    |                                      |
    |-------- Prepare请求 -------->        |
    |                                      | 执行事务操作（但不提交）
    |                                      | 将Undo和Redo日志写入磁盘
    |<------- Vote Yes/No ---------        |
    |                                      |
```

1. 协调者向所有参与者发送Prepare请求
2. 参与者执行事务操作，将数据写入Undo和Redo日志
3. 参与者根据执行结果，向协调者回复Yes（可以提交）或No（无法提交）

**第二阶段：提交阶段（Commit/Abort）**

情况一：所有参与者都回复Yes
```
协调者                                    参与者
    |                                      |
    |-------- Commit请求 -------->         |
    |                                      | 正式提交事务
    |                                      | 释放锁和资源
    |<------- Ack ----------------         |
    |                                      |
```

情况二：任何一个参与者回复No，或者超时未回复
```
协调者                                    参与者
    |                                      |
    |-------- Abort请求 --------->         |
    |                                      | 利用Undo日志回滚事务
    |                                      | 释放锁和资源
    |<------- Ack ----------------         |
    |                                      |
```

### 2.2 协调者故障分析

**场景1：协调者在发送Prepare之前故障**
- 影响：事务还未开始，无影响
- 恢复：协调者重启后可以重新发起事务

**场景2：协调者在发送Prepare之后、收到所有Vote之前故障**
- 影响：参与者已经执行了事务操作并持有锁，但不知道是否应该提交
- 恢复：参与者等待超时后自行回滚（安全的，因为协调者还没做出决定）

**场景3：协调者在做出Commit/Abort决定后、发送决定之前故障**
- 影响：这是最危险的情况。协调者已经决定了，但参与者不知道决定是什么
- 恢复：协调者必须将决定写入持久化日志（WAL），重启后重新发送决定

**场景4：协调者在发送部分Commit/Abort后故障**
- 影响：部分参与者收到了决定，部分没有
- 恢复：协调者重启后重新发送决定给未确认的参与者

### 2.3 参与者故障分析

**场景1：参与者在回复Vote之前故障**
- 处理：协调者等待超时后，视为该参与者投了No，执行Abort

**场景2：参与者在回复Vote Yes之后、收到Commit/Abort之前故障**
- 处理：参与者重启后，查询协调者获取事务决定，然后执行相应操作
- 问题：如果协调者也故障了，参与者将处于不确定状态

**场景3：参与者在收到Commit后、执行提交之前故障**
- 处理：参与者重启后，从Redo日志中恢复并完成提交

### 2.4 2PC的阻塞问题

2PC最大的问题是**阻塞**。当协调者故障时，参与者可能长时间持有锁等待决定：

```
时间线：
T1: 协调者发送Prepare
T2: 参与者A回复Yes，参与者B回复Yes
T3: 协调者决定Commit，但在发送前宕机
T4: 参与者A和B都在等待决定...
    - 它们已经投了Yes，不能自行回滚（可能协调者已经决定Commit）
    - 它们也不能自行提交（可能协调者已经决定Abort）
    - 只能等待协调者恢复
    - 期间持有的锁无法释放，阻塞其他事务
```

### 2.5 2PC的工程实现

**XA协议**是2PC的工业标准实现，被MySQL、PostgreSQL、Oracle等数据库支持：

```sql
-- MySQL XA事务示例
XA START 'txn_001';
UPDATE accounts SET balance = balance - 100 WHERE user_id = 1;
XA END 'txn_001';
XA PREPARE 'txn_001';
-- 等待协调者决定
XA COMMIT 'txn_001';  -- 或 XA ROLLBACK 'txn_001';
```

## 3. 3PC（三阶段提交）

### 3.1 3PC的改进思路

三阶段提交在2PC的基础上增加了一个CanCommit阶段，并引入了超时机制：

**第一阶段：CanCommit**
```
协调者                                    参与者
    |                                      |
    |-------- CanCommit? -------->         |
    |                                      | 检查自身状态（不执行操作）
    |<------- Yes/No -------------         |
```

**第二阶段：PreCommit**
```
协调者                                    参与者
    |                                      |
    |-------- PreCommit --------->         |
    |                                      | 执行事务操作（不提交）
    |<------- Ack ----------------         |
```

**第三阶段：DoCommit**
```
协调者                                    参与者
    |                                      |
    |-------- DoCommit ---------->         |
    |                                      | 正式提交事务
    |<------- Ack ----------------         |
```

### 3.2 3PC相比2PC的改进

1. **引入超时机制**：参与者在PreCommit阶段后如果超时未收到DoCommit，会自动提交（因为能进入PreCommit说明所有参与者都同意了）
2. **降低阻塞概率**：通过CanCommit阶段提前过滤掉不能参与的节点，减少了在持有锁状态下等待的概率

### 3.3 3PC的局限

3PC并没有完全解决问题：
- **网络分区时仍可能不一致**：如果在DoCommit阶段发生网络分区，部分参与者收到了Abort，部分参与者超时后自动Commit，导致数据不一致
- **复杂度增加**：多了一轮通信，延迟更高
- **实际应用少**：由于上述问题，3PC在工业界很少被使用

## 4. TCC（Try-Confirm-Cancel）

### 4.1 TCC的基本思想

TCC是一种业务层面的分布式事务方案，将每个业务操作分为三个步骤：

- **Try**：预留业务资源（冻结而非扣减）
- **Confirm**：确认执行业务操作（使用预留的资源）
- **Cancel**：取消预留的资源

```
电商下单TCC示例：

Try阶段：
  - 订单服务：创建订单，状态为待确认
  - 库存服务：冻结库存（available-1, frozen+1）
  - 账户服务：冻结金额（available-100, frozen+100）

Confirm阶段（所有Try成功）：
  - 订单服务：订单状态改为已确认
  - 库存服务：扣减冻结库存（frozen-1）
  - 账户服务：扣减冻结金额（frozen-100）

Cancel阶段（任何Try失败）：
  - 订单服务：订单状态改为已取消
  - 库存服务：释放冻结库存（frozen-1, available+1）
  - 账户服务：释放冻结金额（frozen-100, available+100）
```

### 4.2 TCC的关键设计要求

**幂等性：** Confirm和Cancel操作必须是幂等的，因为网络问题可能导致重复调用。

```python
def confirm_deduct_inventory(order_id):
    # 幂等检查：如果已经确认过，直接返回成功
    record = db.query("SELECT status FROM tcc_records WHERE order_id = ?", order_id)
    if record and record.status == 'confirmed':
        return True

    # 执行确认操作
    db.execute("UPDATE inventory SET frozen = frozen - 1 WHERE product_id = ?", product_id)
    db.execute("UPDATE tcc_records SET status = 'confirmed' WHERE order_id = ?", order_id)
    return True
```

### 4.3 空回滚问题

**问题描述：** Try请求由于网络原因未到达参与者，但协调者超时后发起了Cancel。参与者收到Cancel请求时，并没有执行过Try，这就是空回滚。

```
时间线：
T1: 协调者发送Try请求给参与者A（网络丢失，未到达）
T2: 协调者超时，认为Try失败
T3: 协调者发送Cancel请求给参与者A
T4: 参与者A收到Cancel，但从未执行过Try
```

**解决方案：** 参与者在Cancel时检查是否执行过Try，如果没有，直接返回成功（空回滚）。

```python
def cancel_deduct_inventory(order_id):
    record = db.query("SELECT * FROM tcc_records WHERE order_id = ?", order_id)
    if record is None:
        # 空回滚：Try未执行，记录一条Cancel记录防止后续悬挂
        db.execute("INSERT INTO tcc_records (order_id, status) VALUES (?, 'cancelled')", order_id)
        return True
    if record.status == 'cancelled':
        return True  # 幂等
    # 正常回滚逻辑
    db.execute("UPDATE inventory SET frozen = frozen - 1, available = available + 1 WHERE product_id = ?", product_id)
    db.execute("UPDATE tcc_records SET status = 'cancelled' WHERE order_id = ?", order_id)
    return True
```

### 4.4 悬挂问题

**问题描述：** Cancel比Try先到达参与者。Cancel执行了空回滚后，迟到的Try请求到达并执行，导致资源被冻结但永远不会被释放。

```
时间线：
T1: 协调者发送Try请求（网络延迟）
T2: 协调者超时，发送Cancel请求
T3: 参与者收到Cancel，执行空回滚
T4: 参与者收到迟到的Try请求并执行 → 资源被冻结，永远无法释放！
```

**解决方案：** Try执行前检查是否已经有Cancel记录，如果有，拒绝执行Try。

```python
def try_deduct_inventory(order_id, product_id):
    record = db.query("SELECT * FROM tcc_records WHERE order_id = ?", order_id)
    if record and record.status == 'cancelled':
        # 已经Cancel过了，拒绝Try（防悬挂）
        return False
    # 正常Try逻辑
    db.execute("UPDATE inventory SET available = available - 1, frozen = frozen + 1 WHERE product_id = ?", product_id)
    db.execute("INSERT INTO tcc_records (order_id, status) VALUES (?, 'trying')", order_id)
    return True
```

### 4.5 TCC的优缺点

**优点：**
- 不依赖数据库的事务机制，适用于任何存储
- 业务灵活性高，可以根据业务特点定制Try/Confirm/Cancel逻辑
- 不会长时间持有数据库锁

**缺点：**
- 业务侵入性强，每个服务都需要实现三个接口
- 开发成本高，需要处理幂等、空回滚、悬挂等问题
- Confirm/Cancel失败时需要重试机制

## 5. Saga模式

### 5.1 Saga的基本思想

Saga模式由Hector Garcia-Molina和Kenneth Salem在1987年提出。核心思想是将一个长事务拆分为多个本地事务，每个本地事务都有对应的补偿事务。如果某个本地事务失败，则按逆序执行之前所有已完成事务的补偿操作。

```
正向流程：T1 → T2 → T3 → T4
补偿流程：C1 ← C2 ← C3（如果T4失败）

其中：
T1: 创建订单        C1: 取消订单
T2: 扣减库存        C2: 恢复库存
T3: 扣减余额        C3: 恢复余额
T4: 增加积分        （T4失败，触发补偿）
```

### 5.2 编排式Saga（Choreography）

每个服务监听事件并决定下一步操作，没有中心协调者。

```
订单服务                库存服务                账户服务                积分服务
    |                      |                      |                      |
    |--订单创建事件-->      |                      |                      |
    |                      |--库存扣减事件-->      |                      |
    |                      |                      |--余额扣减事件-->      |
    |                      |                      |                      |--积分增加事件-->
    |                      |                      |                      |
    |<--------------------- Saga完成 -----------------------------------|
```

**优点：**
- 简单，不需要额外的协调服务
- 服务之间松耦合

**缺点：**
- 流程分散在各个服务中，难以理解和维护
- 服务之间存在循环依赖的风险
- 难以处理复杂的补偿逻辑

### 5.3 协调式Saga（Orchestration）

由一个中心协调器（Saga Orchestrator）负责管理整个Saga的执行流程。

```
                    Saga协调器
                   /    |    \                      /     |     \                订单服务  库存服务  账户服务  积分服务

协调器负责：
1. 按顺序调用各服务
2. 记录每一步的执行状态
3. 失败时按逆序调用补偿操作
4. 处理重试和超时
```

```python
class OrderSagaOrchestrator:
    def __init__(self):
        self.steps = [
            SagaStep(action=self.create_order, compensation=self.cancel_order),
            SagaStep(action=self.deduct_inventory, compensation=self.restore_inventory),
            SagaStep(action=self.deduct_balance, compensation=self.restore_balance),
            SagaStep(action=self.add_points, compensation=self.remove_points),
        ]

    def execute(self, order_data):
        completed_steps = []
        for step in self.steps:
            try:
                step.action(order_data)
                completed_steps.append(step)
            except Exception as e:
                # 失败，按逆序执行补偿
                for completed_step in reversed(completed_steps):
                    try:
                        completed_step.compensation(order_data)
                    except Exception as comp_error:
                        # 补偿失败，记录日志，人工介入
                        log.error(f"补偿失败: {comp_error}")
                raise SagaFailedException(e)
```

**优点：**
- 流程集中管理，易于理解和维护
- 容易添加新步骤或修改流程
- 便于监控和排查问题

**缺点：**
- 协调器是单点，需要保证高可用
- 增加了系统复杂度

### 5.4 补偿事务设计原则

1. **补偿操作必须幂等**：同一个补偿操作可能被执行多次
2. **补偿操作不能失败**：如果补偿操作失败，需要重试直到成功，或者人工介入
3. **补偿是语义上的撤销**：不一定是物理上的回滚。例如，"取消订单"而不是"删除订单记录"
4. **考虑业务可见性**：用户可能已经看到了中间状态，补偿时需要通知用户

## 6. 本地消息表方案

### 6.1 基本原理

本地消息表方案的核心思想是利用本地事务保证业务操作和消息发送的原子性。

```
步骤：
1. 在业务数据库中创建一张消息表
2. 业务操作和消息写入在同一个本地事务中完成
3. 后台任务定期扫描消息表，将未发送的消息发送到消息队列
4. 下游服务消费消息并执行操作
5. 下游服务处理完成后，更新消息状态为已完成
```

### 6.2 详细流程

```sql
-- 步骤1：业务操作和消息写入在同一个事务中
BEGIN;
-- 业务操作
UPDATE accounts SET balance = balance - 100 WHERE user_id = 1;
-- 写入消息表
INSERT INTO local_messages (id, topic, body, status, created_at)
VALUES ('msg_001', 'transfer', '{"from":1,"to":2,"amount":100}', 'NEW', NOW());
COMMIT;
```

```python
# 步骤2：后台定时任务扫描并发送消息
def scan_and_send_messages():
    messages = db.query("SELECT * FROM local_messages WHERE status = 'NEW' AND created_at < NOW() - INTERVAL 5 SECOND")
    for msg in messages:
        try:
            mq.send(msg.topic, msg.body)
            db.execute("UPDATE local_messages SET status = 'SENT' WHERE id = ?", msg.id)
        except Exception as e:
            log.error(f"发送消息失败: {e}")
            # 下次扫描会重试
```

```python
# 步骤3：下游服务消费消息（需要幂等处理）
def handle_transfer_message(msg):
    # 幂等检查
    if db.query("SELECT 1 FROM processed_messages WHERE msg_id = ?", msg.id):
        return  # 已处理过

    db.begin()
    db.execute("UPDATE accounts SET balance = balance + ? WHERE user_id = ?", msg.amount, msg.to_user)
    db.execute("INSERT INTO processed_messages (msg_id) VALUES (?)", msg.id)
    db.commit()
```

### 6.3 优缺点

**优点：**
- 实现简单，不依赖外部组件
- 利用本地事务保证可靠性
- 消息不会丢失

**缺点：**
- 消息表会不断增长，需要定期清理
- 定时扫描有延迟
- 与业务数据库耦合

## 7. 最大努力通知

### 7.1 基本思想

最大努力通知是最简单的分布式事务方案，适用于对一致性要求不高的场景。核心思想是：发送方尽最大努力将通知发送给接收方，如果接收方没有收到，可以主动查询。

### 7.2 典型场景

**支付回调通知：**
```
1. 用户在商户系统下单
2. 商户系统调用支付平台发起支付
3. 用户完成支付
4. 支付平台通知商户系统支付结果（最大努力通知）
   - 第1次通知：立即
   - 第2次通知：5分钟后
   - 第3次通知：30分钟后
   - 第4次通知：2小时后
   - 第5次通知：24小时后
5. 如果所有通知都失败，商户系统可以主动查询支付结果
```

### 7.3 实现要点

```python
class BestEffortNotifier:
    RETRY_INTERVALS = [0, 300, 1800, 7200, 86400]  # 秒

    def notify(self, callback_url, payload):
        for i, interval in enumerate(self.RETRY_INTERVALS):
            time.sleep(interval)
            try:
                response = requests.post(callback_url, json=payload, timeout=5)
                if response.status_code == 200:
                    return True
            except Exception as e:
                log.warning(f"第{i+1}次通知失败: {e}")
        # 所有重试都失败
        log.error(f"通知最终失败: {callback_url}")
        return False
```

### 7.4 与可靠消息的区别

| 特性 | 可靠消息（本地消息表） | 最大努力通知 |
|------|---------------------|-------------|
| 一致性 | 最终一致 | 尽力而为 |
| 主动方 | 发送方保证消息可靠 | 接收方需要主动查询兜底 |
| 适用场景 | 内部系统间 | 跨平台、跨企业 |
| 实现复杂度 | 中等 | 简单 |

## 8. 各方案对比与适用场景

### 8.1 全面对比

| 方案 | 一致性 | 性能 | 业务侵入 | 实现复杂度 | 适用场景 |
|------|--------|------|----------|-----------|---------|
| 2PC | 强一致 | 低 | 低 | 中 | 数据库层面的跨库事务 |
| 3PC | 强一致 | 低 | 低 | 高 | 理论研究，实际少用 |
| TCC | 最终一致 | 高 | 高 | 高 | 资金、库存等核心业务 |
| Saga | 最终一致 | 高 | 中 | 中 | 长流程业务编排 |
| 本地消息表 | 最终一致 | 高 | 中 | 低 | 异步解耦的业务 |
| 最大努力通知 | 弱一致 | 高 | 低 | 低 | 跨平台通知 |

### 8.2 选择建议

```
决策树：

是否需要强一致性？
├── 是 → 能否接受性能损失？
│   ├── 是 → 2PC（XA事务）
│   └── 否 → TCC
└── 否 → 是否是长流程？
    ├── 是 → Saga
    └── 否 → 是否跨平台？
        ├── 是 → 最大努力通知
        └── 否 → 本地消息表
```

### 8.3 实际案例

**案例1：银行转账**
- 方案：TCC
- 原因：资金操作需要高可靠性，TCC可以通过冻结金额实现资源预留

**案例2：电商下单**
- 方案：Saga（协调式）
- 原因：涉及多个服务的长流程，需要灵活的补偿机制

**案例3：订单完成后发送通知**
- 方案：本地消息表
- 原因：通知是异步操作，不需要同步等待结果

**案例4：第三方支付回调**
- 方案：最大努力通知
- 原因：跨平台场景，接收方可以主动查询兜底

## 9. 总结

分布式事务没有银弹。每种方案都是在一致性、可用性、性能和复杂度之间做权衡。在实际工程中，通常会根据业务的重要程度采用不同的方案：核心链路使用TCC或Saga保证数据一致性，非核心链路使用本地消息表或最大努力通知实现最终一致。关键是理解每种方案的原理、优缺点和适用场景，根据实际业务需求做出合理选择。
