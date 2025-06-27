use std::env;
use std::path::Path;
use std::sync::Arc;
use std::sync::OnceLock;

use super::utils::verify_secret_key;
use crate::state::AppState;
use axum::{extract::State, routing::post, Json, Router};
use juggler::agents::{extension::Envs, ExtensionConfig};
use http::{HeaderMap, StatusCode};
use serde::{Deserialize, Serialize};
use tracing;

/// Enum representing the different types of extension configuration requests.
#[derive(Deserialize)]
#[serde(tag = "type")]
enum ExtensionConfigRequest {
    /// Server-Sent Events (SSE) extension.
    #[serde(rename = "sse")]
    Sse {
        /// The name to identify this extension
        name: String,
        /// The URI endpoint for the SSE extension.
        uri: String,
        #[serde(default)]
        /// Map of environment variable key to values.
        envs: Envs,
        /// List of environment variable keys. The server will fetch their values from the keyring.
        #[serde(default)]
        env_keys: Vec<String>,
        timeout: Option<u64>,
    },
    /// Standard I/O (stdio) extension.
    #[serde(rename = "stdio")]
    Stdio {
        /// The name to identify this extension
        name: String,
        /// The command to execute.
        cmd: String,
        /// Arguments for the command.
        #[serde(default)]
        args: Vec<String>,
        #[serde(default)]
        /// Map of environment variable key to values.
        envs: Envs,
        /// List of environment variable keys. The server will fetch their values from the keyring.
        #[serde(default)]
        env_keys: Vec<String>,
        timeout: Option<u64>,
    },
    /// Built-in extension that is part of the juggler binary.
    #[serde(rename = "builtin")]
    Builtin {
        /// The name of the built-in extension.
        name: String,
        display_name: Option<String>,
        timeout: Option<u64>,
    },
    /// Frontend extension that provides tools to be executed by the frontend.
    #[serde(rename = "frontend")]
    Frontend {
        /// The name to identify this extension
        name: String,
        /// The tools provided by this extension
        tools: Vec<mcp_core::tool::Tool>,
        /// Optional instructions for using the tools
        instructions: Option<String>,
    },
}

/// Response structure for adding an extension.
///
/// - `error`: Indicates whether an error occurred (`true`) or not (`false`).
/// - `message`: Provides detailed error information when `error` is `true`.
#[derive(Serialize)]
struct ExtensionResponse {
    error: bool,
    message: Option<String>,
}

/// Handler for adding a new extension configuration.
async fn add_extension(
    State(state): State<Arc<AppState>>,
    headers: HeaderMap,
    raw: axum::extract::Json<serde_json::Value>,
) -> Result<Json<ExtensionResponse>, StatusCode> {
    verify_secret_key(&headers, &state)?;

    // Log the raw request for debugging
    tracing::info!(
        "Received extension request: {}",
        serde_json::to_string_pretty(&raw.0).unwrap()
    );

    // Try to parse into our enum
    let request: ExtensionConfigRequest = match serde_json::from_value(raw.0.clone()) {
        Ok(req) => req,
        Err(e) => {
            tracing::error!("Failed to parse extension request: {}", e);
            tracing::error!(
                "Raw request was: {}",
                serde_json::to_string_pretty(&raw.0).unwrap()
            );
            return Err(StatusCode::UNPROCESSABLE_ENTITY);
        }
    };

    // If this is a Stdio extension that uses npx, check for Node.js installation
    #[cfg(target_os = "windows")]
    if let ExtensionConfigRequest::Stdio { cmd, .. } = &request {
        if cmd.ends_with("npx.cmd") || cmd.ends_with("npx") {
            // Check if Node.js is installed in standard locations
            let node_exists = std::path::Path::new(r"C:\Program Files\nodejs\node.exe").exists()
                || std::path::Path::new(r"C:\Program Files (x86)\nodejs\node.exe").exists();

            if !node_exists {
                // Get the directory containing npx.cmd
                let cmd_path = std::path::Path::new(&cmd);
                let script_dir = cmd_path.parent().ok_or(StatusCode::INTERNAL_SERVER_ERROR)?;

                // Run the Node.js installer script
                let install_script = script_dir.join("install-node.cmd");

                if install_script.exists() {
                    eprintln!("Installing Node.js...");
                    let output = std::process::Command::new(&install_script)
                        .arg("https://nodejs.org/dist/v23.10.0/node-v23.10.0-x64.msi")
                        .output()
                        .map_err(|e| {
                            eprintln!("Failed to run Node.js installer: {}", e);
                            StatusCode::INTERNAL_SERVER_ERROR
                        })?;

                    if !output.status.success() {
                        eprintln!(
                            "Failed to install Node.js: {}",
                            String::from_utf8_lossy(&output.stderr)
                        );
                        return Ok(Json(ExtensionResponse {
                            error: true,
                            message: Some(format!(
                                "Failed to install Node.js: {}",
                                String::from_utf8_lossy(&output.stderr)
                            )),
                        }));
                    }
                    eprintln!("Node.js installation completed");
                } else {
                    eprintln!(
                        "Node.js installer script not found at: {}",
                        install_script.display()
                    );
                    return Ok(Json(ExtensionResponse {
                        error: true,
                        message: Some("Node.js installer script not found".to_string()),
                    }));
                }
            }
        }
    }

    // Construct ExtensionConfig with Envs populated from keyring based on provided env_keys.
    let extension_config: ExtensionConfig = match request {
        ExtensionConfigRequest::Sse {
            name,
            uri,
            envs,
            env_keys,
            timeout,
        } => ExtensionConfig::Sse {
            name,
            uri,
            envs,
            env_keys,
            description: None,
            timeout,
            bundled: None,
        },
        ExtensionConfigRequest::Stdio {
            name,
            cmd,
            args,
            envs,
            env_keys,
            timeout,
        } => {
            // TODO: We can uncomment once bugs are fixed. Check allowlist for Stdio extensions
            // if !is_command_allowed(&cmd, &args) {
            //     return Ok(Json(ExtensionResponse {
            //         error: true,
            //         message: Some(format!(
            //             "Extension '{}' is not in the allowed extensions list. Command: '{} {}'. If you require access please ask your administrator to update the allowlist.",
            //             args.join(" "),
            //             cmd, args.join(" ")
            //         )),
            //     }));
            // }

            ExtensionConfig::Stdio {
                name,
                cmd,
                args,
                description: None,
                envs,
                env_keys,
                timeout,
                bundled: None,
            }
        }
        ExtensionConfigRequest::Builtin {
            name,
            display_name,
            timeout,
        } => ExtensionConfig::Builtin {
            name,
            display_name,
            timeout,
            bundled: None,
        },
        ExtensionConfigRequest::Frontend {
            name,
            tools,
            instructions,
        } => ExtensionConfig::Frontend {
            name,
            tools,
            instructions,
            bundled: None,
        },
    };

    // Get a reference to the agent
    let agent = state
        .get_agent()
        .await
        .map_err(|_| StatusCode::PRECONDITION_FAILED)?;
    let response = agent.add_extension(extension_config).await;

    // Respond with the result.
    match response {
        Ok(_) => Ok(Json(ExtensionResponse {
            error: false,
            message: None,
        })),
        Err(e) => {
            eprintln!("Failed to add extension configuration: {:?}", e);
            Ok(Json(ExtensionResponse {
                error: true,
                message: Some(format!(
                    "Failed to add extension configuration, error: {:?}",
                    e
                )),
            }))
        }
    }
}

/// Handler for removing an extension by name
async fn remove_extension(
    State(state): State<Arc<AppState>>,
    headers: HeaderMap,
    Json(name): Json<String>,
) -> Result<Json<ExtensionResponse>, StatusCode> {
    verify_secret_key(&headers, &state)?;

    // Get a reference to the agent
    let agent = state
        .get_agent()
        .await
        .map_err(|_| StatusCode::PRECONDITION_FAILED)?;
    match agent.remove_extension(&name).await {
        Ok(_) => Ok(Json(ExtensionResponse {
            error: false,
            message: None,
        })),
        Err(e) => Ok(Json(ExtensionResponse {
            error: true,
            message: Some(format!("Failed to remove extension: {:?}", e)),
        })),
    }
}

/// Registers the extension management routes with the Axum router.
pub fn routes(state: Arc<AppState>) -> Router {
    Router::new()
        .route("/extensions/add", post(add_extension))
        .route("/extensions/remove", post(remove_extension))
        .with_state(state)
}

/// Structure representing the allowed extensions from the YAML file
#[derive(Deserialize, Debug, Clone)]
struct AllowedExtensions {
    #[allow(dead_code)]
    extensions: Vec<ExtensionAllowlistEntry>,
}

/// Structure representing an individual extension entry in the allowlist
#[derive(Deserialize, Debug, Clone)]
struct ExtensionAllowlistEntry {
    #[allow(dead_code)]
    id: String,
    #[allow(dead_code)]
    command: String,
}

// Global cache for the allowed extensions
#[allow(dead_code)]
static ALLOWED_EXTENSIONS: OnceLock<Option<AllowedExtensions>> = OnceLock::new();

/// Fetches and parses the allowed extensions from the URL specified in GOOSE_ALLOWLIST env var
#[allow(dead_code)]
fn fetch_allowed_extensions() -> Option<AllowedExtensions> {
    match env::var("GOOSE_ALLOWLIST") {
        Err(_) => {
            // Environment variable not set, no allowlist to enforce
            None
        }
        Ok(url) => match reqwest::blocking::get(&url) {
            Err(e) => {
                eprintln!("Failed to fetch allowlist: {}", e);
                None
            }
            Ok(response) if !response.status().is_success() => {
                eprintln!("Failed to fetch allowlist, status: {}", response.status());
                None
            }
            Ok(response) => match response.text() {
                Err(e) => {
                    eprintln!("Failed to read allowlist response: {}", e);
                    None
                }
                Ok(text) => match serde_yaml::from_str::<AllowedExtensions>(&text) {
                    Ok(allowed) => Some(allowed),
                    Err(e) => {
                        eprintln!("Failed to parse allowlist YAML: {}", e);
                        None
                    }
                },
            },
        },
    }
}

/// Gets the cached allowed extensions or fetches them if not yet cached
#[allow(dead_code)]
fn get_allowed_extensions() -> &'static Option<AllowedExtensions> {
    ALLOWED_EXTENSIONS.get_or_init(fetch_allowed_extensions)
}

/// Checks if a command is allowed based on the allowlist
#[allow(dead_code)]
fn is_command_allowed(cmd: &str, args: &[String]) -> bool {
    // Check if bypass is enabled
    if let Ok(bypass_value) = env::var("GOOSE_ALLOWLIST_BYPASS") {
        if bypass_value.to_lowercase() == "true" {
            // Bypass the allowlist check
            println!("Allowlist check bypassed due to GOOSE_ALLOWLIST_BYPASS=true");
            return true;
        }
    }

    // Proceed with normal allowlist check
    is_command_allowed_with_allowlist(&make_full_cmd(cmd, args), get_allowed_extensions())
}

fn make_full_cmd(cmd: &str, args: &[String]) -> String {
    // trim each arg string to remove any leading/trailing whitespace
    let args_trimmed = args.iter().map(|arg| arg.trim()).collect::<Vec<&str>>();

    format!("{} {}", cmd.trim(), args_trimmed.join(" ").trim())
}

/// Normalizes a command name by removing common executable extensions (.exe, .cmd, .bat)
/// This makes the allowlist more portable across different operating systems
fn normalize_command_name(cmd: &str) -> String {
    cmd.replace(".exe", "")
        .replace(".cmd", "")
        .replace(".bat", "")
        .replace(" -y ", " ")
        .replace(" -y", "")
        .replace("-y ", "")
        .to_string()
}

/// Implementation of command allowlist checking that takes an explicit allowlist parameter
/// This makes it easier to test without relying on global state
fn is_command_allowed_with_allowlist(
    cmd: &str,
    allowed_extensions: &Option<AllowedExtensions>,
) -> bool {
    // Extract the first part of the command (before any spaces)
    let first_part = cmd.split_whitespace().next().unwrap_or(cmd);

    // Extract the base command name (last part of the path)
    let cmd_base_with_ext = Path::new(first_part)
        .file_name()
        .and_then(|name| name.to_str())
        .unwrap_or(first_part);

    // Normalize the command name by removing extensions like .exe or .cmd
    let cmd_base = normalize_command_name(cmd_base_with_ext);

    // Special case: Always allow commands ending with "/juggled" or equal to "juggled"
    // But still enforce that it's in the same directory as the current executable
    if cmd_base == "juggled" {
        // Only allow exact matches (no arguments)
        if cmd == first_part {
            // For absolute paths, check that it's in the same directory as the current executable
            if (first_part.contains('/') || first_part.contains('\\'))
                && !first_part.starts_with("./")
            {
                let current_exe = std::env::current_exe().unwrap();
                let current_exe_dir = current_exe.parent().unwrap();
                let expected_path = current_exe_dir.join("juggled").to_str().unwrap().to_string();

                // Normalize both paths before comparing
                let normalized_cmd_path = normalize_command_name(first_part);
                let normalized_expected_path = normalize_command_name(&expected_path);

                if normalized_cmd_path == normalized_expected_path {
                    return true;
                }
                // If the path doesn't match, don't allow it
                println!("Juggled not in expected directory: {}", cmd);
                println!("Expected path: {}", expected_path);
                return false;
            } else {
                // For non-path juggled or relative paths, allow it
                return true;
            }
        }
        return false;
    }

    match allowed_extensions {
        // No allowlist configured, allow all commands
        None => true,

        // Empty allowlist, allow all commands
        Some(extensions) if extensions.extensions.is_empty() => true,

        // Check against the allowlist
        Some(extensions) => {
            // Strip out the Juggler app resources/bin prefix if present (handle both macOS and Windows paths)
            let mut cmd_to_check = cmd.to_string();
            let mut is_juggler_path = false;

            // Check for macOS-style Juggler.app path
            if cmd_to_check.contains("Juggler.app/Contents/Resources/bin/") {
                if let Some(idx) = cmd_to_check.find("Juggler.app/Contents/Resources/bin/") {
                    cmd_to_check = cmd_to_check
                        [(idx + "Juggler.app/Contents/Resources/bin/".len())..]
                        .to_string();
                    is_juggler_path = true;
                }
            }
            // Check for Windows-style Juggler path with resources\bin
            else if cmd_to_check.to_lowercase().contains("\\resources\\bin\\")
                || cmd_to_check.contains("/resources/bin/")
            {
                // Also handle forward slashes
                if let Some(idx) = cmd_to_check
                    .to_lowercase()
                    .rfind("\\resources\\bin\\")
                    .or_else(|| cmd_to_check.rfind("/resources/bin/"))
                {
                    let path_len = if cmd_to_check.contains("/resources/bin/") {
                        "/resources/bin/".len()
                    } else {
                        "\\resources\\bin\\".len()
                    };
                    cmd_to_check = cmd_to_check[(idx + path_len)..].to_string();
                    is_juggler_path = true;
                }
            }

            // Only check current directory for non-Juggler paths
            if !is_juggler_path {
                // Check that the command exists as a peer command to current executable directory
                // Only apply this check if the command includes a path separator
                let current_exe = std::env::current_exe().unwrap();
                let current_exe_dir = current_exe.parent().unwrap();
                let expected_path = current_exe_dir
                    .join(&cmd_base)
                    .to_str()
                    .unwrap()
                    .to_string();

                // Normalize both paths before comparing
                let normalized_cmd_path = normalize_command_name(first_part);

                if (first_part.contains('/') || first_part.contains('\\'))
                    && normalized_cmd_path != expected_path
                    && !cmd_to_check.contains("Juggler.app/Contents/Resources/bin/")
                {
                    println!("Command not in expected directory: {}", cmd);
                    return false;
                }

                // Remove current_exe_dir + "/" from the cmd to clean it up
                let path_to_trim = format!("{}/", current_exe_dir.to_str().unwrap());
                cmd_to_check = cmd_to_check.replace(&path_to_trim, "");
            }

            println!("Command to check after path trimming: {}", cmd_to_check);

            // Remove @version suffix from command parts, but preserve scoped npm packages
            let parts: Vec<&str> = cmd_to_check.split_whitespace().collect();
            let mut cleaned_parts: Vec<String> = Vec::new();

            for part in parts {
                if part.contains('@') && !part.starts_with('@') {
                    // This is likely a package with a version suffix, like "package@1.0.0"
                    // Keep only the part before the @ symbol
                    if let Some(base_part) = part.split('@').next() {
                        cleaned_parts.push(base_part.to_string());
                    } else {
                        cleaned_parts.push(part.to_string());
                    }
                } else {
                    // Either no @ symbol or it's a scoped package (starts with @)
                    cleaned_parts.push(part.to_string());
                }
            }

            // Reconstruct the command without version suffixes
            cmd_to_check = cleaned_parts.join(" ");

            println!("Command to check after @version removal: {}", cmd_to_check);

            // Normalize the command before comparing with allowlist entries
            let normalized_cmd = normalize_command_name(&cmd_to_check);

            println!("Final normalized command: {}", normalized_cmd);

            extensions.extensions.iter().any(|entry| {
                let normalized_entry = normalize_command_name(&entry.command);
                normalized_cmd == normalized_entry
            })
        }
    }
}
