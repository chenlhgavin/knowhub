# CLAUDE.md — Development Guidelines for KnowHub

## Core Principles

- **SOLID/DRY**: Follow SOLID principles. Extract shared logic but avoid premature abstraction.
- **No incomplete code**: Never leave `TODO`, `FIXME`, or placeholder comments. Every commit must be complete and functional.
- **Analyze before coding**: Read and understand existing code before making changes. Never propose changes to code you haven't read.
- **Remove dead code**: Delete unused imports, variables, functions, and files. No commented-out code blocks.
- **Minimal changes**: Only make changes directly requested or clearly necessary. Don't refactor surrounding code or add features beyond what was asked.

## Design Principles

### Type Safety

- **TypeScript**: Use strict mode. Prefer explicit types over `any`. Use discriminated unions to make illegal states unrepresentable.
- **Rust**: Leverage the type system — use enums for state machines, newtypes for domain concepts, `Option`/`Result` for fallibility. Never use `unwrap()` or `expect()` in production code.
- **Astro Content Collections**: Define Zod schemas for all content frontmatter. Use typed helper functions in `site/src/data/topics.ts`.

### Error Handling

- **TypeScript/Astro**: Rely on build-time validation via TypeScript strict mode and Zod content schemas. Handle errors at system boundaries.
- **Rust (library crates)**: Use `thiserror` to define error enums with `#[error]` and `#[source]` attributes. Each module should have its own error type.
- **Rust (application/binary)**: Use `anyhow::Result` with `.context()` for rich error propagation. The `?` operator throughout — no `unwrap()`.
- **Python**: Use specific exception types. Catch exceptions at appropriate levels, not broadly.

### API Design

- Prefer composition over inheritance.
- Keep public interfaces small and focused.
- Use descriptive names that convey intent without comments.

## Code Quality

- **Function size**: Keep functions under 50 lines. Extract helper functions for complex logic.
- **Import ordering**: Group imports by category — standard library, third-party, local — with blank lines between groups.
- **Dead code**: Remove all unused code immediately. Don't keep "just in case" code.
- **Linting**: All code must pass linting without warnings before commit.

## Security

- **Input validation**: Validate all external input at system boundaries. Content collection schemas serve as validation for markdown frontmatter.
- **Sensitive data**: Never commit `.env` files, API keys, tokens, or credentials. Use `.env.example` for documenting required environment variables.
- **Secrets management**: Use environment variables for secrets. Never hardcode secrets in source code.
- **Dependencies**: Keep dependencies up to date. Review new dependencies for security advisories before adding.

## Testing (TDD)

### Workflow

1. **Write a failing test** that describes the expected behavior
2. **Implement** the minimum code to make the test pass
3. **Refactor** while keeping all tests green

### Conventions

- **Test naming**: Use descriptive names that state the scenario and expected outcome (e.g., `test_parse_url_with_missing_scheme_returns_error`).
- **Rust tests**: Place unit tests in `#[cfg(test)] mod tests` within the source file. Integration tests go in `tests/` directory. Use `#[tokio::test]` for async tests.
- **TypeScript tests**: Co-locate test files with source using `.test.ts` / `.spec.ts` suffix.
- **Python tests**: Place tests in `tests/` directory mirroring source structure. Use `pytest` with descriptive function names prefixed with `test_`.
- **Coverage**: Focus coverage on critical paths and edge cases rather than chasing percentages. All error paths must be tested.
- **Mocking**: Mock external dependencies (HTTP, filesystem, databases) at system boundaries. Prefer dependency injection over monkey-patching.

## Code Style

### TypeScript / Astro

- Use `const` by default, `let` when mutation is needed. Never use `var`.
- Prefer arrow functions for callbacks and inline functions.
- Use template literals over string concatenation.
- Trailing commas in multiline arrays, objects, and parameter lists.
- Format with Prettier defaults if available; otherwise follow Astro conventions.

### Rust

- Follow `rustfmt` defaults (use `cargo +nightly fmt`).
- Use `snake_case` for functions/variables, `PascalCase` for types/traits, `SCREAMING_SNAKE_CASE` for constants.
- Prefer `impl Trait` in argument position for simple generics.
- Use `clippy` with `-D warnings` — all warnings are errors.
- Group `use` statements: `std` → external crates → `crate`/`super`/`self`.

### Python

- Follow PEP 8. Use type hints for all function signatures.
- Use `snake_case` for functions/variables, `PascalCase` for classes.
- Prefer f-strings over `.format()` or `%` formatting.
- Use `ruff` for linting and formatting.

### Markdown / MDX

- Use ATX-style headers (`#`, `##`, `###`).
- One sentence per line in prose (for better diffs).
- Code blocks must specify a language for syntax highlighting.
- Frontmatter must conform to the content collection Zod schema.

## Toolchain & Build

### Site (Astro / TypeScript)

```bash
cd site
npm install                     # Install dependencies
npm run dev                     # Dev server (localhost:4321)
npm run build                   # Production build → dist/
npm run preview                 # Preview production build
```

### Rust (Cargo workspace)

```bash
cd rustascent
cargo build --workspace         # Build all crates
cargo test --workspace          # Run all tests
cargo +nightly fmt              # Format code
cargo +nightly fmt -- --check   # Check formatting (CI)
cargo clippy --workspace -- -D warnings  # Lint with warnings as errors
```

### Python

```bash
cd python
python -m venv .venv && source .venv/bin/activate  # Virtual environment
pip install -r requirements.txt                     # Install deps (if present)
pytest                                              # Run tests
ruff check .                                        # Lint
ruff format .                                       # Format
```

## Key Patterns & Conventions

### Content Pipeline

All site content follows the article rendering pipeline:
1. Write `.md`/`.mdx` in `site/src/content/{topic}/`
2. Register metadata in `site/src/data/topics.ts`
3. Astro indexes via content collections at build time
4. Dynamic routes resolve slugs via `getStaticPaths()`
5. Static HTML is generated and deployed

### Component Organization

Components in `site/src/components/` are organized by concern:
- `cards/` — Card-style UI components (TopicCard, ArticleCard)
- `content/` — Content rendering components
- `interactive/` — Client-side interactive widgets (React islands)
- `layout/` — Structural layout components
- `sections/` — Page section components

### Rust Project Structure

The Rust workspace under `rustascent/` follows these conventions:
- Each project has its own `Cargo.toml` with explicit dependency versions
- Error types defined per module using `thiserror`
- Application entry points use `anyhow::Result<()>` for `main()`
- Async code uses `tokio` with `#[tokio::main]` and `rt-multi-thread`
- Prefer message-passing (`tokio::sync::mpsc`) over shared mutable state

## CODA Repository Documentation

See [.coda.md](.coda.md) for a comprehensive overview of this repository's structure, tech stack, and conventions. This file is auto-generated by CODA and kept up to date.
