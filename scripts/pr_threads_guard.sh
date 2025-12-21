#!/usr/bin/env bash
# pr_threads_guard.sh - Enforce Copilot/bot review thread resolution before merge
#
# POLICY: PRs cannot advance while any review thread is in an "active" state.
# Active = (isResolved=false AND isOutdated=false)
#
# CRITICAL CONSTRAINT:
#   Agents can NEVER resolve threads. Only humans can set isResolved=true.
#   This is the mandatory human-in-the-loop checkpoint when AI makes mistakes.
#   Agents may: push fixes (making threads outdated), reply with rationale.
#   Agents must: stop and wait for human to resolve in GitHub UI.
#
# MODES:
#   --check (default)         Read-only: lists blocking threads, no mutations
#   --resolve-bot-threads     Write: reply to and resolve bot threads (HUMAN ONLY)
#     --annotate              (required with resolve) Adds rationale before resolving
#     --force                 Resolve without annotation (REQUIRES force registry)
#   --strict                  Fail on isResolved=false regardless of outdated status
#                             AUTO-ENABLED when AGENT_CONTEXT=true or CI=true
#
# Usage:
#   scripts/pr_threads_guard.sh <PR#>                                    # Check only
#   scripts/pr_threads_guard.sh <PR#> --check                            # Explicit check
#   scripts/pr_threads_guard.sh <PR#> --resolve-bot-threads --annotate   # Reply + resolve
#   scripts/pr_threads_guard.sh <PR#> --resolve-bot-threads --force      # Bypass annotation (logged)
#
# Exit codes:
#   0 - No active threads (or all resolved successfully)
#   1 - Active threads exist (policy violation)
#   2 - Usage error
#   3 - API error
#   4 - Annotation failed (--force not provided)
#   5 - Force blocked (agent context without override)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TAGS_ROOT="${TAGS_ROOT:-$(dirname "${SCRIPT_DIR}")}"

# Temp file cleanup trap
cleanup_temp_files() {
  rm -f "/tmp/pr_title_$$" 2>/dev/null || true
}
trap cleanup_temp_files EXIT

# Source force registry for --force operations
FORCE_REGISTRY="${TAGS_ROOT}/governance/force_registry.sh"
if [[ -f "${FORCE_REGISTRY}" ]]; then
  # shellcheck source=governance/force_registry.sh
  # shellcheck disable=SC1091  # External governance file not always present
  source "${FORCE_REGISTRY}"
fi

# ─────────────────────────────────────────────────────────────
# Argument parsing
# ─────────────────────────────────────────────────────────────

PR="${1:-}"
MODE="check"  # Default mode
STRICT=false
ANNOTATE=false
FORCE=false

# Auto-enable strict mode for agents/CI (unresolved threads are always blocking)
if [[ "${AGENT_CONTEXT:-}" == "true" || "${CI:-}" == "true" ]]; then
  STRICT=true
fi

print_usage() {
  cat << 'USAGE'
Usage: pr_threads_guard.sh <PR_NUMBER|PR_URL> [OPTIONS]

MODES (mutually exclusive):
  --check                   Read-only: list blocking threads (default)
  --resolve-bot-threads     Write: reply to and resolve bot/copilot threads

OPTIONS:
  --annotate                Required with --resolve-bot-threads: add rationale
  --force                   Bypass annotation requirement (logged to force registry)
  --strict                  Fail on any unresolved thread (even if outdated)

EXIT CODES:
  0 = Success (no active threads, or all resolved)
  1 = Active threads exist (policy violation)
  2 = Usage error
  3 = API error
  4 = Annotation failed (--force not provided)
  5 = Force blocked (agent context without override)

EXAMPLES:
  # Check for blocking threads
  ./pr_threads_guard.sh 373

  # Resolve bot threads with annotation
  ./pr_threads_guard.sh 373 --resolve-bot-threads --annotate

  # Force resolve without annotation (emergency, logged)
  export FORCE_OVERRIDE_TOKEN="FORCE-20251221-ci-unblock"
  ./pr_threads_guard.sh 373 --resolve-bot-threads --force

POLICY:
  Every thread must end in exactly one state:
  1. FIXED (code pushed under thread → becomes outdated)
  2. RESOLVED (reply with rationale → resolve)
  3. DEFERRED (create issue, reply "Tracked in #XXX" → resolve)
USAGE
}

# Check for help flag first (before PR validation)
if [[ "${PR}" == "-h" || "${PR}" == "--help" ]]; then
  print_usage
  exit 0
fi

if [[ -z "${PR}" ]]; then
  print_usage
  exit 2
fi

# Extract PR number from URL if needed
if [[ "${PR}" =~ /pull/([0-9]+) ]]; then
  PR="${BASH_REMATCH[1]}"
fi

# Validate PR number
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
    --check)
      MODE="check"
      shift
      ;;
    --resolve-bot-threads)
      MODE="resolve"
      shift
      ;;
    --annotate)
      ANNOTATE=true
      shift
      ;;
    --force)
      FORCE=true
      shift
      ;;
    --strict)
      STRICT=true
      shift
      ;;
    -h|--help)
      print_usage
      exit 0
      ;;
    *)
      echo "❌ Unknown argument: $1"
      print_usage
      exit 2
      ;;
  esac
done

# CRITICAL: Block agents from using --resolve-bot-threads entirely
# Thread resolution is a HUMAN-ONLY operation
if [[ "${MODE}" == "resolve" && "${AGENT_CONTEXT:-}" == "true" ]]; then
  echo "❌ BLOCKED: Agents cannot use --resolve-bot-threads"
  echo ""
  echo "   Thread resolution is a HUMAN-ONLY operation."
  echo "   This is the mandatory human-in-the-loop checkpoint."
  echo ""
  echo "   Agent-allowed operations:"
  echo "     1. scripts/pr_threads_guard.sh $PR --check"
  echo "     2. Push code changes (threads become outdated)"
  echo "     3. Reply with rationale via gh api graphql (comments only)"
  echo "     4. Wait for human to resolve in GitHub UI"
  echo ""
  exit 5
fi

# Validate mode + options
if [[ "${MODE}" == "resolve" && "${ANNOTATE}" == "false" && "${FORCE}" == "false" ]]; then
  echo "❌ --resolve-bot-threads requires either --annotate or --force"
  echo ""
  echo "  --annotate: Add rationale comment before resolving (preferred)"
  echo "  --force:    Bypass annotation (logged to force registry)"
  exit 2
fi

if [[ "${ANNOTATE}" == "true" && "${FORCE}" == "true" ]]; then
  echo "❌ Cannot use both --annotate and --force"
  echo "   --force bypasses annotation; they are mutually exclusive"
  exit 2
fi

# ─────────────────────────────────────────────────────────────
# Prerequisites
# ─────────────────────────────────────────────────────────────

command -v gh >/dev/null || { echo "❌ gh CLI not found"; exit 3; }
command -v jq >/dev/null || { echo "❌ jq not found"; exit 3; }

# Get repo info from current directory
REPO_INFO="$(gh repo view --json owner,name 2>/dev/null)" || {
  echo "❌ Not in a GitHub repository or gh not authenticated"
  exit 3
}
OWNER="$(jq -r '.owner.login' <<<"${REPO_INFO}")"
REPO="$(jq -r '.name' <<<"${REPO_INFO}")"

# ─────────────────────────────────────────────────────────────
# GraphQL Queries
# ─────────────────────────────────────────────────────────────

# shellcheck disable=SC2016  # GraphQL queries intentionally use single quotes
QUERY_THREADS='
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

# shellcheck disable=SC2016  # GraphQL queries intentionally use single quotes
MUTATION_ADD_COMMENT='
mutation($threadId: ID!, $body: String!) {
  addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $threadId, body: $body}) {
    comment {
      id
      body
    }
  }
}
'

# shellcheck disable=SC2016  # GraphQL queries intentionally use single quotes
MUTATION_RESOLVE='
mutation($threadId: ID!) {
  resolveReviewThread(input: {threadId: $threadId}) {
    thread {
      id
      isResolved
    }
  }
}
'

# ─────────────────────────────────────────────────────────────
# Fetch all threads (paginated)
# ─────────────────────────────────────────────────────────────

fetch_all_threads() {
  local all_threads="[]"
  local cursor=""
  local pr_title=""
  local page=1

  while true; do
    local query_args=(-f query="${QUERY_THREADS}" -F owner="${OWNER}" -F name="${REPO}" -F number="${PR}")
    if [[ -n "${cursor}" ]]; then
      query_args+=(-F after="${cursor}")
    fi

    local result
    result="$(gh api graphql "${query_args[@]}" 2>&1)" || {
      echo "❌ GraphQL query failed (page ${page}): ${result}"
      exit 3
    }

    # Check for API errors
    if echo "${result}" | jq -e '.errors' >/dev/null 2>&1; then
      echo "❌ API error:"
      echo "${result}" | jq -r '.errors[].message'
      exit 3
    fi

    # Check if pullRequest exists
    if echo "${result}" | jq -e '.data.repository.pullRequest == null' >/dev/null 2>&1; then
      echo "❌ Pull request #${PR} not found in ${OWNER}/${REPO}"
      echo "   Possible causes: wrong PR number, wrong repository, or insufficient permissions"
      exit 3
    fi

    # Extract title (only on first page)
    if [[ -z "${pr_title}" ]]; then
      pr_title="$(echo "${result}" | jq -r '.data.repository.pullRequest.title // "(unknown)"')"
      echo "${pr_title}" > /tmp/pr_title_$$
    fi

    # Extract threads from this page
    local page_threads
    page_threads="$(echo "${result}" | jq '.data.repository.pullRequest.reviewThreads.nodes')"
    all_threads="$(echo "${all_threads}" "${page_threads}" | jq -s 'add')"

    # Check for next page
    local has_next
    has_next="$(echo "${result}" | jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.hasNextPage')"
    if [[ "${has_next}" != "true" ]]; then
      break
    fi

    cursor="$(echo "${result}" | jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.endCursor')"
    page=$((page + 1))

    # Safety limit
    if [[ ${page} -gt 50 ]]; then
      echo "⚠️  Warning: Stopped pagination after 50 pages (5000 threads)"
      break
    fi
  done

  echo "${all_threads}"
}

# ─────────────────────────────────────────────────────────────
# Filter for active threads
# ─────────────────────────────────────────────────────────────

filter_active_threads() {
  local threads="$1"
  local strict="$2"

  if [[ "${strict}" == "true" ]]; then
    # Strict: any unresolved thread counts
    echo "${threads}" | jq '[.[] | select(.isResolved == false)]'
  else
    # Standard: only unresolved AND not outdated
    echo "${threads}" | jq '[.[] | select(.isResolved == false and .isOutdated == false)]'
  fi
}

# ─────────────────────────────────────────────────────────────
# Display thread info
# ─────────────────────────────────────────────────────────────

display_threads() {
  local threads="$1"
  local count
  count="$(echo "${threads}" | jq 'length')"

  if [[ "${count}" -eq 0 ]]; then
    return 0
  fi

  echo ""
  echo "─────────────────────────────────────────────────────────────"
  while read -r thread; do
    local path_file
    path_file="$(echo "${thread}" | jq -r '.path // "(no path)"')"
    local line
    line="$(echo "${thread}" | jq -r '.line // "(no line)"')"
    local author
    author="$(echo "${thread}" | jq -r '.comments.nodes[0].author.login // "(unknown)"')"
    local body
    body="$(echo "${thread}" | jq -r '.comments.nodes[0].body // "(no body)"' | head -c 200)"
    local is_outdated
    is_outdated="$(echo "${thread}" | jq -r '.isOutdated')"
    local thread_id
    thread_id="$(echo "${thread}" | jq -r '.id')"

    echo ""
    echo "📍 ${path_file}:${line}"
    echo "   ID: ${thread_id}"
    echo "   Author: ${author}"
    echo "   Outdated: ${is_outdated}"
    echo "   Comment: ${body}..."
  done < <(echo "${threads}" | jq -c '.[]')
  echo ""
  echo "─────────────────────────────────────────────────────────────"
}

# ─────────────────────────────────────────────────────────────
# Add annotation comment to thread
# ─────────────────────────────────────────────────────────────

annotate_thread() {
  local thread_id="$1"
  local author="$2"
  local body_preview="$3"

  # Build annotation message
  local annotation
  annotation="**Governance Resolution**: This review thread by @${author} has been acknowledged.

Original concern: ${body_preview}...

**Resolution**: Addressed via automated governance enforcement. Thread resolved as part of PR merge readiness protocol.

---
*Resolved by pr_threads_guard.sh --resolve-bot-threads --annotate*
*Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")*"

  local result
  result="$(gh api graphql -f query="${MUTATION_ADD_COMMENT}" -F threadId="${thread_id}" -F body="${annotation}" 2>&1)" || {
    echo "❌ Failed to add annotation to thread ${thread_id}: ${result}"
    return 1
  }

  # Check for errors
  if echo "${result}" | jq -e '.errors' >/dev/null 2>&1; then
    echo "❌ API error adding annotation:"
    echo "${result}" | jq -r '.errors[].message'
    return 1
  fi

  echo "   ✅ Annotated thread ${thread_id}"
  return 0
}

# ─────────────────────────────────────────────────────────────
# Resolve a thread (HUMAN ONLY - agents are blocked)
# ─────────────────────────────────────────────────────────────

resolve_thread() {
  local thread_id="$1"

  # CRITICAL: Agents can NEVER resolve threads
  # This is the mandatory human-in-the-loop for AI review feedback
  if [[ "${AGENT_CONTEXT:-}" == "true" ]]; then
    echo "❌ BLOCKED: Agents cannot resolve review threads."
    echo ""
    echo "   Thread resolution is a HUMAN-ONLY operation."
    echo "   This is the mandatory checkpoint when AI makes mistakes."
    echo ""
    echo "   Agent options:"
    echo "     1. Push code changes (threads become outdated)"
    echo "     2. Add comment via gh api graphql (no resolution)"
    echo "     3. Stop and wait for human to resolve in GitHub UI"
    echo ""
    echo "   Thread ID: ${thread_id}"
    return 1
  fi

  local result
  result="$(gh api graphql -f query="${MUTATION_RESOLVE}" -F threadId="${thread_id}" 2>&1)" || {
    echo "❌ Failed to resolve thread ${thread_id}: ${result}"
    return 1
  }

  # Check for errors
  if echo "${result}" | jq -e '.errors' >/dev/null 2>&1; then
    echo "❌ API error resolving thread:"
    echo "${result}" | jq -r '.errors[].message'
    return 1
  fi

  echo "   ✅ Resolved thread ${thread_id}"
  return 0
}

# ─────────────────────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────────────────────

echo "== Fetching review threads for PR #${PR} =="
THREADS="$(fetch_all_threads)"
PR_TITLE="$(cat /tmp/pr_title_$$ 2>/dev/null || echo "(unknown)")"
rm -f /tmp/pr_title_$$

# shellcheck disable=SC2034  # TOTAL used for context/debugging
TOTAL="$(echo "${THREADS}" | jq 'length')"

# Calculate all three thread states for visibility
# THREADS contains ALL threads - filter for unresolved ones
UNRESOLVED_TOTAL="$(echo "${THREADS}" | jq '[.[] | select(.isResolved == false)] | length')"
UNRESOLVED_ACTIVE="$(echo "${THREADS}" | jq '[.[] | select(.isResolved == false and .isOutdated == false)] | length')"
UNRESOLVED_OUTDATED="$(echo "${THREADS}" | jq '[.[] | select(.isResolved == false and .isOutdated == true)] | length')"

# Get threads that are blocking based on mode
ACTIVE_THREADS="$(filter_active_threads "${THREADS}" "${STRICT}")"
ACTIVE_COUNT="$(echo "${ACTIVE_THREADS}" | jq 'length')"

if [[ "${STRICT}" == "true" ]]; then
  MODE_DESC="STRICT (ALL unresolved threads block)"
else
  MODE_DESC="STANDARD (only active threads block)"
fi

echo ""
echo "== PR #${PR}: ${PR_TITLE} =="
echo "Mode: ${MODE_DESC}"
echo "Operation: ${MODE}"
echo ""
echo "Thread States:"
echo "  📊 Unresolved Total:    ${UNRESOLVED_TOTAL}"
echo "  🔴 Unresolved Active:   ${UNRESOLVED_ACTIVE} (not outdated)"
echo "  🟡 Unresolved Outdated: ${UNRESOLVED_OUTDATED} (code changed under them)"
echo "  🚫 Blocking Count:      ${ACTIVE_COUNT} (based on mode)"

# ─────────────────────────────────────────────────────────────
# MODE: CHECK (read-only)
# ─────────────────────────────────────────────────────────────

if [[ "${MODE}" == "check" ]]; then
  if [[ "${ACTIVE_COUNT}" -eq 0 ]]; then
    echo ""
    echo "✅ No blocking review threads. Safe to proceed."
    exit 0
  fi

  echo ""
  echo "❌ POLICY VIOLATION: ${ACTIVE_COUNT} thread(s) must be handled before merge."
  echo ""
  echo "Each thread must be:"
  echo "  1. Made OUTDATED (push code change under it), or"
  echo "  2. RESOLVED (reply with rationale, then resolve in GitHub UI), or"
  echo "  3. DEFERRED (create issue, reply with 'Tracked in #XXX', resolve in GitHub UI)"

  # Context-aware help message
  if [[ "${AGENT_CONTEXT:-}" == "true" || "${CI:-}" == "true" ]]; then
    echo ""
    echo "⚠️  AGENT/CI MODE: You can only push code changes or add replies."
    echo "   Thread resolution (isResolved=true) is a HUMAN-ONLY operation."
    echo "   Wait for human to resolve threads in GitHub UI."
  else
    echo ""
    echo "Tip: Use --resolve-bot-threads --annotate to resolve programmatically"
  fi

  display_threads "${ACTIVE_THREADS}"

  echo ""
  echo "Action required: Handle all threads before proceeding."
  exit 1
fi

# ─────────────────────────────────────────────────────────────
# MODE: RESOLVE (write)
# ─────────────────────────────────────────────────────────────

if [[ "${MODE}" == "resolve" ]]; then
  if [[ "${ACTIVE_COUNT}" -eq 0 ]]; then
    echo ""
    echo "✅ No active review threads to resolve."
    exit 0
  fi

  echo ""
  echo "🔧 Resolving ${ACTIVE_COUNT} active thread(s)..."

  # Force validation
  if [[ "${FORCE}" == "true" ]]; then
    echo ""
    echo "⚠️  --force specified: bypassing annotation requirement"

    # Check if force registry is available
    if ! declare -f validate_force_permitted >/dev/null 2>&1; then
      echo "❌ Force registry not loaded. Cannot use --force safely."
      echo "   Ensure governance/force_registry.sh exists and is sourceable."
      exit 5
    fi

    # Validate force is permitted (blocks agents without override)
    if ! validate_force_permitted "pr_threads_guard"; then
      exit 5
    fi
  fi

  RESOLVED_COUNT=0
  FAILED_COUNT=0
  ANNOTATION_FAILED=false

  while read -r thread; do
    thread_id="$(echo "${thread}" | jq -r '.id')"
    author="$(echo "${thread}" | jq -r '.comments.nodes[0].author.login // "(unknown)"')"
    body_preview="$(echo "${thread}" | jq -r '.comments.nodes[0].body // ""' | head -c 100)"
    path_file="$(echo "${thread}" | jq -r '.path // "(no path)"')"
    line="$(echo "${thread}" | jq -r '.line // "?"')"

    echo ""
    echo "📍 Processing: ${path_file}:${line} (by ${author})"

    # Step 1: Annotate (unless --force)
    if [[ "${ANNOTATE}" == "true" ]]; then
      if ! annotate_thread "${thread_id}" "${author}" "${body_preview}"; then
        echo "   ❌ Annotation failed for thread ${thread_id}"
        ANNOTATION_FAILED=true
        FAILED_COUNT=$((FAILED_COUNT + 1))
        continue  # Skip resolution if annotation failed
      fi
    elif [[ "${FORCE}" == "true" ]]; then
      echo "   ⚠️  Skipping annotation (--force)"
      # Log to force registry
      log_force_operation \
        "pr_threads_guard" \
        "PR#${PR}:${thread_id}" \
        "Resolved thread without annotation. Author: ${author}, File: ${path_file}:${line}" \
        "Add retroactive annotation via GitHub UI or API. Thread ID: ${thread_id}"
    fi

    # Step 2: Resolve
    if resolve_thread "${thread_id}"; then
      RESOLVED_COUNT=$((RESOLVED_COUNT + 1))
    else
      FAILED_COUNT=$((FAILED_COUNT + 1))
    fi

  done < <(echo "${ACTIVE_THREADS}" | jq -c '.[]')

  echo ""
  echo "─────────────────────────────────────────────────────────────"
  echo "Resolution Summary:"
  echo "  Resolved: ${RESOLVED_COUNT}"
  echo "  Failed: ${FAILED_COUNT}"
  echo "─────────────────────────────────────────────────────────────"

  if [[ "${FAILED_COUNT}" -gt 0 ]]; then
    if [[ "${ANNOTATION_FAILED}" == "true" && "${FORCE}" == "false" ]]; then
      echo ""
      echo "❌ Some annotations failed. Use --force to bypass annotation requirement."
      echo "   (Force operations are logged to governance/force_registry.sh)"
      exit 4
    fi
    echo ""
    echo "❌ Some threads could not be resolved."
    exit 1
  fi

  echo ""
  echo "✅ All ${RESOLVED_COUNT} threads resolved successfully."
  exit 0
fi
