


# Task: update-doc

## Overview

The KnowHub monorepo has no root-level `README.md`, making it difficult for learners who discover the project on GitHub to understand what it offers or how to get started. Additionally, the `site/README.md` references an MIT license, but no `LICENSE` file exists in the repository.

This task creates two files at the repo root:

1. **`README.md`** — The project's front door, introducing the knowledge hub and its three learning tracks (Rust, Python, Architecture), with quick-start instructions and links to sub-project READMEs.
2. **`LICENSE`** — A standard MIT license file, formalizing what `site/README.md` already claims.

## Target Audience

Developers who discover the KnowHub repository on GitHub and want to understand what the project offers, what learning tracks are available, and how to get started — either by browsing the live site or running the curriculum content locally.

## Content Outline

### README.md

#### 1. Header & Tagline
- Project name: **KnowHub**
- One-line description: A content-driven technical knowledge base covering Rust, Python, and Software Architecture
- Live site link: `https://chenlhgavin.github.io/knowhub`

#### 2. Overview
- KnowHub is an Astro-powered static website combined with standalone, hands-on curriculum tracks
- Three tracks: **Rust** (20 lessons, 3 projects), **Python** (10 chapters, 3 projects), **Architecture** (6 modules)
- The browsable website serves as the presentation layer; curriculum content works independently
- Explicit note: curriculum content is written in **Chinese (中文)**

#### 3. Project Structure
- High-level directory tree showing four main areas:
  - `site/` — Astro 5 static website (presentation layer, deployed to GitHub Pages)
  - `rustascent/` — Rust learning track (Cargo workspace with lessons and projects)
  - `python/` — Python learning track (10 chapters with exercises/solutions, 3 capstone projects)
  - `architecture/` — Software architecture curriculum (6 modules with lessons, exercises, answers)

#### 4. Learning Tracks
- **Rust (RustAscend)**
  - 20 lessons progressing from basics to async programming and macros
  - Cargo workspace with 3 runnable projects: hello_rust, httpie, scrape_url
  - Link to `rustascent/README.md` for full roadmap
- **Python (PyAscend)**
  - 10 chapters from variables and control flow through metaclasses and concurrency
  - Exercises and solutions in every chapter
  - 3 capstone projects: Expense Tracker, Text Analyzer, Task Scheduler
  - Link to `python/README.md` for full roadmap
- **Architecture**
  - 6 modules: Fundamentals, Design Basics (SOLID, patterns, layered), Distributed Systems (CAP, consensus), Architecture Methodology (microservices, HA, caching/MQ), System Design Practice (URL shortener, feed system), Architect Mindset (DDD, evolutionary architecture)
  - Lessons, exercises, and answer keys per module

#### 5. Getting Started
- **Browse online**: link to live GitHub Pages site
- **Run the site locally**:
  ```bash
  cd site && npm install && npm run dev
  ```
  Site available at `http://localhost:4321/knowhub`
- **Rust track**:
  ```bash
  cd rustascent
  cargo build --workspace        # build all projects
  cargo run -p httpie            # run a specific project
  ```
- **Python track**:
  ```bash
  cd python
  python3 01_basics/exercises/ex01_variables.py
  ```

#### 6. Tech Stack
- Compact table with two columns (Technology, Role):
  - Astro 5 — Static site generation
  - React 19 — Interactive components (Astro islands)
  - Tailwind CSS 4 — Styling
  - MDX / Markdown — Content authoring
  - Mermaid — Diagram rendering
  - Rust / Cargo / Tokio — Rust curriculum and projects
  - Python 3.10+ — Python curriculum

#### 7. Note
- This is a personal educational project
- Not accepting contributions
- Learners are welcome to fork and adapt for their own use

#### 8. License
- MIT — link to `LICENSE` file

### LICENSE

- Standard MIT license text
- Year: 2026
- Copyright holder: derived from existing project metadata / git config

## Development Phases

### Phase 1: Add LICENSE file
- **Goal**: Formalize the MIT license already referenced in `site/README.md`
- **Tasks**:
  - Create `LICENSE` at the repo root with standard MIT license text, year 2026
- **Commit message**: `docs: add MIT LICENSE file`

### Phase 2: Create root README.md
- **Goal**: Provide a clear entry point for learners discovering the project on GitHub
- **Tasks**:
  - Create `README.md` at the repo root following the content outline above
  - Include live site link, project structure, learning track summaries, getting started commands, tech stack table
  - Add Chinese content language note in the Overview section
  - Link to `rustascent/README.md` and `python/README.md` for detailed track information
  - Add personal project note and license reference at the bottom
- **Commit message**: `docs: add root README introducing KnowHub and learning tracks`

### Phase 3: Verify
- **Goal**: Ensure all references in the README are accurate
- **Tasks**:
  - Confirm all directory paths referenced in the README exist in the repo
  - Confirm the live site URL matches `site/astro.config.mjs` (`https://chenlhgavin.github.io/knowhub`)
  - Confirm the Cargo workspace package names match actual `Cargo.toml` entries (e.g., `httpie`)
  - Confirm Python exercise file paths match actual file structure (e.g., `python/01_basics/exercises/ex01_variables.py`)
- **Commit message**: No commit — verification only

## References

- `site/README.md` — Existing site README with tech stack details, page routes, content management guide
- `site/astro.config.mjs` — Astro deployment config (canonical site URL and base path)
- `rustascent/README.md` — Full Rust learning roadmap, directory structure, quick start
- `python/README.md` — Python curriculum overview, chapter listing, project descriptions
- `architecture/` directory structure — 6 modules with lessons/exercises/answers
- `.coda.md` — Repository architecture overview and conventions
- `site/src/data/topics.ts` — Topic and article definitions (source of truth for content catalog)

## Risk & Trade-offs

- **Content language mismatch**: The README is in English but all curriculum content (lessons, exercises, articles) is in Chinese. Mitigated by an explicit note in the Overview section, but may still surprise some English-speaking learners.
- **Stat drift**: Concrete numbers (20 lessons, 10 chapters, 6 modules, 3 projects) could become stale if content is added or removed. Acceptable for a personal project with low change frequency.
- **No screenshots or visuals**: The README will be text-only. Screenshots of the live site could improve appeal but add maintenance burden. Can be added later if desired.
- **No architecture/ README**: Unlike `rustascent/` and `python/`, the `architecture/` directory has no README of its own. The root README will summarize its content, but there's no detailed sub-README to link to. Consider creating one in a follow-up task.
