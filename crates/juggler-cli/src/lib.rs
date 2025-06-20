use etcetera::AppStrategyArgs;
use once_cell::sync::Lazy;
pub mod cli;
pub mod commands;
pub mod logging;
pub mod project_tracker;
pub mod recipes;
pub mod session;
pub mod signal;
// Re-export commonly used types
pub use session::Session;

pub static APP_STRATEGY: Lazy<AppStrategyArgs> = Lazy::new(|| AppStrategyArgs {
    top_level_domain: "vladimirpesic".to_string(),
    author: "vladimirpesic".to_string(),
    app_name: "juggler".to_string(),
});
