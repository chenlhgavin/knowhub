#!/bin/bash
#
# Setup Helper for Codex Code Review
# Validates and configures the environment for Codex CLI
#
# Usage: setup.sh [--check | --install | --auth]
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ==============================================================================
# Check Functions
# ==============================================================================

check_node() {
    if command -v node &> /dev/null; then
        local version
        version=$(node --version)
        log_success "Node.js installed: $version"
        return 0
    else
        log_error "Node.js not found"
        return 1
    fi
}

check_npm() {
    if command -v npm &> /dev/null; then
        local version
        version=$(npm --version)
        log_success "npm installed: $version"
        return 0
    else
        log_error "npm not found"
        return 1
    fi
}

check_codex() {
    if command -v codex &> /dev/null; then
        local version
        version=$(codex --version 2>/dev/null || echo "unknown")
        log_success "Codex CLI installed: $version"
        return 0
    else
        log_error "Codex CLI not found"
        return 1
    fi
}

check_auth() {
    # Codex CLI handles its own authentication via stored auth.json
    # Just verify Codex CLI is available; auth is managed internally
    if command -v codex &> /dev/null; then
        log_success "Codex CLI available (auth managed by CLI)"
        return 0
    fi

    log_warning "Codex CLI not installed - cannot verify auth"
    return 1
}

check_git() {
    if git rev-parse --is-inside-work-tree &> /dev/null; then
        log_success "Inside git repository: $(git rev-parse --show-toplevel)"
        return 0
    else
        log_warning "Not inside a git repository"
        return 1
    fi
}

# ==============================================================================
# Installation Functions
# ==============================================================================

install_codex() {
    log_info "Installing Codex CLI..."

    if ! check_npm; then
        log_error "npm is required to install Codex CLI"
        echo ""
        echo "Install Node.js first: https://nodejs.org/"
        return 1
    fi

    npm install -g @openai/codex

    if check_codex; then
        log_success "Codex CLI installed successfully"
    else
        log_error "Installation failed"
        return 1
    fi
}

# ==============================================================================
# Authentication Functions
# ==============================================================================

setup_auth() {
    log_info "Codex CLI manages authentication internally via ~/.codex/auth.json"
    echo ""
    echo "If you need to re-authenticate, run:"
    echo "  codex login"
    echo ""
    echo "Or set an API key:"
    echo "  export OPENAI_API_KEY='your-api-key-here'"
    echo ""
}

# Kept for backwards compatibility
setup_api_key() { setup_auth; }
setup_device_code() { setup_auth; }
setup_oauth() { setup_auth; }

# ==============================================================================
# Main Functions
# ==============================================================================

run_full_check() {
    echo "=========================================="
    echo "  Codex Code Review - Environment Check"
    echo "=========================================="
    echo ""

    local all_ok=true

    echo "Prerequisites:"
    echo "--------------"
    check_node || all_ok=false
    check_npm || all_ok=false
    check_codex || all_ok=false
    echo ""

    echo "Authentication:"
    echo "---------------"
    check_auth || all_ok=false
    echo ""

    echo "Git Repository:"
    echo "---------------"
    check_git || all_ok=false
    echo ""

    echo "=========================================="
    if $all_ok; then
        log_success "All checks passed! Ready to run code reviews."
    else
        log_warning "Some checks failed. Run 'setup.sh --install' or 'setup.sh --auth' to fix."
    fi
    echo "=========================================="
}

show_usage() {
    cat << 'EOF'
Codex Code Review - Setup Helper

Usage: setup.sh [command]

Commands:
  --check     Run full environment check (default)
  --install   Install Codex CLI
  --auth      Configure authentication
  --help      Show this help message

Environment Variables:
  OPENAI_API_KEY          OpenAI API key (recommended for headless)
  CODEX_API_KEY           Alternative API key variable
  CODEX_PERMISSION_MODE   Permission mode: auto, full-auto, bypass, ask
  CI                      Set to 'true' in CI environments

Examples:
  # Check environment
  bash setup.sh --check

  # Install Codex CLI
  bash setup.sh --install

  # Setup authentication
  bash setup.sh --auth

  # Run with bypass mode in CI
  CI=true CODEX_PERMISSION_MODE=bypass bash review.sh staged

EOF
}

# ==============================================================================
# Entry Point
# ==============================================================================

main() {
    case "${1:-}" in
        --check|"")
            run_full_check
            ;;
        --install)
            install_codex
            ;;
        --auth)
            setup_auth
            ;;
        --help|-h)
            show_usage
            ;;
        *)
            log_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
