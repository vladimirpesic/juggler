use anyhow::Result;
use juggler_cli::cli::cli;

#[tokio::main]
async fn main() -> Result<()> {
    cli().await
}
