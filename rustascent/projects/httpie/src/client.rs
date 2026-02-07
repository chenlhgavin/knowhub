use anyhow::Result;
use reqwest::{Client, Response};

use crate::cli::ParsedRequest;

/// Build and send an HTTP request based on parsed CLI arguments
pub async fn send(req: &ParsedRequest) -> Result<Response> {
    let client = Client::builder().user_agent("httpie/0.1.0").build()?;

    let mut builder = client.request(req.method.clone(), &req.url);

    // Set custom headers
    for (key, value) in &req.headers {
        builder = builder.header(key.as_str(), value.as_str());
    }

    // Set URL query parameters
    if !req.query_params.is_empty() {
        builder = builder.query(&req.query_params);
    }

    // Set JSON body (also sets Content-Type: application/json automatically)
    if let Some(body) = &req.body {
        builder = builder.json(body);
    }

    let response = builder.send().await?;
    Ok(response)
}
