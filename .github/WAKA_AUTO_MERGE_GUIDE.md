# WakaTime Auto-Merge Workflow Guide

## Table of Contents
- [Quick Start](#quick-start)
- [Known Limitations](#wakatime-free-tier-limitations)
- [Daily Automation Schedule](#daily-automation-schedule)
- [Problem & Solution](#problem-statement)
- [Implementation](#implementation-steps)
- [Testing](#step-4-test-the-fix)

**Status**: ✅ Working  
**Last Verified**: 2025-12-21 (PR #107 auto-merged successfully)  
**Current Schedule**: Midnight UTC daily (via cron)
**Known Limitation**: WakaTime free tier stats are 2-4 hours behind (caching behavior)

## Quick Start

The workflow is fully functional and requires zero manual intervention:
- ✅ Runs automatically at **midnight UTC** every day
- ✅ Fetches stats from WakaTime API
- ✅ Creates/updates PR with auto-merge enabled
- ✅ All checks run automatically and merge when passing
- **Note**: Stats will be 2-4 hours delayed on free tier (see [WakaTime Free Tier Limitations](#wakatime-free-tier-limitations))

## Problem Statement

### Symptoms
- WakaTime workflow creates PRs successfully
- Required checks show "Expected — Waiting for status to be reported"
- Checks never execute, auto-merge never triggers
- PRs remain open indefinitely despite no actual problems

### Root Cause
**GitHub Security Policy**: Pull requests created with `GITHUB_TOKEN` (bot token) do **NOT** trigger `pull_request` workflow events.

This is intentional to prevent infinite workflow loops:
```text
Workflow runs → Creates PR → Triggers workflow → Creates PR → ∞
```

**Impact**: 
- `lint.yml` requires `pull_request` event to run
- `docs-quality.yml` requires `pull_request` event to run  
- No workflows = no commit status = auto-merge blocked

### Why workflow_dispatch Didn't Work
Initial attempt (PR #93) added `workflow_dispatch` trigger to workflows, allowing manual execution:
```yaml
on:
  pull_request:
  workflow_dispatch:  # Added this
```

**Problem**: `workflow_dispatch` runs execute successfully but don't report commit status back to the PR. Auto-merge requires commit status from `pull_request` events.

## Solution: Fine-Grained Personal Access Token

### Why PATs Work
Personal Access Tokens (PATs) are **not** subject to bot token restrictions:
- ✅ PRs created with PAT **DO** trigger `pull_request` workflows
- ✅ Workflows run automatically when PR is created
- ✅ Commit status is reported properly
- ✅ Auto-merge executes when all checks pass

### Fine-Grained vs Classic PAT
**Use Fine-Grained PATs** (recommended):
- ✅ Scoped to specific repositories only
- ✅ Granular permissions (principle of least privilege)
- ✅ Expiration enforcement (security best practice)
- ✅ Audit trail per repository
- ✅ Can be revoked without affecting other repos

**Avoid Classic PATs**:
- ❌ Full account access
- ❌ Cannot limit to specific repositories
- ❌ Overly broad permissions

## Implementation Steps

### Step 1: Create Fine-Grained PAT

1. **Navigate to token creation**:
   - Go to https://github.com/settings/personal-access-tokens/new
   - Or: Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token

2. **Configure token**:
   - **Token name**: `WakaTime Workflow` (or descriptive name)
   - **Expiration**: 90 days recommended (or custom)
   - **Description**: `Auto-merge WakaTime stats PRs with proper workflow triggering`

3. **Repository access**:
   - **Select**: "Only select repositories"
   - **Choose**: `reesey275/reesey275` (or your repo)

4. **Repository permissions** (exact requirements):

   ```
   Actions: Read and write          # Trigger workflow_dispatch
   Commit statuses: Read and write  # Optional but helpful
   Contents: Read and write          # Git operations (commit, push, branch)
   Metadata: Read-only               # Auto-included, required
   Pull requests: Read and write     # Create/update PRs, enable auto-merge
   ```

5. **Generate and copy token**:
   - Click "Generate token"
   - **CRITICAL**: Copy token immediately (shown only once)
   - Store securely (you'll need it for next step)

### Step 2: Add PAT to Repository Secrets

```bash
cd ~/Projects/reesey275

# Add secret (will prompt for token)
gh secret set WAKA_PAT
# Paste the token when prompted

# Verify secret was added
gh secret list | grep WAKA_PAT
# Should show: WAKA_PAT  Updated 2025-12-21
```

**Alternative** (via GitHub UI):
1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `WAKA_PAT`
4. Secret: Paste the token
5. Click "Add secret"

### Step 3: Update Workflow to Use PAT

Modify `.github/workflows/waka-readme.yml`:

**Checkout step** (line ~27):

```yaml
- name: Checkout main
  uses: actions/checkout@8e8c483db84b4bee98b60c0593521ed34d9990e8 # v6.0.1
  with:
    ref: main
    token: ${{ secrets.WAKA_PAT || github.token }}  # Use PAT with fallback
```

**PR creation step** (line ~218):

```yaml
- name: Create or update PR and enable auto-merge
  env:
    GH_TOKEN: ${{ secrets.WAKA_PAT || github.token }}  # Use PAT with fallback
  run: |
    # ... rest of the script
```

**Key Points**:
- `secrets.WAKA_PAT || github.token`: Uses PAT if available, falls back to bot token
- Backward compatible: Works without PAT (but won't auto-merge)
- Two locations: checkout (for git operations) and gh CLI (for PR operations)

### Step 4: Test the Fix

#### Manual Test (Immediate)

```bash
# Trigger workflow manually
gh workflow run waka-readme.yml

# Wait ~1 minute, then check for PR
gh pr list

# If PR created, verify checks are running
gh pr checks <PR_NUMBER>

# Monitor auto-merge
watch -n 5 'gh pr view <PR_NUMBER> --json state,statusCheckRollup,autoMergeRequest'
```

#### Expected Behavior
1. **Workflow runs** (1-2 minutes)
2. **PR created** with proper title/body
3. **Workflows trigger automatically** (`lint.yml`, `docs-quality.yml`)
4. **Checks report status** (visible in PR, not "Expected — Waiting")
5. **Auto-merge executes** when all checks pass (30-60 seconds)
6. **PR merges automatically** without manual intervention

#### Success Indicators
- ✅ PR shows "Merging..." status
- ✅ Checks display green checkmarks (not yellow pending)
- ✅ PR closes and merges to main
- ✅ Commit appears in main branch history
- ✅ No "Expected — Waiting" messages

### Step 5: Verify Daily Automation

The workflow runs automatically via cron:
```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
```

**Check next automated run**:

```bash
# View recent workflow runs
gh run list --workflow=waka-readme.yml --limit 5

# View specific run logs
gh run view <RUN_NUMBER> --log

# Check for auto-merged PRs
gh pr list --state merged --limit 5 | grep "waka"
```

## Troubleshooting Guide

### Issue: "Expected — Waiting for status to be reported"

**Symptoms**:
- PR created successfully
- Checks show pending status forever
- No workflows triggered

**Diagnosis**:

```bash
# Check which token was used
gh run view <RUN_NUMBER> --log | grep "Auto-merge"

# Check PR commit status (replace OWNER/REPO with your repository)
OWNER=reesey275
REPO=reesey275
gh api repos/${OWNER}/${REPO}/pulls/<PR_NUMBER>/commits -q '.[].sha' | head -1 | \
  xargs -I {} gh api repos/${OWNER}/${REPO}/commits/{}/status --jq '.statuses'
```

**Solutions**:
1. Verify `WAKA_PAT` secret exists: `gh secret list | grep WAKA_PAT`
2. Verify PAT has correct permissions (see Step 1)
3. Check PAT hasn't expired: Regenerate if needed
4. Confirm workflow file uses `secrets.WAKA_PAT` in both locations

### Issue: PAT Works But Checks Still Don't Run

**Symptoms**:
- PR created with PAT
- Checks still don't trigger
- PR event should fire but doesn't

**Diagnosis**:

```bash
# Check workflow triggers
grep -A 5 "^on:" .github/workflows/lint.yml
grep -A 5 "^on:" .github/workflows/docs-quality.yml

# Verify pull_request event is listed
```

**Solutions**:
1. Ensure workflows have `pull_request:` in `on:` trigger
2. Check workflow files aren't disabled
3. Verify branch protection requires these checks
4. Test workflow manually: `gh workflow run lint.yml --ref <BRANCH>`

### Issue: Checks Run But Auto-Merge Doesn't Trigger

**Symptoms**:
- Workflows execute successfully
- Checks show green
- PR remains open

**Diagnosis**:

```bash
# Check auto-merge request status
gh pr view <PR_NUMBER> --json autoMergeRequest

# Check required checks configuration (replace OWNER/REPO with your repository)
OWNER=reesey275
REPO=reesey275
gh api repos/${OWNER}/${REPO}/branches/main/protection -q '.required_status_checks'
```

**Solutions**:
1. Verify auto-merge is enabled in PR: `gh pr view <PR_NUMBER> --json autoMergeRequest`
2. Check branch protection requires correct checks
3. Ensure all required checks passed (not just some)
4. Verify no review requirements blocking merge

### Issue: Token Permission Errors

**Symptoms**:
- Workflow fails with "403 Forbidden" or "Resource not accessible"
- Error: "refusing to allow a Personal Access Token to create or update workflow"

**Diagnosis**:

```bash
# Check workflow run errors
gh run view <RUN_NUMBER> --log | grep -i "error\|forbidden\|403"
```

**Solutions**:
1. Verify PAT has all required permissions:
   - Contents: Read and write ✅
   - Pull requests: Read and write ✅
   - Actions: Read and write ✅
2. Regenerate PAT with correct permissions
3. Update secret: `gh secret set WAKA_PAT` (paste new token)
4. Check PAT repository access includes your repo

### Issue: PAT Expired

**Symptoms**:
- Worked previously, now fails
- Error: "Bad credentials" or "token is invalid"

**Solutions**:

```bash
# Regenerate PAT at GitHub
# https://github.com/settings/personal-access-tokens

# Update secret
gh secret set WAKA_PAT
# Paste new token

# Test immediately
gh workflow run waka-readme.yml
```

**Best Practice**: Set calendar reminder before PAT expiration to regenerate proactively.

## Architecture Decisions

### Why Not GitHub App?
**Considered but rejected**:
- ✅ Would solve bot token limitation
- ❌ Complex setup (app creation, installation, key management)
- ❌ Overkill for single-repo, single-workflow use case
- ❌ Requires webhook endpoint or installation flow

**Verdict**: Fine-Grained PAT is simpler and sufficient for this use case.

### Why Fallback to github.token?
```yaml
token: ${{ secrets.WAKA_PAT || github.token }}
```

**Rationale**:
- ✅ Backward compatibility if PAT not configured
- ✅ Workflow doesn't fail completely
- ✅ Still updates README (just won't auto-merge)
- ✅ Easier debugging (partial functionality vs total failure)

**Trade-off**: PR will be stuck without PAT, but at least README updates.

### Why Not Manually Merge Stuck PRs?
**Considered**: Use `gh pr merge --admin` to bypass checks.

**Rejected**:
- ❌ Defeats purpose of required checks
- ❌ Manual intervention ruins "zero-touch" goal
- ❌ Doesn't solve root cause
- ❌ Would need to do this daily forever

**Verdict**: Fix the root cause (use PAT) instead of working around symptoms.

## WakaTime Free Tier Limitations

### Stats Staleness Issue

**Symptom**: README stats show data from 2-4 hours ago

**Root Cause**: WakaTime's free tier caches API responses. The API returns:
- `is_up_to_date: true` (misleading - doesn't mean data is fresh)
- `percent_calculated: 100%` (doesn't guarantee current data)
- Actual data: 2-4 hours behind real-time activity

**Why It Happens**: Free tier API uses cached responses for performance. Only paid tiers get real-time updates.

### Why Longer Retries Don't Help

The workflow includes retry logic (3 attempts with 5-second delays), but this doesn't solve the core issue:
- If WakaTime's cache is stale, we're hitting their cached data
- Retrying immediately just gets the same cached response
- Longer delays between retries might help slightly, but won't solve the fundamental caching

### Acceptable Solution: Daily Runs

With one run per day at midnight UTC:
- ✅ Data refreshes once daily
- ✅ By next midnight, WakaTime cache has had 24 hours to update
- ✅ You get reasonably current stats every morning
- ✅ No need for paid tier if daily updates are acceptable

### If You Need Real-Time Stats

WakaTime paid tier ($9-19/month) provides:
- Real-time API responses (immediate data)
- No caching delays
- Better rate limits
- Advanced analytics
- But: **Not necessary** if daily midnight runs are acceptable

### Current Implementation (Free Tier Friendly)

The workflow is configured to work well with free tier limitations:
```yaml
on:
  schedule:
    # Runs at 12am UTC every day
    - cron: '0 0 * * *'
```

**By design**: One daily run allows the free tier's cache to naturally refresh while providing fresh-enough stats for a README.

## Success Metrics

### PR #96 (First Success)
- **Created**: 2025-12-21 08:58:11 UTC
- **Merged**: 2025-12-21 08:58:52 UTC
- **Duration**: 41 seconds
- **Checks**: All passed automatically
- **Intervention**: None required

### Expected Ongoing Behavior
- ✅ Daily execution at 00:00 UTC
- ✅ PR creation with fresh stats
- ✅ Automatic workflow triggering
- ✅ Status reporting to PR
- ✅ Auto-merge within 1-2 minutes
- ✅ Zero manual intervention

## Maintenance

### PAT Renewal (Every 90 Days)
1. **Regenerate token** at GitHub (same settings)
2. **Update secret**: `gh secret set WAKA_PAT`
3. **Test**: `gh workflow run waka-readme.yml`
4. **Verify**: Next PR auto-merges successfully

### Monitoring
```bash
# Check recent workflow runs
gh run list --workflow=waka-readme.yml --limit 10

# Check for failed runs
gh run list --workflow=waka-readme.yml --status failure

# Check for stuck PRs (open for >1 hour)
gh pr list --search "is:pr is:open label:waka created:>1hour"
```

### Alerting (Optional)
Consider setting up notifications for:
- Workflow failures (GitHub Actions notifications)
- Stuck PRs (GitHub saved searches)
- PAT expiration reminders (calendar event)

## References

### GitHub Documentation
- [GitHub Bot Token Limitations](https://docs.github.com/actions/security-guides/automatic-token-authentication#using-the-github_token-in-a-workflow)
- [Fine-Grained PAT Permissions](https://docs.github.com/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens)
- [Triggering Workflows](https://docs.github.com/actions/using-workflows/triggering-a-workflow#triggering-a-workflow-from-a-workflow)

### Related PRs
- **PR #89**: Fixed heredoc YAML parsing in waka-readme.yml
- **PR #90**: Fixed emoji UTF-8 encoding in waka-readme.yml
- **PR #91**: Fixed JQ syntax errors in debug commands
- **PR #93**: Added workflow_dispatch to lint.yml (partial solution)
- **PR #95**: Implemented PAT solution (complete fix)
- **PR #96**: First successful auto-merge with PAT

### Key Insights
1. Bot tokens don't trigger pull_request workflows (by design)
2. workflow_dispatch runs don't report commit status
3. PATs bypass bot token restrictions
4. Fine-Grained PATs > Classic PATs for security
5. Auto-merge requires commit status from pull_request events

## FAQ

**Q: Will this work for other workflows?**  
A: Yes! Any workflow that creates PRs with auto-merge can use this pattern.

**Q: What if I don't want auto-merge?**  
A: Still use PAT to trigger checks properly. Just don't enable auto-merge on PRs.

**Q: Can I use Classic PAT instead?**  
A: Yes, but Fine-Grained is more secure (scoped access, expiration, audit trail).

**Q: What happens if PAT expires?**  
A: Workflow falls back to github.token, PRs get stuck (like before). Regenerate PAT.

**Q: Does this expose security risks?**  
A: No. Fine-Grained PAT is scoped to one repo with minimal permissions. More secure than Classic PAT.

**Q: Why 90 day expiration?**  
A: GitHub security best practice. Forces regular rotation. Use custom if needed.

**Q: Can I share PAT across repos?**  
A: Yes, but not recommended. Create separate PATs per repo for better security/audit.

---

**Last Updated**: 2025-12-21  
**Maintained By**: reesey275  
**Status**: Production, working as designed
