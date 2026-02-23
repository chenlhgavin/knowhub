


# Verification Plan: update-doc

## Automated Checks

- [ ] All pre-configured checks pass (scoped to the Rust workspace since no root Cargo.toml exists):
  - [ ] `cd rustascent && cargo build --workspace`
  - [ ] `cd rustascent && cargo +nightly fmt -- --check`
  - [ ] `cd rustascent && cargo clippy --workspace -- -D warnings`
- [ ] No regression in existing tests (`cd rustascent && cargo test --workspace`)
- [ ] Site still builds cleanly: `cd site && npm run build`

## Functional Verification

### LICENSE file

- [ ] Scenario 1: LICENSE file exists and is valid
  - Check: `LICENSE` exists at the repo root
  - Expected: Standard MIT license text, year 2026, copyright holder name present

- [ ] Scenario 2: LICENSE content matches site/README.md claim
  - Check: `site/README.md` references "MIT" — the new `LICENSE` file should be MIT
  - Expected: License type is consistent across the repo

### README.md — Required Sections

- [ ] Scenario 3: README contains all specified sections
  - Check: Read `README.md` and confirm presence of:
    - Header with project name "KnowHub"
    - One-line tagline / description
    - Live site link (`https://chenlhgavin.github.io/knowhub`)
    - Overview section with Chinese content language note
    - Project Structure section with directory tree
    - Learning Tracks section (Rust, Python, Architecture subsections)
    - Getting Started section with commands
    - Tech Stack table
    - Personal project note (not accepting contributions)
    - License section linking to `LICENSE`
  - Expected: All sections present, none missing

- [ ] Scenario 4: README is written in English
  - Check: Scan the README for language
  - Expected: All prose is in English (Chinese appears only in the language note as 中文)

### README.md — Factual Accuracy

- [ ] Scenario 5: Directory paths in Project Structure match the repo
  - Check: Verify each directory listed in the tree actually exists:
    - `site/`
    - `rustascent/`
    - `python/`
    - `architecture/`
  - Expected: All four directories exist at the repo root

- [ ] Scenario 6: Rust track stats are accurate
  - Check: Count lesson files in `rustascent/lessons/`, count projects in `rustascent/projects/`
  - Expected: 20 lessons, 3 projects (hello_rust, httpie, scrape_url)

- [ ] Scenario 7: Python track stats are accurate
  - Check: Count chapter directories in `python/` (pattern `[0-9]*_*`), count project directories in `python/projects/`
  - Expected: 10 chapters, 3 projects (p01_expense_tracker, p02_text_analyzer, p03_task_scheduler)

- [ ] Scenario 8: Architecture track stats are accurate
  - Check: Count module directories in `architecture/` (pattern `[0-9]*-*`)
  - Expected: 6 modules

- [ ] Scenario 9: Cargo workspace package name in Getting Started is valid
  - Check: Verify `httpie` is an actual package name in the Cargo workspace
  - Input: `grep 'httpie' rustascent/Cargo.toml`
  - Expected: Package name matches exactly what the README uses (`cargo run -p httpie`)

- [ ] Scenario 10: Python exercise file path in Getting Started is valid
  - Check: Verify `python/01_basics/exercises/ex01_variables.py` exists
  - Expected: File exists at that exact path

### README.md — Links

- [ ] Scenario 11: Sub-project README links are valid
  - Check: Verify the README links to `rustascent/README.md` and `python/README.md`
  - Expected: Both files exist and are linked with correct relative paths

- [ ] Scenario 12: Live site URL is correct
  - Check: The URL `https://chenlhgavin.github.io/knowhub` matches the configured deployment in `site/astro.config.mjs`
  - Expected: URLs are consistent with `site: 'https://chenlhgavin.github.io'` and `base: '/knowhub'`

## Edge Cases

- [ ] README renders correctly as GitHub-flavored Markdown (no broken tables, no unclosed code fences, no malformed links)
- [ ] Directory tree in Project Structure uses plain code block (no special characters that might render incorrectly)
- [ ] Tech stack table has consistent column alignment and renders as a proper table
- [ ] No trailing whitespace or inconsistent line endings in either file
- [ ] LICENSE file has no trailing newline issues (ends with a single newline)

## Integration Points

- [ ] `site/README.md` license claim ("MIT") is consistent with the new root `LICENSE` file
- [ ] No conflicts with existing files — confirm no root `README.md` or `LICENSE` exists before creation
- [ ] Git status after changes shows exactly two new untracked files: `README.md` and `LICENSE`
- [ ] The new README does not duplicate content from sub-project READMEs — it summarizes and links instead

## Performance

Not applicable — documentation-only change, no runtime impact.

## Security

- [ ] LICENSE file does not inadvertently include any sensitive information (email addresses, internal names) beyond what the author intends to be public
- [ ] README does not expose any internal infrastructure details, API keys, or credentials
