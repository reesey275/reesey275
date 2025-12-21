#!/usr/bin/env bash
set -euo pipefail

# File a CI breach issue using gh CLI.
# Usage:
#   scripts/file_ci_breach_issue.sh "SHA_LIST" "FAILED_CHECKS" "DEADLINE_ISO"
# Example:
#   scripts/file_ci_breach_issue.sh "eb059b8,f7a9ddc" "Lint,docs-quality" "2025-12-21T09:30:00Z"

repo="reesey275/reesey275"
sha_list="${1:-}"
failed_checks="${2:-}"
deadline="${3:-}"

if [[ -z "${sha_list}" || -z "${failed_checks}" || -z "${deadline}" ]]; then
  printf "Usage: %s \"SHA_LIST\" \"FAILED_CHECKS\" \"DEADLINE_ISO\"\n" "$(basename "$0")"
  exit 2
fi

# Construct body on the fly to avoid external dependencies
body=$(cat <<EOF
# CI Breach — Unauthorized Merge to \`main\` with Failing Checks

This issue records a governance breach: a change landed on \`main\` while CI checks were failing or not enforced.

## Commit SHA(s)
- ${sha_list}

## CI Checks (failed)
- ${failed_checks}

## Root Cause
- Merge to \`main\` bypassed PR pipeline and/or required checks did not cover the failing workflows.

## Action Required
- The author must submit a PR that fully remediates the broken state or reverts their own changes.

## Enforcement
- TAGS governance prohibits bypassing protected CI gates. This is a Class 1 breach.

## Deadline
- ${deadline}

## Evidence
- See recent commits and latest runs in repository Actions history.

## Acceptance Criteria
- PR merged that restores green checks (Lint + docs-quality at minimum).
- Branch protection validated with required checks covering critical workflows.
- Incident closed with links to fix PR and postmortem notes.
EOF
)

printf "Creating issue in %s...\n" "$repo"
# Create the issue
issue_url=$(gh issue create --title "CI Breach — Unauthorized Merge to main with Failing Checks" \
  --body "$body" --repo "$repo" --json url | jq -r '.url')

printf "Issue created: %s\n" "$issue_url"
printf "Add a comment and close it after remediation, or leave open until the fix PR lands.\n"
