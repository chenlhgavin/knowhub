---
name: codex-code-review
description: Perform code reviews using OpenAI Codex CLI. Use this skill when users request code review, analysis of diffs/PRs, security audits, performance/architecture analysis, or automated code quality feedback.
---

# Codex Code Review Skill

This skill leverages OpenAI Codex CLI in headless mode to perform comprehensive code reviews with AI-powered analysis.

## Prerequisites

- **Codex CLI**: Install via `npm install -g @openai/codex` or follow [official docs](https://developers.openai.com/codex/cli/)
- **Authentication**: Codex CLI manages authentication internally via `~/.codex/auth.json`. No manual API key or environment variable setup is required.
- **Git Repository**: Codex requires commands to run inside a Git repository

## Permission Setup (IMPORTANT)

Before running reviews, ensure proper permissions are granted. The script handles this automatically, but understanding the modes is important:

| Mode | Flag | Use Case |
|------|------|----------|
| Full Auto | `--full-auto` | Standard reviews (workspace read/write, prompts for network) |
| CI/Headless | `--dangerously-bypass-approvals-and-sandbox` | Automated pipelines (use with caution) |

**For v0.20+**: If full-auto doesn't work, the script will fall back to bypass mode in CI environments (when `CI=true`).

## Capabilities

1. **Git Staged Changes Review**: Review changes before committing
2. **Specific Files Review**: Analyze one or more specified files
3. **Directory Review**: Comprehensive review of entire directories
4. **Git Diff Review**: Analyze diffs between branches, commits, or refs
5. **Security Audit**: Check for vulnerabilities (SQL injection, XSS, auth bypasses, etc.)
6. **Performance Analysis**: Identify performance bottlenecks and optimization opportunities
7. **Architecture Review**: Evaluate design patterns and code structure

## Usage

When the user requests a code review, follow these steps:

### Step 0: Environment Setup (First Time Only)

Run the setup script to verify the environment:

```bash
bash /home/ubuntu/workspace/codeai/.claude/skills/codex-code-review/scripts/setup.sh --check
```

If Codex CLI is not installed:
```bash
bash /home/ubuntu/workspace/codeai/.claude/skills/codex-code-review/scripts/setup.sh --install
```

### Step 1: Determine Review Type and Execute

### 1. Review Git Staged Changes

Review changes that are staged for commit:

```bash
bash /home/ubuntu/workspace/codeai/.claude/skills/codex-code-review/scripts/review.sh staged
```

### 2. Review Specific Files

Review one or more specific files:

```bash
bash /home/ubuntu/workspace/codeai/.claude/skills/codex-code-review/scripts/review.sh files "path/to/file1.js" "path/to/file2.py"
```

### 3. Review Directory

Review all files in a directory:

```bash
bash /home/ubuntu/workspace/codeai/.claude/skills/codex-code-review/scripts/review.sh directory "src/components"
```

### 4. Review Git Diff

Review diff between branches or commits:

```bash
# Diff against main branch
bash /home/ubuntu/workspace/codeai/.claude/skills/codex-code-review/scripts/review.sh diff --base main

# Diff between specific commits
bash /home/ubuntu/workspace/codeai/.claude/skills/codex-code-review/scripts/review.sh diff --base abc123 --head def456

# Diff for a specific commit
bash /home/ubuntu/workspace/codeai/.claude/skills/codex-code-review/scripts/review.sh diff --commit HEAD
```

### 5. Security Audit

Perform security-focused review:

```bash
bash /home/ubuntu/workspace/codeai/.claude/skills/codex-code-review/scripts/review.sh security "src/"
```

### 6. Performance Analysis

Analyze code for performance issues:

```bash
bash /home/ubuntu/workspace/codeai/.claude/skills/codex-code-review/scripts/review.sh performance "src/"
```

### 7. Architecture Review

Evaluate code architecture and design:

```bash
bash /home/ubuntu/workspace/codeai/.claude/skills/codex-code-review/scripts/review.sh architecture "src/"
```

## Script Parameters

| Parameter | Description |
|-----------|-------------|
| `staged` | Review git staged changes |
| `files <file1> [file2...]` | Review specific files |
| `directory <path>` | Review all files in directory |
| `diff --base <ref> [--head <ref>]` | Review git diff |
| `diff --commit <ref>` | Review a specific commit |
| `security <path>` | Security-focused audit |
| `performance <path>` | Performance analysis |
| `architecture <path>` | Architecture review |

### Optional Flags

| Flag | Description |
|------|-------------|
| `--output <file>` | Save review to file (default: stdout) |
| `--format <md\|json>` | Output format (default: md) |
| `--focus <areas>` | Comma-separated focus areas |

## Review Focus Areas

When analyzing code, the review covers:

### Code Quality
- Code readability and maintainability
- Naming conventions and consistency
- Code duplication (DRY - Don't Repeat Yourself)
- Function/method complexity (cyclomatic complexity)
- Error handling patterns
- **KISS** - Keep It Simple, Stupid (avoid over-engineering)
- **YAGNI** - You Aren't Gonna Need It (no premature abstractions)

### Security (OWASP Top 10)
- SQL injection vulnerabilities
- Cross-site scripting (XSS)
- Authentication/authorization bypasses
- Insecure deserialization
- Sensitive data exposure
- Hardcoded secrets/credentials
- Command injection
- Path traversal

### Performance
- Algorithm efficiency (time/space complexity)
- Memory leaks and resource management
- Database query optimization (N+1 queries)
- Caching opportunities
- Async/concurrent processing patterns
- Resource cleanup and disposal

### Architecture & Design (SOLID Principles)
- **S**ingle Responsibility Principle - One class/function, one purpose
- **O**pen/Closed Principle - Open for extension, closed for modification
- **L**iskov Substitution Principle - Subtypes must be substitutable
- **I**nterface Segregation Principle - Small, focused interfaces
- **D**ependency Inversion Principle - Depend on abstractions

### Design Best Practices
- Clear and consistent API/interface design
- Appropriate abstraction levels
- Low coupling, high cohesion
- Proper separation of concerns
- Appropriate design patterns (not overused)
- Extensibility without over-engineering

### Best Practices
- Language-specific idioms
- Framework conventions
- Testing coverage indicators
- Documentation completeness

## Workflow

1. **Parse Request**: Identify the review type from user input
2. **Validate Prerequisites**: Check Codex CLI installation
3. **Execute Review**: Run the appropriate review script via Codex CLI
4. **Web Search Verification** (CRITICAL - Claude Code's responsibility):
   - Codex CLI does NOT have web search capability
   - After receiving Codex results, Claude Code MUST use WebSearch tool to verify findings
   - This step prevents false positives about dependency versions, best practices, CVEs, etc.
5. **Present Results**: Format and display the review findings with verified context
6. **Offer Actions**: Suggest follow-up actions (fix issues, create PR, etc.)

## Web Search Integration (MANDATORY)

**CRITICAL**: Before reporting ANY issue, Claude MUST verify findings using WebSearch to avoid false positives.

### When to Search

| Finding Type | What to Search |
|-------------|----------------|
| Dependency issues | Latest stable version, known vulnerabilities, deprecation status |
| Best practices | Current recommended patterns for the language/framework/version |
| Security vulnerabilities | CVE database, recent security advisories |
| Deprecated APIs | Official deprecation announcements, migration guides |
| Performance patterns | Current best practices, framework-specific optimizations |
| Design patterns | Latest recommendations for the specific tech stack |

### Search Examples

```
# Before flagging an outdated dependency
WebSearch: "lodash 4.17.21 latest version security vulnerabilities 2026"

# Before suggesting a pattern change
WebSearch: "React useEffect best practices 2026"

# Before reporting a security issue
WebSearch: "CVE-2024-xxxxx details affected versions"

# Before recommending architecture changes
WebSearch: "microservices vs monolith Node.js best practices 2026"
```

### Verification Rules

1. **ALWAYS verify dependency versions** before flagging as outdated
2. **ALWAYS check if a security pattern** is actually needed for the framework version in use
3. **ALWAYS confirm best practices** haven't changed with newer framework versions
4. **NEVER report false positives** - when uncertain, search first
5. **Include sources** in the review report for significant findings

## Example Workflows

### Example 1: Pre-commit Review with Web Verification

User: "Review my staged changes before I commit"

1. Check staged files:
```bash
git diff --cached --name-only
```

2. Run the review:
```bash
bash /home/ubuntu/workspace/codeai/.claude/skills/codex-code-review/scripts/review.sh staged
```

3. **Web Search Verification** (if review mentions dependencies):
   - Search: "lodash 4.17.21 security vulnerabilities 2026"
   - Search: "[package-name] latest version npm"

### Example 2: PR Review with Best Practices Verification

User: "Review the changes in my feature branch"

1. Review diff against main:
```bash
bash /home/ubuntu/workspace/codeai/.claude/skills/codex-code-review/scripts/review.sh diff --base main
```

2. **Web Search Verification** (for patterns/practices):
   - Search: "[framework] [pattern] best practices 2026"
   - Example: "React context vs Redux state management best practices 2026"

### Example 3: Security Audit with CVE Verification

User: "Check this directory for security issues"

1. Run security-focused review:
```bash
bash /home/ubuntu/workspace/codeai/.claude/skills/codex-code-review/scripts/review.sh security "src/api/"
```

2. **Web Search Verification** (for any security findings):
   - Search: "CVE-2024-XXXXX details affected versions"
   - Search: "[vulnerability type] [framework] mitigation 2026"
   - Search: "[dependency] security advisory"

### Example 4: Architecture Review with Design Verification

User: "Review the architecture of the auth module"

1. Run architecture review:
```bash
bash /home/ubuntu/workspace/codeai/.claude/skills/codex-code-review/scripts/review.sh architecture "src/auth/"
```

2. **Web Search Verification**:
   - Search: "JWT vs session authentication best practices 2026"
   - Search: "[framework] authentication patterns"
   - Search: "microservices auth patterns SOLID principles"

### Example 5: Full Codebase Review

User: "Do a comprehensive review of the entire src directory"

1. Run directory review:
```bash
bash /home/ubuntu/workspace/codeai/.claude/skills/codex-code-review/scripts/review.sh directory "src/"
```

2. Run architecture review:
```bash
bash /home/ubuntu/workspace/codeai/.claude/skills/codex-code-review/scripts/review.sh architecture "src/"
```

3. Run security audit:
```bash
bash /home/ubuntu/workspace/codeai/.claude/skills/codex-code-review/scripts/review.sh security "src/"
```

4. **Aggregate findings and verify critical issues via WebSearch**

## Output Format

Reviews are formatted in Markdown with sections:

```markdown
# Code Review Report

## Summary
Brief overview of findings

## Critical Issues
Issues requiring immediate attention

## Warnings
Important but non-critical issues

## Suggestions
Improvements and optimizations

## Positive Aspects
Well-written code patterns observed

## Recommendations
Actionable next steps
```

## Error Handling

- **Codex not installed**: Provide installation instructions
- **Not a git repo**: Advise initializing git or using --skip-git-repo-check (cautiously)
- **Rate limits**: Suggest waiting
- **Empty diff/staged**: Inform user no changes found to review

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CODEX_PERMISSION_MODE` | Permission mode: `auto`, `full-auto`, `bypass`, `ask` | `auto` |
| `CI` | Set to `true` in CI environments (enables bypass mode) | `false` |

## Notes

- Reviews are AI-generated and should be treated as suggestions
- **Always verify critical security findings via WebSearch before reporting**
- Combine with other tools (linters, SAST) for comprehensive analysis
- The skill auto-detects CI environments and adjusts permissions accordingly
- For v0.20+ of Codex CLI, `--full-auto` may still prompt for some operations
- Use `CODEX_PERMISSION_MODE=bypass` only in isolated CI environments

## Sources

- [Codex CLI Documentation](https://developers.openai.com/codex/cli/)
- [Codex CLI Security](https://developers.openai.com/codex/security/)
- [Command Line Options](https://developers.openai.com/codex/cli/reference/)
