use std::env;
use std::fs;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    for arg in std::env::args() {
        println!("{}", arg);
    }

    let args: Vec<String> = env::args().collect();

    let url = args.get(1).map(|s| s.as_str()).unwrap_or("https://www.rust-lang.org");
    let output_path = args.get(2).map(|s| s.as_str()).unwrap_or("output.md");

    println!("正在请求 {} ...", url);

    let html = reqwest::blocking::get(url)?.text()?;

    println!("获取到 HTML，长度: {} 字节", html.len());

    let markdown = html2md::parse_html(&html);

    fs::write(output_path, &markdown)?;

    println!("转换完成，Markdown 已保存到 {}", output_path);

    Ok(())
}
