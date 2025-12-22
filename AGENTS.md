Setup commands Codex should run

Markdown checks: bash scripts/lint_markdown.sh

External link checks: bash scripts/check_links.sh

PR rules

Title format: `<type>(<area>): <subject>`

No broken links; README passes lint.

## WakaTime Workflow Integration

The repository includes an automated WakaTime stats workflow for keeping README metrics current.

### Key Points for Agents

1. **Auto-Merge Enabled**: The `waka-readme` workflow creates PRs with auto-merge enabled. No manual intervention required.

2. **Schedule**: Runs daily at midnight UTC via cron trigger (`0 0 * * *`)

3. **Authentication**: Uses a Fine-Grained PAT (`WAKA_PAT` secret) to properly trigger dependent workflows.
   - **Do NOT** use regular `github.token` for this workflow
   - PAT enables automatic workflow execution on PR creation
   - See `.github/WAKA_AUTO_MERGE_GUIDE.md` for complete details

4. **Free Tier Behavior**: WakaTime free tier stats are 2-4 hours behind real-time data.
   - This is expected and acceptable with daily midnight runs
   - By next midnight run, cache will have refreshed
   - If real-time stats needed, only paid tier provides that

5. **Stats Included**:
   - Languages (top 5)
   - Editors (top 3)
   - Operating systems (top 3)
   - Projects (top 5)
   - Categories like "AI Coding", "Coding", "Writing Docs"
   - Overall stats: total hours, daily average, best day

6. **Removed Sections** (API limitations):
   - Day-of-week breakdown (WakaTime free tier API response doesn't include `.data.days` array with daily breakdowns)
   - Language repos (GitHub API returns incomplete repository list for languages)

### When Modifying the Workflow

- Never disable the fine-grained PAT - it's critical for auto-merge functionality
- Keep the midnight UTC schedule unless there's a specific reason to change
- Debug with `gh workflow run waka-readme.yml` for manual testing
- Check recent runs: `gh run list --workflow=waka-readme.yml --limit 10`
- Reference `.github/WAKA_AUTO_MERGE_GUIDE.md` for troubleshooting

### Documentation Location

Full technical details: [.github/WAKA_AUTO_MERGE_GUIDE.md](.github/WAKA_AUTO_MERGE_GUIDE.md)

## PR Review Thread Governance

The repository uses `scripts/pr_threads_guard.sh` to enforce Copilot review thread resolution.

### Critical Policy for Agents

**AGENTS CANNOT RESOLVE REVIEW THREADS** - This is a mandatory human-in-the-loop checkpoint:
- Agents may push fixes to make threads outdated
- Agents may reply with rationale or explanations
- **Agents must NEVER** attempt to resolve threads
- Only humans can mark threads as resolved in GitHub UI

### When Review Threads Block Your Work

If Copilot leaves review comments and your PR shows active threads:

1. **Push fixes**: Address the issues raised and push new commits
2. **Verify threads become outdated**: Threads automatically mark as outdated when fixes are pushed
3. **Wait for human**: A human must manually resolve the threads in GitHub UI
4. **Do NOT**: Try to force-resolve or work around the system

### Complete Review Thread Workflow

**Before attempting to merge any PR**, always check for active review threads:

```bash
# Step 1: Check for blocking threads
scripts/pr_threads_guard.sh <PR_NUMBER>

# Exit codes:
# 0 = No active threads (safe to merge)
# 1 = Active threads exist (PR blocked)
# 3 = API error (check network/auth)
```

**Step-by-step procedure**:

1. **Check thread status**:

   ```bash
   scripts/pr_threads_guard.sh 112
   ```

2. **Interpret results**:
   - Exit 0: ✅ No blocking threads - safe to merge
   - Exit 1: ❌ Active threads found - see output for details
   - Script lists each thread with:
     - Thread ID
     - File path and line number
     - Comment preview
     - Status (active/outdated/resolved)

3. **If threads are blocking**:
   - Review each comment in GitHub UI
   - Push fixes to address the issues
   - Fixed threads become "outdated" automatically
   - Re-run check: `scripts/pr_threads_guard.sh <PR_NUMBER>`
   - Wait for human to resolve any remaining threads

4. **Merge when clear**:

   ```bash
   # Only after pr_threads_guard.sh exits 0
   gh pr merge <PR_NUMBER> --squash
   ```

### Script Modes and Options

**Default mode (--check)**:

```bash
scripts/pr_threads_guard.sh <PR_NUMBER>        # Read-only check
scripts/pr_threads_guard.sh <PR_NUMBER> --check  # Explicit check
```

**Human-only mode (AGENTS BLOCKED)**:

```bash
# AGENTS CANNOT USE THESE - Will fail if AGENT_CONTEXT=true
scripts/pr_threads_guard.sh <PR_NUMBER> --resolve-bot-threads --annotate
scripts/pr_threads_guard.sh <PR_NUMBER> --resolve-bot-threads --force
```

**Strict mode** (auto-enabled in CI and for agents):

```bash
# Treats ALL unresolved threads as blocking (ignores outdated status)
export AGENT_CONTEXT=true  # Auto-enables strict mode
export CI=true             # Also auto-enables strict mode
scripts/pr_threads_guard.sh <PR_NUMBER> --strict
```

**Note**: The `--resolve-bot-threads` mode is human-only and will fail if agent context is detected.

## CI Workflow Management

### Workflow Consolidation Strategy

When multiple workflows perform duplicate checks, consolidate them to reduce CI minutes and maintenance burden.

#### Example: Consolidating Quality Checks

- **Problem**: `lint.yml` and `docs-quality.yml` both run markdown linting
- **Solution**: Merge into single `quality.yml` with sequential steps
- **Benefit**: ~50% reduction in CI minutes, single workflow to maintain

### Updating Branch Protection After Workflow Changes

**Critical**: When workflow job names change, branch protection rules MUST be updated.

#### Step 1: Identify Current Protection Settings

```bash
# Get current required checks
gh api repos/OWNER/REPO/branches/main/protection

# Look for "required_status_checks" section
# Note the "contexts" array and "checks" array with app_id
```

#### Step 2: Determine New Check Name

```yaml

# In new workflow file (e.g., quality.yml)
jobs:
  quality:  # <-- This is the check name
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        # ...
```

The required status check will be: `"Workflow Name / job-name"`
Example: `"Quality Gate / quality"`

#### Step 3: Update Branch Protection

```bash
# Replace old checks with new consolidated check
echo '{
  "strict": true,
  "checks": [
    {
      "context": "quality",
      "app_id": 15368
    }
  ]
}' | gh api --method PATCH \
  repos/OWNER/REPO/branches/main/protection/required_status_checks \
  --input -
```

**Important Notes**:
- Use `app_id: 15368` for GitHub Actions checks
- JSON must use proper types: boolean for `strict`, integer for `app_id`
- The `context` value is the job name from the workflow
- All old check names will be replaced by the new check(s)

#### Step 4: Verify Update

```bash
# Confirm new protection rules
gh api repos/OWNER/REPO/branches/main/protection/required_status_checks

# Should show only new check name(s)
```

### Workflow Best Practices

1. **Sequential Steps in Single Job**: Faster than multiple jobs (single checkout, one runner)
2. **Fail-Fast**: Configure steps to stop on first failure
3. **Conditional Steps**: Use `if` for PR-only checks (e.g., thread governance)
4. **Tool Installation**: Pin versions, install once at beginning
5. **Clear Naming**: Use descriptive job and workflow names for required status checks

### Common Workflow Patterns

**Quality Gate Pattern** (sequential validation):

```yaml
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
      - name: Install tools
      - name: ShellCheck
      - name: Codespell
      - name: Markdownlint
      - name: Vale
      - name: PR Thread Governance
        if: github.event_name == 'pull_request'
```

**Parallel Execution Pattern** (independent checks):
```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps: [linting steps]
  
  test:
    runs-on: ubuntu-latest
    steps: [testing steps]
  
  security:
    runs-on: ubuntu-latest
    steps: [security steps]
```
