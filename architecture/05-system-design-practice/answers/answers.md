# 第五章 系统设计实战 - 习题答案

## 一、选择题

### 1. 答案：B
系统设计的第一步是明确需求和约束条件。包括功能需求（系统要做什么）和非功能需求（QPS、延迟、数据量、可用性等）。不明确需求就开始设计，容易方向跑偏。

### 2. 答案：B
短链服务通常使用Base62编码（a-z, A-Z, 0-9共62个字符）将数字ID转换为短字符串。6位Base62可以表示62^6 ≈ 568亿个短链，足够使用。MD5太长，UUID也太长，自增ID直接暴露了业务信息。

### 3. 答案：C
大V粉丝数可达数千万，如果使用推模式，发一条内容需要写入数千万个收件箱，写扩散严重。推拉结合方案中，大V使用拉模式（只写发件箱），用户查看Feed时实时从大V发件箱拉取。

### 4. 答案：A
"用户可以发布动态"是功能需求。非功能需求是指系统的质量属性，如可用性、性能、可扩展性等。B（可用性）、C（性能）、D（可扩展性）都是非功能需求。

### 5. 答案：B
100万条/天 × 100字节 × 365天 = 36.5GB ≈ 36GB。容量估算是系统设计中的基本功，需要快速估算存储、带宽、QPS等指标。

---

## 二、简答题

### 6. 短链服务请求流程

**完整流程：**
```
1. 用户在浏览器输入短链：https://short.url/abc123
2. 浏览器向短链服务发送HTTP GET请求
3. 短链服务查询缓存（Redis）：
   - 缓存命中 → 直接获取目标URL
   - 缓存未命中 → 查询数据库，将结果写入缓存
4. 短链服务返回HTTP 301/302重定向响应，Location头为目标URL
5. 浏览器根据Location自动跳转到目标URL
```

**可以使用缓存的环节：**
1. **短链→长链映射缓存（Redis）：** 这是最核心的缓存，热门短链的访问频率极高，缓存命中率可达90%+
2. **布隆过滤器：** 在缓存前加一层布隆过滤器，快速判断短链是否存在，过滤无效请求
3. **CDN缓存：** 对于301永久重定向，CDN可以缓存重定向结果，用户请求甚至不需要到达短链服务
4. **本地缓存：** 对于超级热点短链（如营销活动链接），可以在应用层加本地缓存

**301 vs 302的选择：**
- 301（永久重定向）：浏览器会缓存，后续请求不再经过短链服务。适合不需要统计点击量的场景。
- 302（临时重定向）：每次都经过短链服务。适合需要统计点击量、A/B测试的场景。

### 7. 推模式 vs 拉模式

**推模式（Fan-out on Write）：**
- 优点：读操作极快（直接查收件箱）、支持复杂排序
- 缺点：写扩散严重（大V发内容需写入千万收件箱）、存储冗余大、关注/取关维护成本高

**拉模式（Fan-out on Read）：**
- 优点：写操作简单（只写一次）、存储空间小、关注/取关立即生效
- 缺点：读操作慢（需实时聚合多人数据）、关注人数多时性能差

**推拉结合的原因：**
- 纯推模式无法处理大V问题（粉丝千万级的写扩散不可接受）
- 纯拉模式在关注人数多时读性能差
- 推拉结合：普通用户（粉丝<1万）用推模式保证读性能，大V用拉模式避免写扩散。用户查看Feed时合并收件箱数据和大V发件箱数据，兼顾了读写性能。

### 8. 容量估算示例

**日活1000万的社交应用：**

```
基本假设：
  - 日活用户（DAU）：1000万
  - 每用户每天发布0.5条动态
  - 每条动态平均500字节（文字）+ 200KB（图片，存CDN，数据库只存URL）
  - 每用户每天浏览50条动态
  - 读写比：100:1

QPS估算：
  - 写QPS：1000万 × 0.5 / 86400 ≈ 58 QPS（峰值按3倍：174 QPS）
  - 读QPS：1000万 × 50 / 86400 ≈ 5787 QPS（峰值：17361 QPS）

存储估算（一年）：
  - 动态数据：1000万 × 0.5 × 365 × 500B ≈ 912GB ≈ 1TB
  - 图片存储：1000万 × 0.5 × 365 × 200KB ≈ 365TB（CDN/对象存储）
  - 关系数据：1000万用户 × 200关注 × 16B ≈ 32GB

带宽估算：
  - 读带宽：17361 QPS × 500B ≈ 8.7MB/s（文字）
  - 图片带宽：17361 QPS × 200KB ≈ 3.4GB/s（需要CDN分担）
```

---

## 三、设计题

### 9. 评论系统设计

**数据模型：**
```sql
-- 评论表
CREATE TABLE comments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    article_id BIGINT NOT NULL,       -- 文章ID
    user_id BIGINT NOT NULL,          -- 评论者ID
    parent_id BIGINT DEFAULT 0,       -- 父评论ID（0表示顶级评论）
    root_id BIGINT DEFAULT 0,         -- 根评论ID（用于嵌套查询）
    content TEXT NOT NULL,
    like_count INT DEFAULT 0,
    reply_count INT DEFAULT 0,
    created_at DATETIME NOT NULL,
    INDEX idx_article_created (article_id, created_at),
    INDEX idx_article_likes (article_id, like_count),
    INDEX idx_root (root_id, created_at)
);

-- 点赞表（防止重复点赞）
CREATE TABLE comment_likes (
    user_id BIGINT NOT NULL,
    comment_id BIGINT NOT NULL,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (user_id, comment_id)
);
```

**核心API：**
```
POST   /api/v1/articles/{id}/comments          发表评论
GET    /api/v1/articles/{id}/comments?sort=time&cursor=xxx&size=20  获取评论列表
POST   /api/v1/comments/{id}/replies            回复评论
POST   /api/v1/comments/{id}/like               点赞
DELETE /api/v1/comments/{id}/like               取消点赞
```

**缓存策略：**
- 热门文章的前N条评论缓存到Redis（按时间和热度各缓存一份）
- 评论计数缓存：`comment_count:{article_id}` → 评论总数
- 用户点赞状态：`user_likes:{user_id}` → Set（已点赞的评论ID）

**热点文章处理：**
- 写入时：评论先写入消息队列，异步批量写入数据库，避免数据库被打垮
- 读取时：热点文章的评论常驻缓存，设置较长TTL
- 计数：使用Redis INCR原子计数，定期同步到数据库

### 10. 秒杀系统设计

**整体架构：**
```
用户 → CDN（静态页面）→ API网关（限流）→ 秒杀服务 → Redis（库存）→ 消息队列 → 订单服务 → 数据库
```

**库存扣减方案（Redis + Lua脚本）：**
```lua
-- 原子扣减库存
local stock = tonumber(redis.call('get', KEYS[1]))
if stock and stock > 0 then
    redis.call('decr', KEYS[1])
    return 1  -- 扣减成功
else
    return 0  -- 库存不足
end
```

**流量控制策略：**
1. **前端控制：** 按钮点击后置灰，防止重复提交；加入验证码或答题，削峰
2. **网关限流：** 令牌桶限流，只放行一定比例的请求（如库存的10倍）
3. **用户去重：** Redis Set记录已参与的用户ID，同一用户只能抢一次
4. **请求排队：** 通过的请求进入消息队列排队处理

**订单处理流程：**
```
1. 用户点击抢购 → 前端校验（防重复）
2. 请求到达网关 → 限流（令牌桶）
3. 秒杀服务 → 用户去重检查（Redis Set）
4. 秒杀服务 → Redis原子扣减库存（Lua脚本）
5. 扣减成功 → 发送消息到MQ（{user_id, product_id}）
6. 返回"排队中"给用户
7. 订单消费者 → 创建订单 → 写入数据库
8. 用户轮询订单状态 → 返回抢购结果
```

**防刷措施：**
- 同一用户限购1件（Redis Set）
- 同一IP限制请求频率
- 验证码/滑块验证
- 风控系统识别异常行为（如请求间隔过于规律）
