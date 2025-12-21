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
   - Day-of-week breakdown (WakaTime free tier doesn't provide `.data.days`)
   - Language repos (GitHub API returns incomplete repo list)

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

### Script Usage (Reference Only)

```bash
# Check for blocking threads (agents use this)
scripts/pr_threads_guard.sh <PR_NUMBER>

# This command shows which threads are blocking the PR
# Exit 0 = no blocking threads
# Exit 1 = active threads exist (PR cannot merge)
```

**Note**: The `--resolve-bot-threads` mode is human-only and will fail if agent context is detected.
