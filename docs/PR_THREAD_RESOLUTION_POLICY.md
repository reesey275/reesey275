# PR Thread Resolution Policy

## Problem Statement

GitHub's GraphQL `resolveReviewThread` mutation performs a **silent state flip** - it marks threads as resolved without leaving any human-readable audit trail. This creates governance issues:

- No visible record of **why** a thread was resolved
- No reference to **what commit** addressed the concern
- No indication of **who** or **what process** triggered the resolution
- Future code archaeology becomes impossible

## Policy: Audit Trail Required

**RULE:** Never resolve a review thread without leaving an inline reply that documents:

1. **What commit** addressed the concern (SHA reference)
2. **Why** the thread is being resolved (rationale)
3. **Who/what** triggered the resolution (human vs automation)

## Implementation

### Tool: `resolve_bot_threads.sh`

The proper way to resolve bot/Copilot review threads:

```bash
# Check what would be resolved (dry run)
scripts/resolve_bot_threads.sh <PR#> --dry-run

# Resolve with audit trail
scripts/resolve_bot_threads.sh <PR#>

# Force resolution even if reply fails (NOT RECOMMENDED)
scripts/resolve_bot_threads.sh <PR#> --force
```

**What it does:**

1. Queries unresolved bot threads (GraphQL)
2. For each thread:
   - Posts inline reply with commit SHA and rationale (REST API)
   - Resolves the thread (GraphQL mutation)
3. Fails if any inline reply cannot be posted (unless `--force`)

**Example inline reply:**

```markdown
✅ **Resolved by automation**

**Commit:** `36ef22d`
**Reason:** Bot review suggestions applied; resolving thread to unblock merge.
**Policy:** All code changes reviewed and implemented per bot recommendations.

Thread resolved automatically after checks passed.
```

### Tool: `pr_threads_guard.sh`

Enhanced guard script with resolution capability:

```bash
# Check mode (read-only)
scripts/pr_threads_guard.sh <PR#>

# Strict mode (fail on any unresolved thread, even outdated)
scripts/pr_threads_guard.sh <PR#> --strict

# Resolve mode (delegates to resolve_bot_threads.sh)
scripts/pr_threads_guard.sh <PR#> --resolve-bot-threads --annotate
```

**Policy enforcement:**

- `--resolve-bot-threads` **requires** `--annotate` flag
- Exits with error if used without `--annotate`
- Prevents silent resolutions that violate governance

## Workflow Integration

### Option A: Manual resolution workflow

1. Developer reviews bot threads
2. Applies code fixes
3. Commits changes
4. Runs: `scripts/resolve_bot_threads.sh <PR#>`
5. Inline replies are posted with commit SHA
6. Threads are resolved
7. Auto-merge proceeds

### Option B: Automated CI workflow

```yaml
- name: Check for active bot threads
  run: scripts/pr_threads_guard.sh ${{ github.event.pull_request.number }}
  
- name: Resolve bot threads with audit trail
  if: failure()
  run: scripts/resolve_bot_threads.sh ${{ github.event.pull_request.number }}
```

## Why This Matters

### Code Archaeology

Future developers can:
- See **exactly** which commit addressed a concern
- Understand **why** the resolution was acceptable
- Trace the **decision-making process**

### Governance Compliance

Organizations with audit requirements can:
- Demonstrate proper review processes
- Show clear decision trails
- Meet regulatory standards

### Team Trust

Transparent resolution builds trust:
- No "silent fixes" or unexplained changes
- Clear communication of reasoning
- Documented rationale for future reference

## Anti-Patterns (DO NOT DO THIS)

### ❌ Silent GraphQL Resolution

```bash
# BAD: No audit trail
gh api graphql -f query='mutation($id:ID!){
  resolveReviewThread(input:{threadId:$id}){ thread{isResolved} }
}' -F id="$THREAD_ID"
```

**Problem:** Future developers see "resolved" with no explanation.

### ❌ Batch Resolution Without Context

```bash
# BAD: Resolves all threads without documenting each
for id in $THREAD_IDS; do
  resolve_thread "$id"  # No inline reply, no rationale
done
```

**Problem:** Loses specificity about which fix addressed which concern.

### ❌ PR-Level Comment Only

```bash
# WEAK: One comment for all resolutions
gh pr comment <PR#> -b "Resolved all bot threads in commit abc123"
```

**Problem:** Doesn't link specific fixes to specific concerns. Harder to trace during code archaeology.

## Best Practices

### ✅ Inline Reply + Resolution

```bash
# GOOD: Reply documents the fix, then resolve
gh api -X POST "repos/OWNER/REPO/pulls/PR/comments" \
  -f in_reply_to="$COMMENT_ID" \
  -f body="Fixed in commit $SHA: [explanation]"

gh api graphql -f query='mutation($id:ID!){
  resolveReviewThread(input:{threadId:$id}){ thread{isResolved} }
}' -F id="$THREAD_ID"
```

### ✅ Use Provided Tooling

```bash
# BEST: Automated audit trail
scripts/resolve_bot_threads.sh <PR#>
```

**Advantages:**
- Consistent audit format
- Error handling for failed replies
- Dry-run mode for safety
- Policy enforcement built-in

## FAQ

### Q: Why not just rely on "Outdated" status?

**A:** "Outdated" only means the diff hunk changed - it doesn't prove the concern was addressed. You can change whitespace and make a comment "outdated" without fixing anything.

### Q: Can I resolve threads without replies in emergencies?

**A:** Use `--force` flag, but document in a follow-up commit message:

```bash
scripts/resolve_bot_threads.sh <PR#> --force

git commit --allow-empty -m "POLICY: Emergency thread resolution
- Resolved bot threads without inline replies due to [reason]
- See discussion in [link to issue/chat]
- Audit trail documented in this commit message"
```

### Q: What about human reviewer threads?

**A:** This policy applies to **all** review threads, but automation should only resolve **bot** threads. Human threads require human judgment and should be resolved through discussion.

### Q: Does this slow down the workflow?

**A:** Initial setup adds ~5 seconds per PR. Long-term benefit:
- Faster code archaeology (no digging through git history)
- Clearer decision rationale (reduces confusion)
- Compliance with audit requirements (saves hours in reviews)

## References

- GitHub REST API: [Create Review Comment](https://docs.github.com/en/rest/pulls/comments#create-a-review-comment-for-a-pull-request)
- GitHub GraphQL API: [resolveReviewThread mutation](https://docs.github.com/en/graphql/reference/mutations#resolvereviewthread)
- `in_reply_to` parameter: Links comment to thread for proper nesting

## Changelog

- **2025-12-21**: Initial policy document
  - Created `resolve_bot_threads.sh` for audit trail automation
  - Enhanced `pr_threads_guard.sh` with `--resolve-bot-threads --annotate` mode
  - Established "audit trail required" as mandatory policy
