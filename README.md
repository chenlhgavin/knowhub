# KnowHub

A content-driven technical knowledge base covering Rust, Python, and Software Architecture.

Live site: <https://chenlhgavin.github.io/knowhub>

## Overview

KnowHub is an Astro-powered static website combined with standalone, hands-on curriculum tracks.
It offers three learning tracks: **Rust** (20 lessons, 3 projects), **Python** (10 chapters, 3 projects), and **Architecture** (6 modules).
The browsable website serves as the presentation layer; curriculum content works independently.

> **Note:** All curriculum content (lessons, exercises, articles) is written in **Chinese (中文)**.

## Features

- Browsable knowledge hub with articles on Rust, Python, and software architecture
- Three self-paced curriculum tracks with lessons, exercises, and answer keys
- Runnable Rust projects (HTTP client, web scraper) in a Cargo workspace
- Python capstone projects progressing from beginner to advanced
- Presentation slides with fullscreen carousel viewer
- Mermaid diagram rendering in articles
- Responsive design with dark mode support

## Prerequisites

- **Site**: Node.js 20+ and npm
- **Rust track**: Rust toolchain via [rustup](https://rustup.rs/) (stable + nightly for formatting)
- **Python track**: Python 3.10+

## Project Structure

```
knowhub/
├── site/           # Astro 5 static website (presentation layer, deployed to GitHub Pages)
├── rustascent/     # Rust learning track (Cargo workspace with lessons and projects)
├── python/         # Python learning track (10 chapters with exercises/solutions, 3 capstone projects)
└── architecture/   # Software architecture curriculum (6 modules with lessons, exercises, answers)
```

## Learning Tracks

### Rust (RustAscend)

- 20 lessons progressing from basics to async programming and macros
- Cargo workspace with 3 runnable projects: hello_rust, httpie, scrape_url

See [rustascent/README.md](rustascent/README.md) for the full roadmap.

### Python (PyAscend)

- 10 chapters from variables and control flow through metaclasses and concurrency
- Exercises and solutions in every chapter
- 3 capstone projects: Expense Tracker, Text Analyzer, Task Scheduler

See [python/README.md](python/README.md) for the full roadmap.

### Architecture

- 6 modules covering:
  - Fundamentals
  - Design Basics (SOLID, patterns, layered architecture)
  - Distributed Systems (CAP, consensus)
  - Architecture Methodology (microservices, HA, caching/MQ)
  - System Design Practice (URL shortener, feed system)
  - Architect Mindset (DDD, evolutionary architecture)
- Lessons, exercises, and answer keys per module

## Quick Start

**Browse online:** <https://chenlhgavin.github.io/knowhub>

**Run the site locally:**

```bash
cd site && npm install && npm run dev
```

Site available at `http://localhost:4321/knowhub`

**Rust track:**

```bash
cd rustascent
cargo build --workspace        # build all projects
cargo run -p httpie            # run a specific project
```

**Python track:**

```bash
cd python
python3 01_basics/exercises/ex01_variables.py
```

## Configuration

The site is configured via `site/astro.config.mjs`:

- `site` — Deployment URL (currently `https://chenlhgavin.github.io`)
- `base` — Base path (currently `/knowhub`)
- `server.host` / `server.port` — Dev server bind address (default `0.0.0.0:4321`)

Content is managed through data files and markdown collections.
See [site/README.md](site/README.md) for content management instructions.

## Tech Stack

| Technology | Role |
|---|---|
| Astro 5 | Static site generation |
| React 19 | Interactive components (Astro islands) |
| Tailwind CSS 4 | Styling |
| MDX / Markdown | Content authoring |
| Mermaid | Diagram rendering |
| Rust / Cargo / Tokio | Rust curriculum and projects |
| Python 3.10+ | Python curriculum |

## Development

See [CLAUDE.md](CLAUDE.md) for coding standards, testing workflow, and code style conventions.
See [.coda.md](.coda.md) for architecture details, data flows, and module documentation.

## Note

This is a personal educational project and is not accepting contributions.
Learners are welcome to fork and adapt for their own use.

## License

[MIT](LICENSE)
