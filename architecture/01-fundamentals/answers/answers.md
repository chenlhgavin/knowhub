# 第一章 基础知识 - 习题答案

## 一、选择题

### 1. 答案：B
Go的GC是基于三色标记-清除算法的并发GC。Java使用的是分代GC（不是引用计数），Python使用引用计数+分代GC，Go的GC在1.8之后STW时间已经控制在亚毫秒级别。

### 2. 答案：B
LRU缓存需要O(1)的查找和O(1)的插入/删除。哈希表提供O(1)查找，双向链表提供O(1)的头尾操作和任意位置删除。两者结合是实现LRU的经典方案。

### 3. 答案：D
B+树的非叶子节点只存储索引键，不存储完整数据记录。所有数据都存储在叶子节点中。这使得非叶子节点可以容纳更多的键，降低树的高度，减少磁盘I/O。

### 4. 答案：B
一致性哈希的核心优势是当节点增减时，只需要迁移少量数据（约1/N），而传统哈希取模方式在节点变化时几乎所有数据都需要重新分配。

### 5. 答案：A
正确的时间复杂度排序：O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ)。这是从常数时间到指数时间的递增顺序。

---

## 二、简答题

### 6. 协程与线程的区别

**协程（Coroutine）** 是一种用户态的轻量级线程，由程序自身调度，而非操作系统调度。

| 特性 | 线程 | 协程 |
|------|------|------|
| 调度方 | 操作系统内核 | 用户程序/运行时 |
| 切换开销 | 大（内核态切换） | 小（用户态切换） |
| 内存占用 | 通常1-8MB栈空间 | 通常几KB |
| 并发数量 | 数千级 | 数十万级 |
| 是否抢占 | 抢占式 | 协作式（Go 1.14后支持抢占） |

**Go的goroutine：**
- 由Go运行时调度，使用GMP模型（Goroutine-Machine-Processor）
- 初始栈只有2KB，可动态增长
- 通过channel进行通信（CSP模型）
- Go 1.14引入了基于信号的抢占式调度

**Python的asyncio：**
- 基于事件循环（Event Loop）的单线程协程
- 使用async/await语法
- 协作式调度，遇到await时主动让出控制权
- 适合I/O密集型任务，不适合CPU密集型

### 7. 哈希冲突处理

**链地址法（Chaining）：**
```
索引0 → [K1,V1] → [K5,V5] → null
索引1 → [K2,V2] → null
索引2 → [K3,V3] → [K7,V7] → [K9,V9] → null
索引3 → null
索引4 → [K4,V4] → null
```
- 优点：实现简单，删除方便，负载因子可以大于1
- 缺点：链表过长时查找退化为O(n)，缓存不友好

**开放寻址法（Open Addressing）：**
```
索引0: [K1,V1]
索引1: [K2,V2]
索引2: [K5,V5]  ← K5哈希到索引0，冲突后探测到索引2
索引3: [K3,V3]
索引4: 空
```
- 优点：缓存友好（数据连续存储），无额外指针开销
- 缺点：删除复杂（需要标记删除），负载因子不能太高（通常<0.75），容易产生聚集

### 8. 跳表原理及Redis选择跳表的原因

**跳表原理：** 在有序链表的基础上增加多级索引。底层是完整的有序链表，每一层是下一层的"快速通道"，通过随机化决定每个节点的层数。

```
Level 3:  1 ─────────────────────── 9
Level 2:  1 ────── 4 ────────────── 9
Level 1:  1 ── 3 ─ 4 ── 6 ── 7 ── 9
Level 0:  1  2  3  4  5  6  7  8  9
```

查找时从最高层开始，逐层下降，平均时间复杂度O(log n)。

**Redis选择跳表而非红黑树的原因：**
1. 实现简单：跳表的代码比红黑树简单得多，易于调试和维护
2. 范围查询高效：跳表的底层是有序链表，范围查询只需遍历链表；红黑树需要中序遍历
3. 插入/删除简单：跳表只需修改相邻指针；红黑树需要旋转和重新着色
4. 内存局部性相当：在实际使用中，跳表和红黑树的性能差异不大

---

## 三、设计题

### 9. 内存分配器设计

**设计思路：**

1. **空闲块管理：** 使用空闲链表（Free List）记录所有空闲内存块。每个空闲块的头部存储块大小和指向下一个空闲块的指针。

2. **分配策略：**
   - 首次适配（First Fit）：遍历空闲链表，找到第一个足够大的块。速度快，但容易产生外部碎片。
   - 最佳适配（Best Fit）：找到最小的足够大的块。减少浪费，但遍历慢，容易产生大量小碎片。
   - 最差适配（Worst Fit）：找到最大的块。避免小碎片，但大块很快被用完。

3. **碎片处理：**
   - 合并相邻空闲块：释放内存时检查前后是否有相邻的空闲块，如果有则合并
   - 内存对齐：按8字节或16字节对齐，减少碎片
   - 分级分配：不同大小的请求使用不同的空闲链表（类似slab分配器）

```python
class Block:
    def __init__(self, start, size, is_free=True):
        self.start = start
        self.size = size
        self.is_free = is_free

class MemoryAllocator:
    def __init__(self, total_size):
        self.blocks = [Block(0, total_size, True)]

    def allocate(self, size):
        # 首次适配
        for block in self.blocks:
            if block.is_free and block.size >= size:
                if block.size > size:
                    # 分割块
                    new_block = Block(block.start + size, block.size - size, True)
                    block.size = size
                    self.blocks.insert(self.blocks.index(block) + 1, new_block)
                block.is_free = False
                return block.start
        return None  # 内存不足

    def free(self, ptr):
        for i, block in enumerate(self.blocks):
            if block.start == ptr:
                block.is_free = True
                self._merge_adjacent(i)
                return

    def _merge_adjacent(self, index):
        # 向后合并
        while index + 1 < len(self.blocks) and self.blocks[index + 1].is_free:
            self.blocks[index].size += self.blocks[index + 1].size
            self.blocks.pop(index + 1)
        # 向前合并
        while index > 0 and self.blocks[index - 1].is_free:
            self.blocks[index - 1].size += self.blocks[index].size
            self.blocks.pop(index)
            index -= 1
```

### 10. 一致性哈希实现

```python
import hashlib
from bisect import bisect_right

class ConsistentHash:
    def __init__(self, virtual_nodes=150):
        self.virtual_nodes = virtual_nodes
        self.ring = {}          # hash值 → 物理节点
        self.sorted_keys = []   # 排序后的hash值

    def _hash(self, key):
        md5 = hashlib.md5(key.encode()).hexdigest()
        return int(md5, 16)

    def add_node(self, node):
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}#VN{i}"
            hash_val = self._hash(virtual_key)
            self.ring[hash_val] = node
            self.sorted_keys.append(hash_val)
        self.sorted_keys.sort()

    def remove_node(self, node):
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}#VN{i}"
            hash_val = self._hash(virtual_key)
            if hash_val in self.ring:
                del self.ring[hash_val]
                self.sorted_keys.remove(hash_val)

    def get_node(self, key):
        if not self.ring:
            return None
        hash_val = self._hash(key)
        # 找到第一个大于等于hash_val的位置
        idx = bisect_right(self.sorted_keys, hash_val)
        if idx == len(self.sorted_keys):
            idx = 0  # 环形，回到起点
        return self.ring[self.sorted_keys[idx]]

# 使用示例
ch = ConsistentHash(virtual_nodes=150)
ch.add_node("server-1")
ch.add_node("server-2")
ch.add_node("server-3")

print(ch.get_node("user:1001"))  # 返回某个server
print(ch.get_node("user:1002"))  # 返回某个server

# 添加新节点后，大部分key的映射不变
ch.add_node("server-4")
print(ch.get_node("user:1001"))  # 大概率不变
```
