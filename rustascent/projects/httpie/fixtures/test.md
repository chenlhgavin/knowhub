# httpie 测试用例

## 1. CLI 解析 (`cli.rs`)

### 1.1 normalize_url

| 输入 | 期望输出 | 说明 |
|------|----------|------|
| `example.com` | `http://example.com` | 无 scheme，补 http |
| `example.com/api/v1` | `http://example.com/api/v1` | 带路径，补 http |
| `https://example.com` | `https://example.com` | 已有 https，保持不变 |
| `http://example.com` | `http://example.com` | 已有 http，保持不变 |
| `://example.com` | `http://example.com` | scheme 缺省简写 |
| `:3000` | `http://localhost:3000` | 端口简写，补 localhost |
| `:3000/api` | `http://localhost:3000/api` | 端口简写带路径 |
| `:8080/a/b?x=1` | `http://localhost:8080/a/b?x=1` | 端口简写带路径和查询参数 |
| `localhost:8080` | `http://localhost:8080` | 无 scheme 带端口 |
| `192.168.1.1:9090` | `http://192.168.1.1:9090` | IP 地址 |

### 1.2 is_method

| 输入 | 期望 | 说明 |
|------|------|------|
| `GET` | true | 大写 |
| `get` | true | 小写 |
| `Post` | true | 混合大小写 |
| `PUT` | true | |
| `DELETE` | true | |
| `PATCH` | true | |
| `HEAD` | true | |
| `OPTIONS` | true | |
| `TRACE` | true | |
| `CONNECT` | true | |
| `example.com` | false | URL 不是方法 |
| `name=value` | false | 请求项不是方法 |
| `GE` | false | 不完整的方法名 |
| `GETT` | false | 多余字符 |
| `` (空字符串) | false | 空字符串 |

### 1.3 parse_item

#### 正常解析

| 输入 | 期望类型 | key | value | 说明 |
|------|----------|-----|-------|------|
| `Content-Type:application/json` | Header | `Content-Type` | `application/json` | 标准 header |
| `Authorization:Bearer token123` | Header | `Authorization` | `Bearer token123` | value 含空格 |
| `X-Empty:` | Header | `X-Empty` | `` (空) | 空 value 的 header |
| `name=hello` | Data | `name` | `hello` | 基本键值对 |
| `msg=hello world` | Data | `msg` | `hello world` | value 含空格 |
| `key=` | Data | `key` | `` (空) | 空 value |
| `page==2` | Query | `page` | `2` | 查询参数 |
| `q==rust lang` | Query | `q` | `rust lang` | 查询参数含空格 |
| `filter==` | Query | `filter` | `` (空) | 空 value 查询参数 |

#### 优先级测试

| 输入 | 期望类型 | key | value | 说明 |
|------|----------|-----|-------|------|
| `X-Token:abc=def` | Header | `X-Token` | `abc=def` | `:` 在 `=` 前，识别为 Header |
| `key=val:ue` | Data | `key` | `val:ue` | `=` 在 `:` 前，识别为 Data |
| `a==b:c` | Query | `a` | `b:c` | `==` 最高优先级 |
| `a==b=c` | Query | `a` | `b=c` | `==` 最高优先级 |
| `a:b==c` | Query | `a:b` | `c` | `==` 最高优先级，即使有 `:` |

#### 错误情况

| 输入 | 期望 | 说明 |
|------|------|------|
| `noseparator` | Err | 无分隔符 |
| `justtext` | Err | 纯文本 |
| `` (空字符串) | Err | 空字符串 |

### 1.4 方法推断

| raw_args | 期望 method | 期望 URL | 说明 |
|----------|-------------|----------|------|
| `["example.com"]` | GET | `http://example.com` | 无 data，默认 GET |
| `["example.com", "name=val"]` | POST | `http://example.com` | 有 data，默认 POST |
| `["GET", "example.com"]` | GET | `http://example.com` | 显式 GET |
| `["POST", "example.com"]` | POST | `http://example.com` | 显式 POST 无 body |
| `["PUT", "example.com", "k=v"]` | PUT | `http://example.com` | 显式 PUT + body |
| `["DELETE", "example.com"]` | DELETE | `http://example.com` | 显式 DELETE |
| `["patch", "example.com", "k=v"]` | PATCH | `http://example.com` | 小写方法名 |
| `["example.com", "page==1"]` | GET | `http://example.com` | query 不算 data，默认 GET |
| `["example.com", "X-Auth:tok"]` | GET | `http://example.com` | header 不算 data，默认 GET |
| `["example.com", "page==1", "k=v"]` | POST | `http://example.com` | 混合 query + data，有 data 则 POST |

### 1.5 综合解析

| raw_args | method | url | headers | body | query |
|----------|--------|-----|---------|------|-------|
| `["httpbin.org/get"]` | GET | `http://httpbin.org/get` | [] | None | [] |
| `["POST", "httpbin.org/post", "name=rust", "lang=zh"]` | POST | `http://httpbin.org/post` | [] | `{"name":"rust","lang":"zh"}` | [] |
| `["httpbin.org/get", "page==1", "limit==10"]` | GET | `http://httpbin.org/get` | [] | None | [("page","1"),("limit","10")] |
| `["PUT", ":3000/api", "id=1", "X-Token:abc"]` | PUT | `http://localhost:3000/api` | [("X-Token","abc")] | `{"id":"1"}` | [] |
| `["https://api.example.com", "Authorization:Bearer t", "q==test", "name=foo"]` | POST | `https://api.example.com` | [("Authorization","Bearer t")] | `{"name":"foo"}` | [("q","test")] |

---

## 2. 输出格式化 (`output.rs`)

### 2.1 is_json

| 输入 | 期望 | 说明 |
|------|------|------|
| `application/json` | true | 标准 JSON |
| `application/json; charset=utf-8` | true | 带 charset |
| `application/vnd.api+json` | true | JSON API 规范 |
| `application/problem+json` | true | RFC 7807 |
| `text/html` | false | HTML |
| `text/plain` | false | 纯文本 |
| `application/xml` | false | XML |
| `image/png` | false | 图片 |
| `` (空字符串) | false | 空 |

### 2.2 format_version

| 输入 | 期望 |
|------|------|
| `HTTP_09` | `HTTP/0.9` |
| `HTTP_10` | `HTTP/1.0` |
| `HTTP_11` | `HTTP/1.1` |
| `HTTP_2` | `HTTP/2` |
| `HTTP_3` | `HTTP/3` |

### 2.3 colorize_json

| 输入 JSON | 验证点 |
|-----------|--------|
| `{}` | 包含 `{` 和 `}` |
| `{"key": "value"}` | key 被 cyan 着色，value 被 green 着色 |
| `{"n": 42}` | 数字被 magenta 着色 |
| `{"n": -3.14}` | 负小数被 magenta 着色 |
| `{"n": 1e10}` | 科学记数法被 magenta 着色 |
| `{"b": true}` | true 被 yellow 着色 |
| `{"b": false}` | false 被 yellow 着色 |
| `{"x": null}` | null 被 red 着色 |
| `{"a": "he said \"hi\""}` | 转义引号不截断字符串 |
| `{"a": 1, "b": "x", "c": true, "d": null}` | 混合类型各自正确着色 |
| `{"nested": {"inner": [1, 2, 3]}}` | 嵌套结构正确处理 |
| `[]` | 空数组不报错 |
| `[1, "two", true, null]` | 数组内各类型正确着色 |

---

## 3. HTTP 客户端 (`client.rs`)

### 3.1 请求构建

| 场景 | 验证点 |
|------|--------|
| 基本 GET | User-Agent 为 `httpie/0.1.0` |
| 带 headers | 请求头正确设置 |
| 带 query_params | URL query string 正确拼接 |
| 带 body | Content-Type 自动设为 `application/json`，body 为 JSON |
| 无 body 的 POST | 不设置 Content-Type 和 body |

### 3.2 错误场景

| 场景 | 期望 |
|------|------|
| 不存在的域名 | 返回 DNS 解析错误 |
| 连接超时 | 返回连接错误 |
| 无效 URL (如 `http://`) | 返回 URL 解析错误 |

---

## 4. 集成测试（命令行）

```bash
# 4.1 基本 GET
cargo run -- httpbin.org/get
# 期望: 200 OK，JSON 响应

# 4.2 GET + query 参数
cargo run -- httpbin.org/get page==1 limit==10
# 期望: 200 OK，响应中 args 包含 {"page": "1", "limit": "10"}

# 4.3 自动推断 POST
cargo run -- httpbin.org/post name=rust version=1.93
# 期望: 200 OK，响应中 json 包含 {"name": "rust", "version": "1.93"}

# 4.4 显式 PUT + header + body
cargo run -- PUT httpbin.org/put X-Custom:myvalue name=test
# 期望: 200 OK，响应中 headers 含 X-Custom，json 含 name

# 4.5 显式 DELETE
cargo run -- DELETE httpbin.org/delete
# 期望: 200 OK

# 4.6 PATCH
cargo run -- PATCH httpbin.org/patch status=active
# 期望: 200 OK，响应中 json 含 status

# 4.7 localhost 端口简写
cargo run -- :8080/health
# 期望: 请求发往 http://localhost:8080/health

# 4.8 HTTPS
cargo run -- https://httpbin.org/get
# 期望: 200 OK，scheme 保持 https

# 4.9 自定义多个 headers
cargo run -- httpbin.org/headers Accept:text/plain X-Request-Id:abc123
# 期望: 响应中 headers 包含对应值

# 4.10 混合 header + query + body
cargo run -- POST httpbin.org/post Authorization:Bearer\ tok q==search name=test
# 期望: header、query、body 各自正确

# 4.11 错误 - 无效请求项
cargo run -- httpbin.org/get noseparator
# 期望: 报错 "无法解析请求项"

# 4.12 错误 - 不存在的域名
cargo run -- nonexistent.invalid/path
# 期望: 报错，DNS 解析失败

# 4.13 非 JSON 响应
cargo run -- httpbin.org/html
# 期望: 输出 HTML 原文，不做 JSON 格式化

# 4.14 HEAD 方法
cargo run -- HEAD httpbin.org/get
# 期望: 只输出状态行和 headers，无 body

# 4.15 重定向
cargo run -- httpbin.org/redirect/1
# 期望: reqwest 默认跟随重定向，返回最终 200
```
