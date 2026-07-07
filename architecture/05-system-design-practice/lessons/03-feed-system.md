# 实战案例：信息流系统设计

## 一、需求分析

### 1.1 什么是信息流

信息流（Feed）是社交产品的核心功能，用户可以看到自己关注的人发布的内容，按时间或算法排序。

```
典型产品：
  - 微博：关注的人的微博动态
  - 微信朋友圈：好友的动态
  - Twitter/X：关注的人的推文
  - Instagram：关注的人的图片/视频
  - 抖音：推荐视频流（算法推荐型）
```

### 1.2 核心功能

```
基本功能：
  1. 发布内容（Post）
  2. 关注/取消关注用户（Follow/Unfollow）
  3. 查看信息流（Feed）
  4. 互动（点赞、评论、转发）

非功能需求：
  - 用户量：1亿注册用户，1000万日活
  - 关注关系：平均每人关注200人，大V粉丝可达数千万
  - 发布量：每天500万条新内容
  - 读写比：读远大于写（100:1）
  - 延迟要求：Feed加载 < 500ms
```

### 1.3 难点分析

```
核心挑战：
  1. 读扩散 vs 写扩散的选择
  2. 大V发布内容时的扇出问题（粉丝数千万）
  3. Feed的实时性与性能的平衡
  4. 海量数据的存储与查询
```

---

## 二、Feed流的两种模型

### 2.1 拉模式（Pull / Fan-out on Read）

用户查看Feed时，实时从关注的人的发件箱中拉取内容并合并排序。

```
数据模型：
  发件箱表（Outbox）：
    user_id | post_id | content | created_at
    --------|---------|---------|------------
    用户A   | 001     | ...     | 10:00
    用户A   | 002     | ...     | 10:30
    用户B   | 003     | ...     | 10:15

查看Feed流程：
  1. 获取当前用户的关注列表：[用户A, 用户B, 用户C, ...]
  2. 从每个关注用户的发件箱中获取最新N条内容
  3. 合并排序，取Top N返回

SQL示意：
  SELECT * FROM posts
  WHERE user_id IN (关注列表)
  ORDER BY created_at DESC
  LIMIT 20
```

```
优点：
  - 写操作简单，发布内容只写一次
  - 存储空间小，不需要冗余数据
  - 关注/取消关注立即生效

缺点：
  - 读操作慢，需要实时聚合多个用户的数据
  - 关注人数多时，查询性能差
  - 难以支持复杂的排序算法
```

### 2.2 推模式（Push / Fan-out on Write）

用户发布内容时，将内容推送到所有粉丝的收件箱中。

```
数据模型：
  收件箱表（Inbox / Timeline）：
    owner_id | post_id | author_id | created_at
    ---------|---------|-----------|------------
    用户X    | 001     | 用户A     | 10:00
    用户X    | 003     | 用户B     | 10:15
    用户X    | 002     | 用户A     | 10:30

发布内容流程：
  1. 将内容写入发件箱
  2. 获取粉丝列表
  3. 将内容ID写入每个粉丝的收件箱

查看Feed流程：
  1. 直接从当前用户的收件箱读取
  SELECT * FROM inbox WHERE owner_id = 当前用户 ORDER BY created_at DESC LIMIT 20
```

```
优点：
  - 读操作极快，直接查询收件箱
  - 支持复杂排序（写入时就可以计算排序分数）

缺点：
  - 写扩散严重：大V发一条内容需要写入数千万粉丝的收件箱
  - 存储空间大：每条内容被冗余存储N份
  - 关注/取消关注需要维护收件箱
  - 发布延迟高（需要等待扇出完成）
```

### 2.3 推拉结合（Hybrid）

实际系统通常采用推拉结合的方案。

```
策略：
  - 普通用户（粉丝 < 1000）：推模式
    发布时直接推送到所有粉丝收件箱

  - 大V用户（粉丝 > 10000）：拉模式
    发布时只写入发件箱，不推送

  - 用户查看Feed时：
    1. 从收件箱读取普通用户推送的内容
    2. 从关注的大V的发件箱拉取最新内容
    3. 合并排序返回

阈值设定：
  粉丝数 < 1000  → 纯推
  1000 < 粉丝数 < 10000 → 推（可配置）
  粉丝数 > 10000 → 纯拉
```

```python
class FeedService:
    def publish(self, author_id, post):
        # 写入发件箱
        self.outbox.add(author_id, post)

        follower_count = self.get_follower_count(author_id)
        if follower_count < 10000:
            # 普通用户：推模式
            followers = self.get_followers(author_id)
            for follower_id in followers:
                self.inbox.add(follower_id, post)
        # 大V不推送，读取时拉取

    def get_feed(self, user_id, page_size=20):
        # 1. 从收件箱获取推送的内容
        pushed_posts = self.inbox.get_latest(user_id, page_size)

        # 2. 获取关注的大V列表
        big_v_list = self.get_followed_big_v(user_id)

        # 3. 从大V的发件箱拉取
        pulled_posts = []
        for v_id in big_v_list:
            posts = self.outbox.get_latest(v_id, 5)
            pulled_posts.extend(posts)

        # 4. 合并排序
        all_posts = pushed_posts + pulled_posts
        all_posts.sort(key=lambda p: p.created_at, reverse=True)
        return all_posts[:page_size]
```

---

## 三、存储设计

### 3.1 数据模型

```
用户表（MySQL）：
  users: id, name, avatar, follower_count, following_count

关注关系表（MySQL + Redis）：
  follows: follower_id, following_id, created_at
  索引：(follower_id, following_id), (following_id)

  Redis缓存：
    following:{user_id} → Set（关注列表）
    followers:{user_id} → Set（粉丝列表，仅普通用户缓存）

内容表（MySQL）：
  posts: id, author_id, content, media_urls, created_at
  索引：(author_id, created_at)

收件箱（Redis Sorted Set）：
  inbox:{user_id} → Sorted Set
    member: post_id
    score: timestamp

  ZADD inbox:user123 1704067200 "post_001"
  ZREVRANGE inbox:user123 0 19  # 获取最新20条
```

### 3.2 收件箱的存储优化

```
问题：每个用户的收件箱不能无限增长

解决方案：
  1. 只保留最近N条（如1000条）
     ZADD inbox:user123 timestamp post_id
     ZREMRANGEBYRANK inbox:user123 0 -(N+1)  # 删除最旧的

  2. 设置过期时间
     只保留最近7天的数据
     ZREMRANGEBYSCORE inbox:user123 0 (now - 7days)

  3. 冷热分离
     热数据（7天内）：Redis
     温数据（7-30天）：MySQL/HBase
     冷数据（30天以上）：对象存储/归档
```

### 3.3 内容存储

```
短内容（文字为主，如微博）：
  MySQL + Redis缓存
  热点内容缓存到Redis

长内容（图片、视频）：
  元数据：MySQL
  媒体文件：对象存储（S3/OSS）
  CDN加速分发

内容缓存策略：
  - 新发布的内容：写入缓存，TTL 24小时
  - 热点内容：延长TTL，或永不过期
  - 冷内容：不缓存，从数据库读取
```

---

## 四、关键技术方案

### 4.1 异步扇出

```
发布内容时的扇出不应该同步执行，应该通过消息队列异步处理。

发布流程：
  1. 用户发布内容 → API服务
  2. API服务写入内容表 → 返回成功
  3. API服务发送消息到MQ：{post_id, author_id}
  4. 扇出消费者：
     a. 获取粉丝列表
     b. 分批写入粉丝收件箱
     c. 每批1000个粉丝，避免单次操作过大

消费者伪代码：
  def fan_out(post_id, author_id):
      followers = get_followers(author_id)
      batch_size = 1000
      for i in range(0, len(followers), batch_size):
          batch = followers[i:i+batch_size]
          pipeline = redis.pipeline()
          for follower_id in batch:
              pipeline.zadd(f"inbox:{follower_id}", {post_id: timestamp})
          pipeline.execute()
```

### 4.2 Feed分页

```
基于游标的分页（推荐）：

  第一页：ZREVRANGEBYSCORE inbox:user123 +inf -inf LIMIT 0 20
  返回：[post_20, post_19, ..., post_1]
  游标：post_1的score（timestamp）

  第二页：ZREVRANGEBYSCORE inbox:user123 (cursor -inf LIMIT 0 20
  返回：[post_40, post_39, ..., post_21]

  优点：
  - 不受新内容插入的影响（不会重复或遗漏）
  - 性能稳定

  注意：
  - 使用开区间 ( 避免重复
  - 如果多条内容时间戳相同，需要用 post_id 作为辅助排序
```

### 4.3 缓存预热与降级

```
缓存预热：
  - 用户登录时，异步预加载Feed到缓存
  - 活跃用户的收件箱常驻缓存
  - 不活跃用户的收件箱按需加载

降级策略：
  - Redis不可用时：降级为纯拉模式，从数据库查询
  - 扇出延迟过高时：暂停推送，用户查看时实时拉取
  - 大促期间：关闭非核心功能（如"可能认识的人"推荐）
```

---

## 五、扩展话题

### 5.1 算法排序Feed

```
时间线排序 vs 算法排序：

时间线排序：
  按发布时间倒序，简单直观
  用户可能错过重要内容

算法排序：
  综合多个因素计算排序分数：
  score = w1 * 时效性 + w2 * 互动量 + w3 * 用户兴趣 + w4 * 内容质量

  因素包括：
  - 内容发布时间（时效性衰减）
  - 点赞、评论、转发数量
  - 用户与作者的互动频率
  - 内容类型偏好
  - 内容质量分（AI评估）
```

### 5.2 实时性优化

```
长轮询（Long Polling）：
  客户端发起请求，服务端hold住连接
  有新内容时立即返回，否则超时后返回空

WebSocket：
  建立持久连接，服务端主动推送新内容
  适合对实时性要求高的场景

Server-Sent Events（SSE）：
  服务端单向推送，比WebSocket轻量
  适合Feed更新通知

实际方案：
  - 在线用户：WebSocket推送新内容提醒（"有N条新动态"）
  - 用户点击刷新时：拉取最新Feed
  - 离线用户：下次打开App时拉取
```

---

## 六、架构总结

```
完整架构：

  客户端 → API网关 → Feed服务 → Redis（收件箱）
                              → MySQL（内容、关系）
                              → 消息队列（异步扇出）
                                    ↓
                              扇出消费者 → Redis（写入收件箱）

  关键设计决策：
  1. 推拉结合：普通用户推，大V拉
  2. 异步扇出：通过消息队列异步推送
  3. 收件箱用Redis Sorted Set存储
  4. 游标分页避免重复和遗漏
  5. 冷热分离降低存储成本

  容量估算（1000万日活）：
  - 收件箱：1000万 × 1000条 × 8字节 ≈ 80GB Redis
  - 内容缓存：500万条/天 × 1KB ≈ 5GB/天
  - 扇出消息：500万条 × 平均200粉丝 = 10亿次写入/天
```
