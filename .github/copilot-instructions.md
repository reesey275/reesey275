# GitHub Copilot Instructions for reesey275

## Project Overview

reesey275 is a personal knowledge management and productivity system with automated WakaTime stats integration.

## Critical Systems

### WakaTime Auto-Merge Workflow
- **Status**: Production, fully operational
- **Schedule**: Daily at midnight UTC (cron: `0 0 * * *`)
- **Automation**: Zero-touch - creates PRs with auto-merge enabled
- **Documentation**: `.github/WAKA_AUTO_MERGE_GUIDE.md`

**Key Points**:
- Uses Fine-Grained PAT (`WAKA_PAT` secret) for proper workflow triggering
- Free tier stats are 2-4 hours behind (expected behavior, acceptable with daily runs)
- All checks run automatically and merge when passing
- Never disable the PAT - it's critical for functionality

## PR Guidelines

### Title Format

```text
<type>(<area>): <subject>
```

Examples:
- `FEAT(waka): add timezone to stats`
- `FIX(workflow): resolve stale stats issue`
- `DOCS(readme): update installation guide`

### Quality Requirements
- ✅ No broken links (external link checks must pass)
- ✅ README passes markdown lint
- ✅ All tests pass before merge
- ✅ Conventional commit messages

### Before Creating PRs
Always verify:
1. Markdown lint passes: `bash scripts/lint_markdown.sh`
2. External links are valid: `bash scripts/check_links.sh`
3. No broken internal links in documentation

## WakaTime Stats Management

### What Gets Updated
The `waka-readme.yml` workflow automatically updates:
- Languages used (top 5 from WakaTime)
- Editors used (top 3)
- Operating systems
- Active projects
- Activity categories (AI Coding, Coding, Writing Docs)
- Time zone and date range

### What's NOT Included (Free Tier Limitations)
- Day-of-week breakdown (API doesn't provide)
- Language repositories (incomplete GitHub data)

### Data Freshness
- **Updated**: Once daily at midnight UTC
- **Freshness**: 2-4 hours behind real-time (WakaTime free tier caching)
- **Refresh Strategy**: Daily runs allow cache to naturally update between runs

### If You Need To Debug

```bash
# Manual workflow trigger
gh workflow run waka-readme.yml

# Check run status
gh run list --workflow=waka-readme.yml --limit 5

# View detailed logs
gh run view <RUN_NUMBER> --log

# Check for stuck PRs
gh pr list --search "is:pr is:open"
```

## Development Standards

### Commit Message Format
Required format (enforced):

```text
TYPE(scope): description

Types: FEAT, FIX, DOCS, STYLE, REFACTOR, TEST, CHORE, CI
```

### Testing Before Commit

```bash
# Full verification
bash scripts/lint_markdown.sh
bash scripts/check_links.sh

# If changes affect WakaTime workflow
gh workflow run waka-readme.yml --wait  # Test mode
gh pr view <PR_NUMBER>  # Verify auto-merge works
```

## Common Tasks

### Adding/Updating Documentation
1. Write markdown files
2. Run lint: `bash scripts/lint_markdown.sh`
3. Check links: `bash scripts/check_links.sh`
4. Commit with `DOCS(section): description`

### Modifying WakaTime Stats Display
1. Edit `.github/workflows/waka-readme.yml`
2. Test with `gh workflow run waka-readme.yml`
3. Verify PR creation and auto-merge
4. Commit with `FEAT(waka): description of change`

### Troubleshooting Auto-Merge
First check: `.github/WAKA_AUTO_MERGE_GUIDE.md` (complete troubleshooting guide)

Quick diagnostics:

```bash
# Verify PAT secret exists
gh secret list | grep WAKA_PAT

# Check workflow has PAT available
grep "WAKA_PAT" .github/workflows/waka-readme.yml

# Test manual workflow run
gh workflow run waka-readme.yml
```

## Repository Structure

```text
.github/
├── workflows/
│   ├── quality.yml              # Consolidated quality gate (lint + docs + governance)
│   └── waka-readme.yml          # Auto-merge WakaTime stats workflow
├── WAKA_AUTO_MERGE_GUIDE.md    # Complete technical documentation
└── copilot-instructions.md     # This file
scripts/
├── lint_markdown.sh             # Markdown linting
├── check_links.sh               # Link validation
└── pr_threads_guard.sh          # Review thread governance enforcement
```

## CI Workflow Management

### Quality Gate Workflow

The `quality.yml` workflow consolidates all quality checks into a single sequential job:

1. **ShellCheck**: Validates shell script syntax
2. **Codespell**: Checks spelling across all files
3. **Markdownlint CLI2**: Enforces markdown formatting rules
4. **Vale**: Validates prose style and quality
5. **PR Thread Governance**: Ensures review threads are resolved (PR-only)

**Status Check Name**: `Quality Gate / quality`

### Modifying Workflows

When changing workflow job names or consolidating workflows:

1. **Update the workflow file** in `.github/workflows/`
2. **Update branch protection** to use new check name:

```bash
# Get current protection settings
gh api repos/reesey275/reesey275/branches/main/protection

# Update required checks (replace old with new)
echo '{
   "strict": true,
   "checks": [
      {
         "context": "quality",
         "app_id": 15368
      }
   ]
}' | gh api --method PATCH \
   repos/reesey275/reesey275/branches/main/protection/required_status_checks \
   --input -
```

1. **Verify protection update**:

```bash
gh api repos/reesey275/reesey275/branches/main/protection/required_status_checks
```

**Critical Notes**:
- The `context` value must match the job name in the workflow
- Use `app_id: 15368` for GitHub Actions checks
- JSON types matter: `strict` is boolean, `app_id` is integer
- All old checks are replaced when updating

## When Something Breaks

1. **Stats not updating**: Check `gh run list --workflow=waka-readme.yml` for failures
2. **Auto-merge not triggering**: Verify PAT exists: `gh secret list | grep WAKA_PAT`
3. **PR stuck open**: Check GitHub Actions logs for workflow failures
4. **Lint failures**: Run `bash scripts/lint_markdown.sh` locally to see issues
5. **Required checks failing**: Verify branch protection matches current workflow job names

## Security Notes

- PAT is scoped to this repository only
- PAT has minimal required permissions (contents write, pull-requests write)
- PAT has 90-day expiration (GitHub best practice)
- PAT should be regenerated when it expires

## PR Review Thread Governance

### Critical: Agents Cannot Resolve Threads

The repository enforces **mandatory human-in-the-loop review** through `scripts/pr_threads_guard.sh`:

**What Agents CAN Do**:
- ✅ Push fixes to address Copilot's raised issues
- ✅ Reply to threads with explanations or rationale
- ✅ Check thread status with `scripts/pr_threads_guard.sh <PR_NUMBER>`

**What Agents CANNOT Do**:
- ❌ Resolve/close review threads
- ❌ Force-merge PRs with active threads
- ❌ Use `--resolve-bot-threads` flag (human-only)

### When Copilot Leaves Review Comments

**Complete Workflow**:

1. **Check thread status first**:

```bash
scripts/pr_threads_guard.sh <PR_NUMBER>
```

- Exit 0 = no blocking threads (proceed)
- Exit 1 = active threads found (address them first)

1. **Review Copilot comments** in GitHub UI:
   - Navigate to PR → Files changed
   - Read each comment thread carefully
   - Understand the root cause, not just symptoms

1. **Push fixes** to address the issues:

```bash
# Make changes to fix the issues
git add .
git commit -m "FIX(component): address Copilot review feedback"
git push
```

- Fixed threads become "outdated" automatically
- Outdated threads don't block merges

1. **Re-check thread status**:

```bash
scripts/pr_threads_guard.sh <PR_NUMBER>
```

- Verify threads are now outdated or resolved

1. **STOP and wait** - a human must resolve threads in GitHub UI:
   - Only humans can mark threads as "Resolved"
   - Do not attempt workarounds or force options
   - Do not try to use `--resolve-bot-threads` (agent-blocked)

1. **Merge only when clear**:

```bash
# Only after pr_threads_guard.sh exits 0
gh pr merge <PR_NUMBER> --squash
```

**Result**: Outdated threads no longer block merges, but unresolved threads always do.

**Exit Codes Reference**:
- `0` - No active threads (safe to merge)
- `1` - Active threads exist (policy violation)
- `2` - Usage error (check command syntax)
- `3` - API error (check network/authentication)
- `4` - Annotation failed (human-only operation)
- `5` - Force blocked (agent attempted human-only operation)

---

**Last Updated**: 2025-12-21
**Status**: Operational
**Workflows**: quality.yml (consolidated), waka-readme.yml (auto-merge)
**Emergency Contact**: `.github/WAKA_AUTO_MERGE_GUIDE.md` for WakaTime issues
