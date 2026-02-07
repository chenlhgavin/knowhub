mod cli;
mod client;
mod output;

use anyhow::Result;

#[tokio::main]
async fn main() {
    if let Err(err) = run().await {
        eprintln!("httpie: error: {err:#}");
        std::process::exit(1);
    }
}

async fn run() -> Result<()> {
    let request = cli::parse()?;
    let response = client::send(&request).await?;
    output::print(response).await?;
    Ok(())
}
