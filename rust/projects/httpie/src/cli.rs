use anyhow::{anyhow, Result};
use clap::Parser;
use reqwest::Method;

/// A Rust implementation of HTTPie - modern, user-friendly HTTP client
#[derive(Parser, Debug)]
#[command(name = "httpie", version, about)]
pub struct Args {
    /// [METHOD] URL [REQUEST_ITEMS...]
    ///
    /// METHOD: HTTP method (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS).
    ///         If omitted, defaults to GET (no data) or POST (with data).
    ///
    /// URL: The request URL. "http://" is prepended if no scheme is given.
    ///
    /// REQUEST_ITEMS:
    ///   Header:Value  - HTTP header
    ///   key=value     - JSON body field (string value)
    ///   key==value    - URL query parameter
    #[arg(required = true, num_args = 1..)]
    raw_args: Vec<String>,
}

/// Parsed and validated HTTP request ready to send
pub struct ParsedRequest {
    pub method: Method,
    pub url: String,
    pub headers: Vec<(String, String)>,
    pub body: Option<serde_json::Value>,
    pub query_params: Vec<(String, String)>,
}

/// Classified request item
enum RequestItem {
    Header(String, String),
    Data(String, String),
    Query(String, String),
}

/// Check if a string is a known HTTP method
fn is_method(s: &str) -> bool {
    matches!(
        s.to_uppercase().as_str(),
        "GET" | "POST" | "PUT" | "DELETE" | "PATCH" | "HEAD" | "OPTIONS" | "TRACE" | "CONNECT"
    )
}

/// Normalize a URL: add scheme if missing, expand :port shorthand
fn normalize_url(raw: &str) -> String {
    if raw.starts_with("://") {
        format!("http{raw}")
    } else if raw.starts_with(':') {
        format!("http://localhost{raw}")
    } else if !raw.contains("://") {
        format!("http://{raw}")
    } else {
        raw.to_string()
    }
}

/// Parse a single request item string into its type
///
/// Priority: `==` → first of `=` or `:` → error
fn parse_item(item: &str) -> Result<RequestItem> {
    // 1. Query parameter: key==value
    if let Some(pos) = item.find("==") {
        let key = &item[..pos];
        let value = &item[pos + 2..];
        return Ok(RequestItem::Query(key.to_string(), value.to_string()));
    }

    // 2. Find first `=` and first `:`, whichever comes first wins
    let eq_pos = item.find('=');
    let colon_pos = item.find(':');

    match (eq_pos, colon_pos) {
        // Both found: the one that appears first wins
        (Some(ep), Some(cp)) if cp < ep => Ok(RequestItem::Header(
            item[..cp].to_string(),
            item[cp + 1..].to_string(),
        )),
        (Some(ep), _) => Ok(RequestItem::Data(
            item[..ep].to_string(),
            item[ep + 1..].to_string(),
        )),
        (None, Some(cp)) => Ok(RequestItem::Header(
            item[..cp].to_string(),
            item[cp + 1..].to_string(),
        )),
        (None, None) => Err(anyhow!(
            "无法解析请求项: '{item}'\n有效格式: Header:Value, key=value, key==value"
        )),
    }
}

/// Parse CLI arguments into a validated request
pub fn parse() -> Result<ParsedRequest> {
    let args = Args::parse();
    let raw = &args.raw_args;

    if raw.is_empty() {
        return Err(anyhow!("缺少 URL 参数"));
    }

    // Determine method, URL, and request items
    let (method_str, url_raw, items) = if raw.len() == 1 {
        (None, raw[0].as_str(), &raw[1..])
    } else if is_method(&raw[0]) {
        (Some(raw[0].as_str()), raw[1].as_str(), &raw[2..])
    } else {
        (None, raw[0].as_str(), &raw[1..])
    };

    // Parse each request item
    let mut headers = Vec::new();
    let mut data = serde_json::Map::new();
    let mut query_params = Vec::new();

    for item_str in items {
        match parse_item(item_str)? {
            RequestItem::Header(k, v) => headers.push((k, v)),
            RequestItem::Data(k, v) => {
                data.insert(k, serde_json::Value::String(v));
            }
            RequestItem::Query(k, v) => query_params.push((k, v)),
        }
    }

    let has_data = !data.is_empty();

    // Infer method: has data → POST, otherwise → GET
    let method = match method_str {
        Some(m) => m
            .to_uppercase()
            .parse::<Method>()
            .map_err(|_| anyhow!("无效的 HTTP 方法: {m}"))?,
        None => {
            if has_data {
                Method::POST
            } else {
                Method::GET
            }
        }
    };

    let url = normalize_url(url_raw);
    let body: Option<serde_json::Value> = if has_data {
        Some(serde_json::Value::Object(data))
    } else {
        None
    };

    Ok(ParsedRequest {
        method,
        url,
        headers,
        body,
        query_params,
    })
}
