# POTATODEV Handoff: Governance Tooling Review

**Date:** 2025-12-21 06:45:36 UTC
**Context:** Post-PR #87 merge - governance tooling enhancements for --audit-outdated functionality
**Status:** PR #87 merged to main (commit cab0765) - local edits detected in pr_threads_guard.sh

---

## 🎯 Mission

1. **Review new guardrails** in `scripts/pr_threads_guard.sh`
2. **Triage VSCode diagnostics** (18 Problems + 27 Info warnings reported)
3. **Document current state** with evidence for archaeological record
4. **Verify CI-safe governance constraints** are preserved

---

## 📋 Review Checklist

### Critical Constraints (NEVER VIOLATE)

- [ ] **One lint workflow, multiple jobs** - Not two separate workflows
  - `lint.yml` contains: MarkdownLint, ShellCheck, PR Thread Governance jobs
  - Each job appears as separate check context (e.g., `Lint / PR Thread Governance`)
  - This is **correct design** - parallelized gates with independent reporting

- [ ] **CI must stay read-only** for governance checks
  - `lint.yml` pr-thread-guard job: `permissions: pull-requests: read`
  - NO write operations in CI (no thread resolution, no PR modifications)

- [ ] **--audit-outdated must be non-blocking** (warn-only) in CI
  - Default exit code: 0 (warning only)
  - Optional `--fail-on-outdated` for strict enforcement (exit 2)
  - CI uses: `bash scripts/pr_threads_guard.sh "${{ github.event.pull_request.number }}" --audit-outdated`

- [ ] **Thread resolution requires reply-then-resolve** with audit trail
  - `resolve_bot_threads.sh` posts inline comment BEFORE resolving
  - Comment documents: commit SHA, reason, policy compliance
  - `--force` flag breaks audit trail (should be avoided)

### New Guardrails in pr_threads_guard.sh

**Recent edits detected** - verify these additions:

- [ ] **Agent constraint enforcement**
  - Comment header states: "Agents can NEVER resolve threads"
  - "Only humans can set isResolved=true"
  - "This is the mandatory human-in-the-loop checkpoint when AI makes mistakes"

- [ ] **Mode-based operation**
  - `--check` (default): Read-only, lists blocking threads
  - `--resolve-bot-threads`: Write mode (requires `--annotate`)
  - `--force`: Bypass annotation (requires force registry)
  - `--strict`: Auto-enabled when `AGENT_CONTEXT=true` or `CI=true`

- [ ] **Force registry integration**
  - Sources: `governance/force_registry.sh`
  - Exit code 5: Force blocked (agent context without override)
  - Logged operations for audit trail

- [ ] **Temp file cleanup**
  - `cleanup_temp_files()` trap on EXIT
  - Removes `/tmp/pr_title_$$`

---

## 🔍 VSCode Diagnostics Triage

### YAML Parsing Errors (Priority: HIGH)

**Location:** `.github/workflows/waka-readme.yml:263`

**Error 1:** Implicit keys need to be on a single line

```yaml
cat > "$TEMP_BODY" <<'EOF'
Automated WakaTime stats update from GitHub Actions.
^--- Error here
```

**Error 2:** Implicit map keys need to be followed by map values

```yaml
cat > "$TEMP_BODY" <<'EOF'
Automated WakaTime stats update from GitHub Actions.
^--- Error here
```

**Root Cause:** Markdown content in heredoc interpreted as YAML at column 1

**Fix Required:** Indent heredoc content or use `--body-file` with temp file
- Current PR body uses markdown with `**Stats Include:**` heading
- YAML parser sees this as attempted map key at column 1
- Solution: All heredoc content must be properly indented within `run: |` block

**Location:** `.github/workflows/docs-quality.yml:7`

**Error:** Unexpected value 'workflow_dispatch'

```yaml
workflow_dispatch:
^--- Error here
```

**Root Cause:** `workflow_dispatch` trigger missing from `on:` block or malformed

**Investigation Needed:**
- Check if `workflow_dispatch:` is under `on:` key
- Verify indentation is correct (2 spaces)
- Confirm no trailing characters or syntax issues

---

## 🛠️ Action Items for POTATODEV

### Immediate (High Priority)

1. **Fix waka-readme.yml YAML parsing error** (line 263)
   - Move PR body content to proper indentation
   - OR use `--body-file` pattern with temp file
   - Verify YAML validates with: `yamllint .github/workflows/waka-readme.yml`

2. **Fix docs-quality.yml workflow_dispatch error** (line 7)
   - Verify `workflow_dispatch:` is under `on:` block
   - Check indentation and syntax
   - Test with: `yamllint .github/workflows/docs-quality.yml`

3. **Review pr_threads_guard.sh recent edits**
   - Verify agent constraint enforcement is correct
   - Test mode flags: `--check`, `--resolve-bot-threads`, `--force`, `--strict`
   - Confirm force registry integration works
   - Validate temp file cleanup

### Evidence Collection

1. **Export full VSCode diagnostics**
   - Copy all Problems (18)
   - Copy all Info warnings (27)
   - Create: `docs/VSCODE_DIAGNOSTICS_2025-12-21.md`

2. **Test governance tooling**

   ```bash
   # Test pr_threads_guard.sh modes
   bash scripts/pr_threads_guard.sh --help
   bash scripts/pr_threads_guard.sh 87 --audit-outdated

   # Test resolve_bot_threads.sh modes
   bash scripts/resolve_bot_threads.sh --help
   bash scripts/resolve_bot_threads.sh 87 --audit-outdated --dry-run
   ```

3. **Verify CI integration**
   - Check `lint.yml` pr-thread-guard job has `--audit-outdated` flag
   - Confirm permissions are `pull-requests: read`
   - Validate no write operations in CI

### Documentation

1. **Create PR with evidence**
   - Title: `FIX(ci): resolve YAML parsing errors in workflow files`
   - Include: VSCode diagnostics export
   - Include: Test results from governance tooling
   - Include: Verification that CI constraints preserved
   - Cross-reference: PR #85, PR #86, PR #87

---

## 📊 Current State Summary

**Merged Work (PR #87):**
- ✅ `--audit-outdated` flag added to `pr_threads_guard.sh`
- ✅ `--resolve-outdated` flag added to `resolve_bot_threads.sh`
- ✅ CI integration with `--audit-outdated` in `lint.yml`
- ✅ Non-blocking warnings for governance debt
- ✅ Read-only permissions preserved

**Outstanding Issues:**
- ⚠️ YAML parsing errors in `waka-readme.yml` (line 263)
- ⚠️ workflow_dispatch error in `docs-quality.yml` (line 7)
- ⚠️ Recent edits to `pr_threads_guard.sh` need review
- ⚠️ 18 Problems + 27 Info warnings from VSCode need triage

**Workflow Architecture (CONFIRMED):**
- ✅ `lint.yml`: ONE workflow with THREE jobs (not two workflows)
  - Job 1: MarkdownLint
  - Job 2: ShellCheck
  - Job 3: PR Thread Governance
- ✅ `docs-quality.yml`: Separate workflow for documentation quality
- ✅ `waka-readme.yml`: Separate workflow for daily automation

**Governance Policy (CODIFIED):**
- ✅ Merge-blocking: Active threads `(isResolved=false AND isOutdated=false)`
- ✅ Governance debt: Outdated threads `(isResolved=false AND isOutdated=true)` surface as warnings
- ✅ Audit trail: ALL resolutions require inline reply documenting commit SHA and rationale
- ✅ Agent constraint: Agents can push fixes, agents CANNOT resolve threads

---

## 🎬 Next Steps

1. **POTATODEV:** Review this handoff document
2. **POTATODEV:** Triage VSCode diagnostics (export full list)
3. **POTATODEV:** Fix YAML parsing errors
4. **POTATODEV:** Test governance tooling
5. **POTATODEV:** Create PR with evidence and verification

---

## 📚 Cross-References

- **PR #85:** Governance violation (outdated thread without audit trail)
- **PR #86:** Technical fix (added missing permissions)
- **PR #87:** Prevention (--audit-outdated tooling) - **MERGED**
- **Canvas:** User-created handoff document with runbook/checklist/PR template

---

**Handoff Complete:** Ready for POTATODEV review and action.

---

## 📊 VSCode Diagnostics Detail Export

### Confirmed YAML Error (MUST FIX)

**File:** `.github/workflows/docs-quality.yml:7`
**Error:** `workflow_dispatch:` incorrectly nested under `push:`
**Fix:** Move to sibling level (same indentation as `pull_request:` and `push:`)

**Current (BROKEN):**

```yaml
on:
  pull_request:
  push:
    branches: [ main ]
    workflow_dispatch:  # WRONG - nested under push
```

**Fixed:**

```yaml
on:
  pull_request:
  push:
    branches: [ main ]
  workflow_dispatch:  # CORRECT - sibling to push and pull_request
```

### Likely False Positive (Investigate)

**File:** `.github/workflows/waka-readme.yml:263`
**Errors:**
1. "Implicit keys need to be on a single line"
2. "Implicit map keys need to be followed by map values"

**Analysis:**
- Errors triggered by bash heredoc (`cat > "$TEMP_BODY" <<'EOF'`)
- Heredoc content contains markdown with `**Stats Include:**`
- VSCode YAML linter incorrectly parsing bash string as YAML structure
- Actual YAML is valid: heredoc is inside bash `run:` block
- Workflow likely executes correctly despite VSCode warning

**Investigation Steps:**
1. Check recent workflow runs: `gh run list --workflow=waka-readme.yml --limit 5`
2. If runs succeed, this is VSCode false positive
3. If runs fail, heredoc indentation may need adjustment
4. Consider installing yamllint for authoritative validation: `pip install yamllint`

---

## 🔧 Quick Fix for POTATODEV

**Priority 1:** Fix docs-quality.yml (confirmed error)

```bash
# Create branch
git checkout -b fix/workflow-yaml-errors

# Fix docs-quality.yml line 7
# Move workflow_dispatch: to correct indentation
# (POTATODEV: Use VSCode editor or sed/awk if comfortable)

# Test YAML syntax (if yamllint available)
yamllint .github/workflows/docs-quality.yml

# Commit
git add .github/workflows/docs-quality.yml
git commit -m "FIX(ci): correct workflow_dispatch indentation in docs-quality.yml

Moved workflow_dispatch trigger to correct indentation level. Was
incorrectly nested under push: block instead of being sibling.

VSCode diagnostic: 'Unexpected value workflow_dispatch' at line 7

Testing: Workflow dispatch should now be accessible via:
gh workflow run docs-quality.yml"

# Push and create PR
git push origin fix/workflow-yaml-errors
gh pr create --title "FIX(ci): correct workflow_dispatch indentation in docs-quality.yml" \
  --body "Fixes VSCode YAML parsing error. See POTATODEV_HANDOFF.md for details."
```

**Priority 2:** Investigate waka-readme.yml (possible false positive)

Wait for POTATODEV review - may not need action if workflows execute successfully.

