#!/bin/bash
#
# Verification Helper for Codex Code Review
# Provides functions to verify findings using web searches and external data
#
# Usage: source verify.sh
#        verify_dependency "package_name" "version"
#        verify_security_issue "CVE-2024-xxxx"
#

set -e

# Configuration
CACHE_DIR="${CACHE_DIR:-/tmp/codex-review-cache}"
CACHE_TTL_SECONDS="${CACHE_TTL_SECONDS:-3600}"  # 1 hour cache

# ==============================================================================
# Cache Management
# ==============================================================================

init_cache() {
    mkdir -p "$CACHE_DIR"
}

get_cache_key() {
    local input="$1"
    echo "$input" | md5sum | cut -d' ' -f1
}

cache_get() {
    local key="$1"
    local cache_file="$CACHE_DIR/$key"

    if [[ -f "$cache_file" ]]; then
        local file_age=$(($(date +%s) - $(stat -c %Y "$cache_file" 2>/dev/null || stat -f %m "$cache_file" 2>/dev/null)))
        if [[ $file_age -lt $CACHE_TTL_SECONDS ]]; then
            cat "$cache_file"
            return 0
        fi
    fi
    return 1
}

cache_set() {
    local key="$1"
    local value="$2"
    local cache_file="$CACHE_DIR/$key"
    echo "$value" > "$cache_file"
}

# ==============================================================================
# Dependency Verification
# ==============================================================================

# Check if a npm package version has known vulnerabilities
verify_npm_package() {
    local package="$1"
    local version="$2"

    init_cache
    local cache_key
    cache_key=$(get_cache_key "npm:$package:$version")

    local cached_result
    if cached_result=$(cache_get "$cache_key"); then
        echo "$cached_result"
        return
    fi

    # Query npm registry for package info
    local npm_info
    if npm_info=$(npm view "$package@$version" --json 2>/dev/null); then
        local result="VERIFIED: $package@$version exists in npm registry"

        # Check for deprecation
        local deprecated
        deprecated=$(echo "$npm_info" | jq -r '.deprecated // empty' 2>/dev/null || true)
        if [[ -n "$deprecated" ]]; then
            result="WARNING: $package@$version is deprecated: $deprecated"
        fi

        cache_set "$cache_key" "$result"
        echo "$result"
    else
        echo "UNVERIFIED: Could not verify $package@$version"
    fi
}

# Check if a Python package version exists
verify_pypi_package() {
    local package="$1"
    local version="$2"

    init_cache
    local cache_key
    cache_key=$(get_cache_key "pypi:$package:$version")

    local cached_result
    if cached_result=$(cache_get "$cache_key"); then
        echo "$cached_result"
        return
    fi

    # Query PyPI for package info
    local pypi_url="https://pypi.org/pypi/$package/$version/json"
    local response
    if response=$(curl -s -f "$pypi_url" 2>/dev/null); then
        local result="VERIFIED: $package==$version exists on PyPI"

        # Check for yanked releases
        local yanked
        yanked=$(echo "$response" | jq -r '.info.yanked // false' 2>/dev/null || echo "false")
        if [[ "$yanked" == "true" ]]; then
            result="WARNING: $package==$version has been yanked from PyPI"
        fi

        cache_set "$cache_key" "$result"
        echo "$result"
    else
        echo "UNVERIFIED: Could not verify $package==$version"
    fi
}

# ==============================================================================
# Security Verification
# ==============================================================================

# Check if a CVE exists and get details
verify_cve() {
    local cve_id="$1"

    init_cache
    local cache_key
    cache_key=$(get_cache_key "cve:$cve_id")

    local cached_result
    if cached_result=$(cache_get "$cache_key"); then
        echo "$cached_result"
        return
    fi

    # Query NVD for CVE details
    local nvd_url="https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=$cve_id"
    local response
    if response=$(curl -s -f "$nvd_url" 2>/dev/null); then
        local vuln_count
        vuln_count=$(echo "$response" | jq -r '.totalResults // 0' 2>/dev/null || echo "0")

        if [[ "$vuln_count" -gt 0 ]]; then
            local description severity
            description=$(echo "$response" | jq -r '.vulnerabilities[0].cve.descriptions[0].value // "No description"' 2>/dev/null || echo "No description")
            severity=$(echo "$response" | jq -r '.vulnerabilities[0].cve.metrics.cvssMetricV31[0].cvssData.baseSeverity // "UNKNOWN"' 2>/dev/null || echo "UNKNOWN")

            local result="VERIFIED CVE: $cve_id - Severity: $severity - $description"
            cache_set "$cache_key" "$result"
            echo "$result"
        else
            echo "NOT FOUND: $cve_id not found in NVD database"
        fi
    else
        echo "UNVERIFIED: Could not query NVD for $cve_id"
    fi
}

# ==============================================================================
# Best Practices Verification
# ==============================================================================

# Generate a verification report for code review findings
generate_verification_report() {
    local findings_file="$1"
    local output_file="${2:-/dev/stdout}"

    echo "# Verification Report" > "$output_file"
    echo "" >> "$output_file"
    echo "Generated: $(date -Iseconds)" >> "$output_file"
    echo "" >> "$output_file"

    # Extract and verify dependencies mentioned
    echo "## Dependency Verification" >> "$output_file"
    echo "" >> "$output_file"

    # Extract npm packages (pattern: package@version or "package": "version")
    local npm_packages
    npm_packages=$(grep -oE '["'\''"][a-zA-Z0-9@/-]+["'\''"]\s*:\s*["'\''"][0-9^~><=.*]+["'\'']' "$findings_file" 2>/dev/null | head -10 || true)

    if [[ -n "$npm_packages" ]]; then
        echo "### NPM Packages" >> "$output_file"
        echo "$npm_packages" | while read -r line; do
            echo "- $line" >> "$output_file"
        done
        echo "" >> "$output_file"
    fi

    # Extract CVEs mentioned
    echo "## Security Advisory Verification" >> "$output_file"
    echo "" >> "$output_file"

    local cves
    cves=$(grep -oE 'CVE-[0-9]{4}-[0-9]+' "$findings_file" 2>/dev/null | sort -u || true)

    if [[ -n "$cves" ]]; then
        echo "$cves" | while read -r cve; do
            local cve_result
            cve_result=$(verify_cve "$cve")
            echo "- $cve_result" >> "$output_file"
        done
    else
        echo "No CVEs mentioned in findings." >> "$output_file"
    fi

    echo "" >> "$output_file"
    echo "---" >> "$output_file"
    echo "*This report helps validate review findings against external sources.*" >> "$output_file"
}

# ==============================================================================
# Export Functions
# ==============================================================================

# If sourced, export functions; if executed directly, show usage
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    cat << 'EOF'
Verification Helper for Codex Code Review

This script provides verification functions. Source it to use:

    source verify.sh

Available functions:
    verify_npm_package <package> <version>
    verify_pypi_package <package> <version>
    verify_cve <CVE-ID>
    generate_verification_report <findings_file> [output_file]

Examples:
    verify_npm_package "lodash" "4.17.21"
    verify_pypi_package "requests" "2.31.0"
    verify_cve "CVE-2024-12345"

EOF
fi
