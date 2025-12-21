#!/usr/bin/env bash
# pr_threads_guard.sh - Enforce Copilot/bot review thread resolution before merge
#
# POLICY: PRs cannot advance while any review thread is in an "active" state.
# Active = (isResolved=false AND isOutdated=false)
#
# Strict mode (--strict): Fail on isResolved=false regardless of outdated status.
# This is required if branch protection has "Conversations must be resolved."
#
# Usage:
#   scripts/pr_threads_guard.sh <PR#>                  # Check mode (read-only)
#   scripts/pr_threads_guard.sh <PR#> --strict         # Strict check mode
#   scripts/pr_threads_guard.sh <PR#> --resolve-bot-threads --annotate  # Resolve with audit
#
# Exit codes:
#   0 - No active threads (safe to proceed)
#   1 - Active threads exist (policy violation) OR resolution failed
#   2 - Usage error
#   3 - API error
#
# IMPORTANT: --resolve-bot-threads requires --annotate to leave audit trail.
# Use scripts/resolve_bot_threads.sh for the actual resolution with audit trail.

set -euo pipefail

PR="${1:-}"
STRICT=false
RESOLVE_MODE=false
ANNOTATE=false

if [[ -z "${PR}" ]]; then
  echo "Usage: $0 <PR_NUMBER|PR_URL> [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --strict                Fail on any unresolved thread (even if outdated)"
  echo "  --resolve-bot-threads   Resolve bot threads (requires --annotate)"
  echo "  --annotate              Leave audit trail when resolving (mandatory with --resolve-bot-threads)"
  echo ""
  echo "Examples:"
  echo "  $0 82                   # Check for active threads"
  echo "  $0 82 --strict          # Check all unresolved threads"
  echo "  $0 82 --resolve-bot-threads --annotate  # Resolve with audit trail"
  echo ""
  echo "Exit codes:"
  echo "  0 = No active threads or all resolved"
  echo "  1 = Active threads exist or resolution failed"
  exit 2
fi

# Extract PR number from URL if needed
if [[ "${PR}" =~ /pull/([0-9]+) ]]; then
  PR="${BASH_REMATCH[1]}"
fi

# Fix B: Validate PR number is non-empty, numeric, and positive
if [[ -z "${PR}" ]]; then
  echo "❌ PR number is empty after URL extraction"
  exit 2
fi
if ! [[ "${PR}" =~ ^[0-9]+$ ]]; then
  echo "❌ PR number must be numeric, got: '${PR}'"
  exit 2
fi
if [[ "${PR}" -le 0 ]]; then
  echo "❌ PR number must be positive, got: ${PR}"
  exit 2
fi

shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --strict) STRICT=true; shift ;;
    --resolve-bot-threads) RESOLVE_MODE=true; shift ;;
    --annotate) ANNOTATE=true; shift ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

# Enforce audit trail policy
if ${RESOLVE_MODE} && ! ${ANNOTATE}; then
  echo "❌ POLICY VIOLATION: --resolve-bot-threads requires --annotate"
  echo ""
  echo "REASON: Resolving threads without audit trail is governance malpractice."
  echo "        Each resolution must leave an inline reply documenting:"
  echo "        1. What commit addressed the concern"
  echo "        2. Why the thread is being resolved"
  echo "        3. Who/what triggered the resolution"
  echo ""
  echo "Use: $0 ${PR} --resolve-bot-threads --annotate"
  echo "Or:  scripts/resolve_bot_threads.sh ${PR}"
  exit 2
fi

command -v gh >/dev/null || { echo "❌ gh CLI not found"; exit 3; }
command -v jq >/dev/null || { echo "❌ jq not found"; exit 3; }

# Get repo info from current directory
REPO_INFO="$(gh repo view --json owner,name 2>/dev/null)" || {
  echo "❌ Not in a GitHub repository or gh not authenticated"
  exit 3
}
OWNER="$(jq -r '.owner.login' <<<"${REPO_INFO}")"
REPO="$(jq -r '.name' <<<"${REPO_INFO}")"

# Fix A: GraphQL query with pagination support (cursor-based)
# Accumulates all threads across pages to handle PRs with >100 threads
QUERY='
query($owner: String!, $name: String!, $number: Int!, $after: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      title
      reviewThreads(first: 100, after: $after) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          comments(first: 1) {
            nodes {
              author { login }
              body
            }
          }
        }
      }
    }
  }
}
'

# Paginated fetch: loop until no more pages
ALL_THREADS="[]"
CURSOR=""
PR_TITLE=""
PAGE=1

while true; do
  # Build query args
  QUERY_ARGS=(-f query="${QUERY}" -F owner="${OWNER}" -F name="${REPO}" -F number="${PR}")
  if [[ -n "${CURSOR}" ]]; then
    QUERY_ARGS+=(-F after="${CURSOR}")
  fi

  RESULT="$(gh api graphql "${QUERY_ARGS[@]}" 2>&1)" || {
    echo "❌ GraphQL query failed (page ${PAGE}): ${RESULT}"
    exit 3
  }

  # Check for API errors
  if echo "${RESULT}" | jq -e '.errors' >/dev/null 2>&1; then
    echo "❌ API error:"
    echo "${RESULT}" | jq -r '.errors[].message'
    exit 3
  fi

  # Fix D: Check if pullRequest is null (wrong PR, wrong repo, or permissions issue)
  if echo "${RESULT}" | jq -e '.data.repository.pullRequest == null' >/dev/null 2>&1; then
    echo "❌ Pull request #${PR} not found in ${OWNER}/${REPO}"
    echo "   Possible causes: wrong PR number, wrong repository, or insufficient permissions"
    exit 3
  fi

  # Extract title (only on first page)
  if [[ -z "${PR_TITLE}" ]]; then
    PR_TITLE="$(echo "${RESULT}" | jq -r '.data.repository.pullRequest.title // "(unknown)"')"
  fi

  # Extract threads from this page
  PAGE_THREADS="$(echo "${RESULT}" | jq '.data.repository.pullRequest.reviewThreads.nodes')"
  ALL_THREADS="$(echo "${ALL_THREADS}" "${PAGE_THREADS}" | jq -s 'add')"

  # Check for next page
  HAS_NEXT="$(echo "${RESULT}" | jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.hasNextPage')"
  if [[ "${HAS_NEXT}" != "true" ]]; then
    break
  fi

  CURSOR="$(echo "${RESULT}" | jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.endCursor')"
  PAGE=$((PAGE + 1))

  # Safety limit: prevent infinite loops
  if [[ ${PAGE} -gt 50 ]]; then
    echo "⚠️  Warning: Stopped pagination after 50 pages (5000 threads)"
    break
  fi
done

THREADS="${ALL_THREADS}"
TOTAL="$(echo "${THREADS}" | jq 'length')"

# Count active threads based on mode
if [[ "${STRICT}" == "true" ]]; then
  # Strict: any unresolved thread counts
  ACTIVE_FILTER='select(.isResolved == false)'
  MODE_DESC="STRICT (unresolved, including outdated)"
else
  # Standard: only unresolved AND not outdated
  ACTIVE_FILTER='select(.isResolved == false and .isOutdated == false)'
  MODE_DESC="STANDARD (unresolved AND not outdated)"
fi

ACTIVE_THREADS="$(echo "${THREADS}" | jq "[.[] | ${ACTIVE_FILTER}]")"
ACTIVE_COUNT="$(echo "${ACTIVE_THREADS}" | jq 'length')"

echo "== PR #${PR}: ${PR_TITLE} =="
echo "Mode: ${MODE_DESC}"
echo "Total threads: ${TOTAL}"
echo "Active threads: ${ACTIVE_COUNT}"
echo ""

if [[ "${ACTIVE_COUNT}" -eq 0 ]]; then
  echo "✅ No active review threads. Safe to proceed."
  exit 0
fi

# Policy violation - list active threads
echo "❌ POLICY VIOLATION: ${ACTIVE_COUNT} active review thread(s) must be handled."
echo ""
echo "Each thread must be:"
echo "  1. Made OUTDATED (push code change under it), or"
echo "  2. RESOLVED (reply with rationale, then resolve), or"
echo "  3. DEFERRED (create issue, reply with 'Tracked in #XXX', resolve)"
echo ""
if ${RESOLVE_MODE} && ${ANNOTATE}; then
  echo "🔄 RESOLVE MODE enabled - will attempt to resolve bot threads with audit trail"
  echo ""
fi
echo "─────────────────────────────────────────────────────────────"

# Fix C: Use process substitution to avoid subshell variable scope issues
# This ensures any variables set in the loop are accessible after the loop
while read -r thread; do
  PATH_FILE="$(echo "${thread}" | jq -r '.path // "(no path)"')"
  LINE="$(echo "${thread}" | jq -r '.line // "(no line)"')"
  AUTHOR="$(echo "${thread}" | jq -r '.comments.nodes[0].author.login // "(unknown)"')"
  BODY="$(echo "${thread}" | jq -r '.comments.nodes[0].body // "(no body)"' | head -c 200)"
  IS_OUTDATED="$(echo "${thread}" | jq -r '.isOutdated')"

  echo ""
  echo "📍 ${PATH_FILE}:${LINE}"
  echo "   Author: ${AUTHOR}"
  echo "   Outdated: ${IS_OUTDATED}"
  echo "   Comment: ${BODY}..."
done < <(echo "${ACTIVE_THREADS}" | jq -c '.[]')

echo ""
echo "─────────────────────────────────────────────────────────────"
echo ""

# If in resolve mode, delegate to resolve_bot_threads.sh
if ${RESOLVE_MODE} && ${ANNOTATE}; then
  echo "🔄 Delegating to resolve_bot_threads.sh for audit trail..."
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  
  if [[ -x "${SCRIPT_DIR}/resolve_bot_threads.sh" ]]; then
    exec "${SCRIPT_DIR}/resolve_bot_threads.sh" "${PR}"
  else
    echo "❌ resolve_bot_threads.sh not found or not executable"
    echo "   Expected: ${SCRIPT_DIR}/resolve_bot_threads.sh"
    exit 3
  fi
fi

echo "Action required: Handle all threads before proceeding."
echo ""
echo "To auto-resolve bot threads with audit trail:"
echo "  scripts/resolve_bot_threads.sh ${PR}"
exit 1
