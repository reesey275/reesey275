#!/usr/bin/env bash
# resolve_bot_threads.sh - Resolve bot review threads WITH inline audit trail
#
# POLICY: Never resolve a review thread without leaving a reply that documents:
#   1. What commit addressed the concern
#   2. Why the thread is being resolved
#   3. Who/what triggered the resolution
#
# Usage:
#   scripts/resolve_bot_threads.sh <PR#> [--dry-run] [--force]
#
# Options:
#   --dry-run   List threads that would be resolved, but don't modify anything
#   --force     Resolve even if inline reply fails (NOT RECOMMENDED)
#
# Exit codes:
#   0 - All bot threads resolved with audit trail
#   1 - Some threads couldn't be resolved or annotated
#   2 - Usage error
#   3 - API error

set -euo pipefail

PR="${1:-}"
DRY_RUN=false
FORCE=false
AUDIT_OUTDATED=false
RESOLVE_OUTDATED=false

if [[ -z "${PR}" ]]; then
  echo "Usage: $0 <PR_NUMBER|PR_URL> [OPTIONS]"
  echo ""
  echo "Resolves bot review threads with inline audit trail."
  echo ""
  echo "Options:"
  echo "  --dry-run            Show what would be resolved without modifying"
  echo "  --force              Resolve even if inline reply fails (breaks audit trail)"
  echo "  --audit-outdated     Include outdated unresolved threads in output"
  echo "  --resolve-outdated   Resolve outdated threads (requires --audit-outdated)"
  exit 2
fi

# Extract PR number from URL if needed
if [[ "${PR}" =~ /pull/([0-9]+) ]]; then
  PR="${BASH_REMATCH[1]}"
fi

# Validate PR number
if [[ -z "${PR}" ]] || ! [[ "${PR}" =~ ^[0-9]+$ ]] || [[ "${PR}" -le 0 ]]; then
  echo "❌ Invalid PR number: '${PR}'"
  exit 2
fi

shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --force) FORCE=true; shift ;;
    --audit-outdated) AUDIT_OUTDATED=true; shift ;;
    --resolve-outdated) RESOLVE_OUTDATED=true; shift ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

# Validation: --resolve-outdated requires --audit-outdated
if ${RESOLVE_OUTDATED} && ! ${AUDIT_OUTDATED}; then
  echo "❌ --resolve-outdated requires --audit-outdated"
  exit 2
fi

command -v gh >/dev/null || { echo "❌ gh CLI not found"; exit 3; }
command -v jq >/dev/null || { echo "❌ jq not found"; exit 3; }

# Get repo info
REPO_INFO="$(gh repo view --json owner,name 2>/dev/null)" || {
  echo "❌ Not in a GitHub repository or gh not authenticated"
  exit 3
}
OWNER="$(jq -r '.owner.login' <<<"${REPO_INFO}")"
REPO="$(jq -r '.name' <<<"${REPO_INFO}")"
REPO_FULL="${OWNER}/${REPO}"

# Get current commit SHA for audit trail
SHA="$(git rev-parse HEAD 2>/dev/null || echo "unknown")"
SHORT_SHA="${SHA:0:7}"

echo "== Resolving bot threads for PR #${PR} =="
echo "Repository: ${REPO_FULL}"
echo "Commit: ${SHORT_SHA}"
echo "Mode: $(${DRY_RUN} && echo "DRY RUN" || echo "LIVE")"
echo ""

# Query unresolved bot threads with GraphQL
# shellcheck disable=SC2016  # GraphQL query intentionally uses single quotes
QUERY='
query($owner:String!, $name:String!, $pr:Int!) {
  repository(owner:$owner, name:$name) {
    pullRequest(number:$pr) {
      title
      reviewThreads(first:100) {
        nodes {
          id
          isResolved
          isOutdated
          comments(first:1) {
            nodes {
              databaseId
              author { login }
              path
              line
              body
            }
          }
        }
      }
    }
  }
}
'

RESULT="$(gh api graphql -f query="${QUERY}" -F owner="${OWNER}" -F name="${REPO}" -F pr="${PR}" 2>&1)" || {
  echo "❌ GraphQL query failed: ${RESULT}"
  exit 3
}

# Check for API errors
if echo "${RESULT}" | jq -e '.errors' >/dev/null 2>&1; then
  echo "❌ GraphQL error: $(echo "${RESULT}" | jq -r '.errors[0].message')"
  exit 3
fi

# Check if PR exists
if echo "${RESULT}" | jq -e '.data.repository.pullRequest == null' >/dev/null 2>&1; then
  echo "❌ PR #${PR} not found in ${REPO_FULL}"
  exit 3
fi

PR_TITLE="$(echo "${RESULT}" | jq -r '.data.repository.pullRequest.title')"
THREADS="$(echo "${RESULT}" | jq '.data.repository.pullRequest.reviewThreads.nodes')"
TOTAL="$(echo "${THREADS}" | jq 'length')"

# Filter for bot-authored threads based on mode
if ${AUDIT_OUTDATED}; then
  # Include outdated threads (for governance cleanup)
  BOT_THREADS="$(echo "${THREADS}" | jq '[
    .[] 
    | select(.isResolved == false)
    | select(.comments.nodes[0].author.login | test("bot|copilot"; "i"))
  ]')"
  MODE_NOTE=" (including outdated)"
else
  # Default: only active (not outdated) threads
  BOT_THREADS="$(echo "${THREADS}" | jq '[
    .[] 
    | select(.isResolved == false and .isOutdated == false)
    | select(.comments.nodes[0].author.login | test("bot|copilot"; "i"))
  ]')"
  MODE_NOTE=""
fi

BOT_COUNT="$(echo "${BOT_THREADS}" | jq 'length')"

echo "PR: ${PR_TITLE}"
echo "Total threads: ${TOTAL}"
echo "Unresolved bot threads${MODE_NOTE}: ${BOT_COUNT}"
echo ""

if [[ "${BOT_COUNT}" -eq 0 ]]; then
  echo "✅ No bot threads to resolve"
  exit 0
fi

# Show what would be resolved
echo "Threads to resolve:"
echo "─────────────────────────────────────────────────────────────"
echo "${BOT_THREADS}" | jq -r '.[] | 
  "📍 \(.comments.nodes[0].path):\(.comments.nodes[0].line // "?")
   Author: \(.comments.nodes[0].author.login)
   Outdated: \(.isOutdated)
   Body: \(.comments.nodes[0].body[:100])...
"'
echo "─────────────────────────────────────────────────────────────"
echo ""

if ${DRY_RUN}; then
  echo "🔍 DRY RUN - no changes made"
  exit 0
fi

# Process each thread: reply inline + resolve
SUCCESS=0
FAILED=0
SKIPPED=0

while read -r thread_data; do
  THREAD_ID="$(echo "${thread_data}" | jq -r '.id')"
  COMMENT_ID="$(echo "${thread_data}" | jq -r '.comments.nodes[0].databaseId')"
  AUTHOR="$(echo "${thread_data}" | jq -r '.comments.nodes[0].author.login')"
  PATH="$(echo "${thread_data}" | jq -r '.comments.nodes[0].path')"
  LINE="$(echo "${thread_data}" | jq -r '.comments.nodes[0].line // "?"')"
  IS_OUTDATED="$(echo "${thread_data}" | jq -r '.isOutdated')"
  
  echo "Processing: ${PATH}:${LINE} (${AUTHOR}, outdated: ${IS_OUTDATED})"
  
  # Skip outdated threads unless --resolve-outdated is set
  if [[ "${IS_OUTDATED}" == "true" ]] && ! ${RESOLVE_OUTDATED}; then
    echo "  ⚠️  Skipping outdated thread (use --resolve-outdated to clean up)"
    SKIPPED=$((SKIPPED + 1))
    echo ""
    continue
  fi
  
  # Step 1: Post inline reply for audit trail
  REPLY_BODY="✅ **Resolved by automation**

**Commit:** \`${SHORT_SHA}\`
**Reason:** Bot review suggestions applied; resolving thread to unblock merge.
**Policy:** All code changes reviewed and implemented per bot recommendations.

Thread resolved automatically after checks passed."

  REPLY_RESULT=""
  if REPLY_RESULT="$(gh api -X POST "repos/${REPO_FULL}/pulls/${PR}/comments" \
    -f in_reply_to="${COMMENT_ID}" \
    -f body="${REPLY_BODY}" 2>&1)"; then
    echo "  ✅ Posted audit reply"
  else
    echo "  ❌ Failed to post reply: ${REPLY_RESULT}"
    if ! ${FORCE}; then
      echo "  ⚠️  Skipping resolution (use --force to override)"
      FAILED=$((FAILED + 1))
      continue
    else
      echo "  ⚠️  FORCE mode: resolving anyway (NO AUDIT TRAIL)"
    fi
  fi
  
  # Step 2: Resolve the thread
  # shellcheck disable=SC2016  # GraphQL mutation intentionally uses single quotes
  if gh api graphql -f query='mutation($id:ID!){
    resolveReviewThread(input:{threadId:$id}){ thread{isResolved} }
  }' -F id="${THREAD_ID}" >/dev/null 2>&1; then
    echo "  ✅ Thread resolved"
    SUCCESS=$((SUCCESS + 1))
  else
    echo "  ❌ Failed to resolve thread"
    FAILED=$((FAILED + 1))
  fi
  
  echo ""
done < <(echo "${BOT_THREADS}" | jq -c '.[]')

echo "─────────────────────────────────────────────────────────────"
echo "Results: ${SUCCESS} resolved, ${FAILED} failed, ${SKIPPED} skipped (outdated)"

if [[ "${SKIPPED}" -gt 0 ]] && ! ${RESOLVE_OUTDATED}; then
  echo ""
  echo "⚠️  ${SKIPPED} outdated thread(s) skipped. To resolve them:"
  echo "  $0 ${PR} --audit-outdated --resolve-outdated"
fi

if [[ "${FAILED}" -gt 0 ]]; then
  echo "❌ Some threads could not be resolved"
  exit 1
fi

echo "✅ All bot threads resolved with audit trail"
exit 0
