#!/bin/bash
#
# Codex Code Review Script
# Performs AI-powered code reviews using OpenAI Codex CLI in headless mode
#
# Usage: review.sh <mode> [options]
#
# Modes:
#   staged                    - Review git staged changes
#   files <file1> [file2...]  - Review specific files
#   directory <path>          - Review directory
#   diff --base <ref>         - Review git diff
#   security <path>           - Security-focused audit
#   performance <path>        - Performance analysis
#   architecture <path>       - Architecture review
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
DEFAULT_FORMAT="md"
CODEX_CMD="codex"

# Permission modes
PERMISSION_MODE="${CODEX_PERMISSION_MODE:-auto}"  # auto, full-auto, bypass, ask
CI_MODE="${CI:-false}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ==============================================================================
# Helper Functions
# ==============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

show_usage() {
    cat << 'EOF'
Codex Code Review Script

Usage: review.sh <mode> [options]

Modes:
  staged                      Review git staged changes
  files <file1> [file2...]    Review specific files
  directory <path>            Review all files in directory
  diff --base <ref>           Review git diff against base ref
  diff --commit <ref>         Review a specific commit
  security <path>             Security-focused audit
  performance <path>          Performance analysis
  architecture <path>         Architecture review

Options:
  --output <file>             Save review to file (default: stdout)
  --format <md|json>          Output format (default: md)
  --focus <areas>             Comma-separated focus areas
  --help                      Show this help message

Examples:
  review.sh staged
  review.sh files src/app.js src/utils.js
  review.sh directory src/components
  review.sh diff --base main
  review.sh diff --commit HEAD~1
  review.sh security src/api/
  review.sh performance src/
  review.sh architecture src/

EOF
}

# ==============================================================================
# Prerequisite Checks
# ==============================================================================

check_codex_installed() {
    if ! command -v "$CODEX_CMD" &> /dev/null; then
        log_error "Codex CLI is not installed."
        echo ""
        echo "Install Codex CLI with one of these methods:"
        echo "  npm install -g @openai/codex"
        echo "  pnpm add -g @openai/codex"
        echo "  brew install openai/tap/codex"
        echo ""
        echo "See: https://developers.openai.com/codex/cli/"
        exit 1
    fi
    log_info "Codex CLI found: $(which $CODEX_CMD)"
}

check_authentication() {
    # Codex CLI handles its own authentication via stored auth.json
    # No explicit API key or login required
    log_info "Using Codex CLI built-in authentication"
    return 0
}

check_git_repo() {
    if ! git rev-parse --is-inside-work-tree &> /dev/null; then
        log_error "Not inside a git repository."
        echo "Codex requires a git repository for safety reasons."
        echo "Initialize with: git init"
        exit 1
    fi
    log_info "Git repository detected: $(git rev-parse --show-toplevel)"
}

run_prerequisites() {
    log_info "Checking prerequisites..."
    check_codex_installed
    check_authentication
    check_git_repo
    log_success "All prerequisites met"
    echo ""
}

# ==============================================================================
# Permission Configuration
# ==============================================================================

get_permission_args() {
    local args=()

    case "$PERMISSION_MODE" in
        bypass)
            # Full bypass for CI/automation (use with caution)
            args+=("--dangerously-bypass-approvals-and-sandbox")
            log_warning "Using bypass mode - all permissions granted"
            ;;
        full-auto)
            # Standard full-auto mode (workspace access, prompts for external)
            args+=("--full-auto")
            log_info "Using full-auto mode"
            ;;
        ask)
            # Interactive mode (prompts for all actions)
            args+=("--sandbox" "workspace-write" "--ask-for-approval" "always")
            log_info "Using interactive mode"
            ;;
        auto|*)
            # Auto-detect: use bypass in CI, full-auto otherwise
            if [[ "$CI_MODE" == "true" ]]; then
                args+=("--dangerously-bypass-approvals-and-sandbox")
                log_info "CI environment detected - using bypass mode"
            else
                args+=("--full-auto")
                log_info "Using full-auto mode"
            fi
            ;;
    esac

    echo "${args[@]}"
}

# ==============================================================================
# Review Prompt Builders
# ==============================================================================

build_base_prompt() {
    local review_type="$1"
    local target="$2"

    cat << EOF
You are performing a comprehensive code review. Analyze the code for:

1. **Code Quality**
   - Readability and maintainability
   - Naming conventions (clear, consistent, meaningful)
   - Code duplication (DRY - Don't Repeat Yourself)
   - Function complexity (keep functions small and focused)
   - Error handling patterns
   - KISS - Keep solutions simple, avoid over-engineering
   - YAGNI - Don't build for hypothetical future needs

2. **Architecture & Design (SOLID Principles)**
   - Single Responsibility: Each class/module/function should have one reason to change
   - Open/Closed: Open for extension, closed for modification
   - Liskov Substitution: Subtypes must be substitutable for their base types
   - Interface Segregation: Prefer small, focused interfaces over large ones
   - Dependency Inversion: Depend on abstractions, not concretions

3. **Interface & Module Design**
   - Clear, intuitive, and consistent APIs/interfaces
   - Appropriate abstraction level (not too much, not too little)
   - Low coupling between modules, high cohesion within modules
   - Proper separation of concerns and clear dependency direction
   - Extensibility for likely changes without over-engineering

4. **Best Practices**
   - Language idioms and conventions
   - Framework-specific patterns
   - Testing considerations
   - Documentation where necessary (not excessive)

5. **Potential Issues**
   - Bugs and edge cases
   - Type safety
   - Null/undefined handling
   - Resource leaks

Format your response as a structured Markdown report with these sections:
- Summary (1-2 sentences)
- Critical Issues (if any - bugs, security, data loss risks)
- Warnings (important but non-critical)
- Suggestions (improvements and optimizations)
- Positive Aspects (well-written patterns observed)

Be specific with line numbers and code references where applicable.
Prioritize actionable feedback over minor style issues.
EOF
}

build_security_prompt() {
    cat << 'EOF'
You are performing a SECURITY AUDIT. Focus on identifying vulnerabilities:

**OWASP Top 10 Checks:**
1. Injection (SQL, NoSQL, OS, LDAP)
2. Broken Authentication
3. Sensitive Data Exposure
4. XML External Entities (XXE)
5. Broken Access Control
6. Security Misconfiguration
7. Cross-Site Scripting (XSS)
8. Insecure Deserialization
9. Using Components with Known Vulnerabilities
10. Insufficient Logging & Monitoring

**Additional Checks:**
- Hardcoded secrets/credentials
- Insecure cryptography
- Path traversal
- Command injection
- CSRF vulnerabilities
- Rate limiting gaps

Format as a security report with severity levels: CRITICAL, HIGH, MEDIUM, LOW.
Include CVE references where applicable.
EOF
}

build_performance_prompt() {
    cat << 'EOF'
You are performing a PERFORMANCE ANALYSIS. Identify:

1. **Algorithm Efficiency**
   - Time complexity issues (O(n²), O(n³), etc.)
   - Space complexity concerns
   - Unnecessary iterations

2. **Memory Management**
   - Memory leaks
   - Large object creation in loops
   - Unreleased resources

3. **I/O Operations**
   - Database query efficiency (N+1 queries)
   - File handling
   - Network calls

4. **Concurrency**
   - Race conditions
   - Blocking operations
   - Thread safety

5. **Caching Opportunities**
   - Repeated computations
   - Static data that could be cached
   - Memoization candidates

Provide specific recommendations with expected impact.
EOF
}

build_architecture_prompt() {
    cat << 'EOF'
You are performing an ARCHITECTURE REVIEW. Evaluate against these principles:

1. **SOLID Principles**
   - Single Responsibility: Does each class/module have one reason to change?
   - Open/Closed: Can behavior be extended without modification?
   - Liskov Substitution: Are subtypes truly substitutable?
   - Interface Segregation: Are interfaces focused and minimal?
   - Dependency Inversion: Do high-level modules depend on abstractions?

2. **Design Simplicity (KISS, YAGNI, DRY)**
   - KISS: Is the solution unnecessarily complex?
   - YAGNI: Are there features/abstractions built for hypothetical future needs?
   - DRY: Is there code duplication that should be abstracted?
   - Are there over-engineered solutions that could be simpler?

3. **Interface Design**
   - Are APIs/interfaces clear and intuitive?
   - Is the contract well-defined and consistent?
   - Are method signatures minimal and focused?
   - Is the public surface area appropriately sized?

4. **Module Organization**
   - Separation of concerns
   - Layer boundaries (presentation, business, data)
   - Appropriate module boundaries
   - Clear dependency direction

5. **Coupling & Cohesion**
   - Tight coupling issues (excessive dependencies)
   - Low cohesion modules (unrelated responsibilities)
   - Circular dependencies
   - God classes/modules

6. **Extensibility (without over-engineering)**
   - Can the code be extended for likely changes?
   - Are extension points at appropriate places?
   - Is there unnecessary flexibility that adds complexity?

Provide architectural recommendations with rationale.
Flag over-engineering as seriously as under-engineering.
EOF
}

# ==============================================================================
# Review Execution Functions
# ==============================================================================

execute_codex_review() {
    local prompt="$1"
    local output_file="${2:-}"
    local format="${3:-md}"

    log_info "Executing Codex review..."

    # Get permission arguments based on mode
    local permission_args
    permission_args=$(get_permission_args)

    # Build codex exec command
    local codex_args=()

    # Add permission args (split by space)
    for arg in $permission_args; do
        codex_args+=("$arg")
    done

    # Add exec command
    codex_args+=("exec")

    # Add JSON output if requested
    if [[ "$format" == "json" ]]; then
        codex_args+=("--json")
    fi

    log_info "Codex args: ${codex_args[*]}"

    # Execute and capture output
    local result
    if result=$($CODEX_CMD "${codex_args[@]}" "$prompt" 2>&1); then
        if [[ -n "$output_file" ]]; then
            echo "$result" > "$output_file"
            log_success "Review saved to: $output_file"
        else
            echo "$result"
        fi
    else
        log_error "Codex execution failed"
        echo "$result" >&2
        return 1
    fi
}

# ==============================================================================
# Review Mode Handlers
# ==============================================================================

review_staged() {
    log_info "Reviewing git staged changes..."

    # Check if there are staged changes
    local staged_files
    staged_files=$(git diff --cached --name-only)

    if [[ -z "$staged_files" ]]; then
        log_warning "No staged changes found."
        echo "Stage changes with: git add <files>"
        exit 0
    fi

    log_info "Files staged for review:"
    echo "$staged_files" | while read -r file; do
        echo "  - $file"
    done
    echo ""

    # Get the diff content
    local diff_content
    diff_content=$(git diff --cached)

    local prompt
    prompt=$(cat << EOF
$(build_base_prompt "staged" "$staged_files")

Review the following staged changes (git diff --cached):

\`\`\`diff
$diff_content
\`\`\`

Files being reviewed:
$staged_files
EOF
)

    execute_codex_review "$prompt" "$OUTPUT_FILE" "$FORMAT"
}

review_files() {
    local files=("$@")

    if [[ ${#files[@]} -eq 0 ]]; then
        log_error "No files specified"
        show_usage
        exit 1
    fi

    log_info "Reviewing specified files..."

    # Validate files exist
    local file_contents=""
    for file in "${files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "File not found: $file"
            exit 1
        fi
        log_info "  - $file"
        file_contents+="

### File: $file

\`\`\`
$(cat "$file")
\`\`\`
"
    done
    echo ""

    local prompt
    prompt=$(cat << EOF
$(build_base_prompt "files" "${files[*]}")

Review the following files:
$file_contents
EOF
)

    execute_codex_review "$prompt" "$OUTPUT_FILE" "$FORMAT"
}

review_directory() {
    local dir_path="$1"

    if [[ -z "$dir_path" ]]; then
        log_error "No directory specified"
        show_usage
        exit 1
    fi

    if [[ ! -d "$dir_path" ]]; then
        log_error "Directory not found: $dir_path"
        exit 1
    fi

    log_info "Reviewing directory: $dir_path"

    # List files in directory
    local files
    files=$(find "$dir_path" -type f \( -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" -o -name "*.py" -o -name "*.go" -o -name "*.java" -o -name "*.rs" -o -name "*.rb" -o -name "*.php" -o -name "*.c" -o -name "*.cpp" -o -name "*.h" -o -name "*.cs" -o -name "*.swift" -o -name "*.kt" \) | head -50)

    if [[ -z "$files" ]]; then
        log_warning "No supported source files found in: $dir_path"
        exit 0
    fi

    log_info "Files found for review:"
    echo "$files" | while read -r file; do
        echo "  - $file"
    done
    echo ""

    local prompt
    prompt=$(cat << EOF
$(build_base_prompt "directory" "$dir_path")

Review the code in directory: $dir_path

Focus on overall patterns and issues across the codebase.
Identify cross-file issues like:
- Inconsistent patterns between files
- Duplicated code across modules
- Missing abstractions
- Circular dependencies

Files to review:
$files
EOF
)

    execute_codex_review "$prompt" "$OUTPUT_FILE" "$FORMAT"
}

review_diff() {
    local base_ref=""
    local head_ref="HEAD"
    local commit_ref=""

    # Parse diff arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --base)
                base_ref="$2"
                shift 2
                ;;
            --head)
                head_ref="$2"
                shift 2
                ;;
            --commit)
                commit_ref="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done

    local diff_content
    local diff_description

    if [[ -n "$commit_ref" ]]; then
        log_info "Reviewing commit: $commit_ref"
        diff_content=$(git show "$commit_ref" --format="" 2>/dev/null || git diff "$commit_ref^..$commit_ref" 2>/dev/null)
        diff_description="Commit $commit_ref"
    elif [[ -n "$base_ref" ]]; then
        log_info "Reviewing diff: $base_ref...$head_ref"
        diff_content=$(git diff "$base_ref...$head_ref")
        diff_description="Changes from $base_ref to $head_ref"
    else
        log_error "Must specify --base <ref> or --commit <ref>"
        show_usage
        exit 1
    fi

    if [[ -z "$diff_content" ]]; then
        log_warning "No differences found"
        exit 0
    fi

    echo ""

    local prompt
    prompt=$(cat << EOF
$(build_base_prompt "diff" "$diff_description")

Review the following git diff ($diff_description):

\`\`\`diff
$diff_content
\`\`\`

Focus on:
- Changes that might introduce bugs
- Changes that affect existing functionality
- Consistency with existing code style
EOF
)

    execute_codex_review "$prompt" "$OUTPUT_FILE" "$FORMAT"
}

review_security() {
    local target_path="${1:-.}"

    log_info "Running security audit on: $target_path"
    echo ""

    local prompt
    prompt=$(cat << EOF
$(build_security_prompt)

Perform a security audit on the code in: $target_path

IMPORTANT: Be thorough but avoid false positives. Consider:
- The context and intended use of the code
- Whether proper input validation exists elsewhere
- Framework-provided protections
EOF
)

    execute_codex_review "$prompt" "$OUTPUT_FILE" "$FORMAT"
}

review_performance() {
    local target_path="${1:-.}"

    log_info "Running performance analysis on: $target_path"
    echo ""

    local prompt
    prompt=$(cat << EOF
$(build_performance_prompt)

Analyze performance in: $target_path

Focus on actual performance issues, not micro-optimizations.
Prioritize issues by potential impact.
EOF
)

    execute_codex_review "$prompt" "$OUTPUT_FILE" "$FORMAT"
}

review_architecture() {
    local target_path="${1:-.}"

    log_info "Running architecture review on: $target_path"
    echo ""

    local prompt
    prompt=$(cat << EOF
$(build_architecture_prompt)

Review the architecture of: $target_path

Consider the codebase as a whole and provide actionable recommendations.
EOF
)

    execute_codex_review "$prompt" "$OUTPUT_FILE" "$FORMAT"
}

# ==============================================================================
# Main Entry Point
# ==============================================================================

main() {
    # Global options
    OUTPUT_FILE=""
    FORMAT="$DEFAULT_FORMAT"
    FOCUS_AREAS=""

    # Parse global options first
    local args=()
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --output)
                OUTPUT_FILE="$2"
                shift 2
                ;;
            --format)
                FORMAT="$2"
                shift 2
                ;;
            --focus)
                FOCUS_AREAS="$2"
                shift 2
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                args+=("$1")
                shift
                ;;
        esac
    done

    # Restore arguments
    set -- "${args[@]}"

    if [[ $# -eq 0 ]]; then
        show_usage
        exit 1
    fi

    # Run prerequisite checks
    run_prerequisites

    # Route to appropriate handler
    local mode="$1"
    shift

    case "$mode" in
        staged)
            review_staged
            ;;
        files)
            review_files "$@"
            ;;
        directory|dir)
            review_directory "$@"
            ;;
        diff)
            review_diff "$@"
            ;;
        security|sec)
            review_security "$@"
            ;;
        performance|perf)
            review_performance "$@"
            ;;
        architecture|arch)
            review_architecture "$@"
            ;;
        *)
            log_error "Unknown mode: $mode"
            show_usage
            exit 1
            ;;
    esac
}

# Run main with all arguments
main "$@"
