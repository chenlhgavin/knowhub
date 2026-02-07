use anyhow::Result;
use colored::Colorize;
use reqwest::Response;
use std::io::IsTerminal;

/// Print the full HTTP response: status line, headers, and body
pub async fn print(response: Response) -> Result<()> {
    let is_tty = std::io::stdout().is_terminal();

    // Extract metadata before consuming the body
    let status = response.status();
    let version = response.version();
    let headers = response.headers().clone();
    let content_type = headers
        .get("content-type")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("")
        .to_string();

    // Consume the body
    let body = response.text().await?;

    // --- Status line ---
    let version_str = format_version(version);
    let status_line = format!(
        "{} {} {}",
        version_str,
        status.as_u16(),
        status.canonical_reason().unwrap_or("")
    );

    if is_tty {
        let colored_status = if status.is_success() {
            status_line.green().bold()
        } else if status.is_redirection() {
            status_line.yellow().bold()
        } else {
            status_line.red().bold()
        };
        println!("{colored_status}");
    } else {
        println!("{status_line}");
    }

    // --- Headers ---
    for (key, value) in &headers {
        let value_str = value.to_str().unwrap_or("<non-utf8>");
        if is_tty {
            println!("{}: {}", key.as_str().dimmed(), value_str);
        } else {
            println!("{}: {value_str}", key.as_str());
        }
    }

    // Blank line separating headers from body
    println!();

    // --- Body ---
    if !body.is_empty() {
        let is_json_type = is_json(&content_type);

        let display_body = if is_json_type {
            jsonxf::pretty_print(&body).unwrap_or_else(|_| body.clone())
        } else {
            body
        };

        if is_tty && is_json_type {
            print!("{}", colorize_json(&display_body));
        } else {
            print!("{display_body}");
        }

        // Ensure trailing newline
        if !display_body.ends_with('\n') {
            println!();
        }
    }

    Ok(())
}

/// Format HTTP version for display
fn format_version(version: reqwest::Version) -> &'static str {
    match version {
        reqwest::Version::HTTP_09 => "HTTP/0.9",
        reqwest::Version::HTTP_10 => "HTTP/1.0",
        reqwest::Version::HTTP_11 => "HTTP/1.1",
        reqwest::Version::HTTP_2 => "HTTP/2",
        reqwest::Version::HTTP_3 => "HTTP/3",
        _ => "HTTP/?",
    }
}

/// Check if the content-type indicates JSON
fn is_json(content_type: &str) -> bool {
    content_type.contains("json")
}

/// Colorize a pretty-printed JSON string with syntax highlighting
///
/// Colors:
/// - Keys:    cyan + bold
/// - Strings: green
/// - Numbers: magenta
/// - Booleans: yellow
/// - Null:    red
fn colorize_json(json: &str) -> String {
    let mut result = String::with_capacity(json.len() * 2);
    let chars: Vec<char> = json.chars().collect();
    let len = chars.len();
    let mut i = 0;

    while i < len {
        match chars[i] {
            // --- Quoted string (key or value) ---
            '"' => {
                let start = i;
                i += 1; // skip opening quote
                while i < len {
                    if chars[i] == '\\' {
                        i += 2; // skip escaped char
                    } else if chars[i] == '"' {
                        i += 1; // skip closing quote
                        break;
                    } else {
                        i += 1;
                    }
                }
                let s: String = chars[start..i].iter().collect();

                // Peek ahead: if next non-whitespace is ':', this is a key
                let mut j = i;
                while j < len && chars[j].is_ascii_whitespace() {
                    j += 1;
                }

                if j < len && chars[j] == ':' {
                    // JSON key
                    result.push_str(&format!("{}", s.cyan().bold()));
                } else {
                    // JSON string value
                    result.push_str(&format!("{}", s.green()));
                }
            }

            // --- Number ---
            c if c.is_ascii_digit()
                || (c == '-' && i + 1 < len && chars[i + 1].is_ascii_digit()) =>
            {
                let start = i;
                i += 1;
                while i < len
                    && (chars[i].is_ascii_digit()
                        || chars[i] == '.'
                        || chars[i] == 'e'
                        || chars[i] == 'E'
                        || chars[i] == '+'
                        || chars[i] == '-')
                {
                    i += 1;
                }
                let num: String = chars[start..i].iter().collect();
                result.push_str(&format!("{}", num.magenta()));
            }

            // --- Boolean: true ---
            't' if chars[i..].starts_with(&['t', 'r', 'u', 'e']) => {
                result.push_str(&format!("{}", "true".yellow()));
                i += 4;
            }

            // --- Boolean: false ---
            'f' if chars[i..].starts_with(&['f', 'a', 'l', 's', 'e']) => {
                result.push_str(&format!("{}", "false".yellow()));
                i += 5;
            }

            // --- Null ---
            'n' if chars[i..].starts_with(&['n', 'u', 'l', 'l']) => {
                result.push_str(&format!("{}", "null".red()));
                i += 4;
            }

            // --- Everything else (braces, brackets, colons, commas, whitespace) ---
            _ => {
                result.push(chars[i]);
                i += 1;
            }
        }
    }

    result
}
