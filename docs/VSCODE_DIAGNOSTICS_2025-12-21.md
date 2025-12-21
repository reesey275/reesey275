# VSCode Diagnostics Export - 2025-12-21

## YAML Parsing Errors

### Error 1: waka-readme.yml:263
**Severity:** Error
**Message:** Implicit keys need to be on a single line
**Location:** `.github/workflows/waka-readme.yml`, line 263, column 1

**Code Context:**


```yaml
cat > "$TEMP_BODY" <<'EOF'
Automated WakaTime stats update from GitHub Actions.
^--- Parser error here
```

**Analysis:**
- Heredoc content (`<<'EOF'`) is INSIDE a bash `run:` block
- Content is NOT at column 1 of YAML (it's inside bash script)
- VSCode YAML linter may be incorrectly parsing bash heredoc as YAML
- Actual YAML structure is valid: heredoc is string content within bash script

**Investigation Required:**
- Verify YAML validates with `yamllint`
- Check if VSCode is using incorrect YAML schema
- Test workflow execution in GitHub Actions (should work despite VSCode warning)

### Error 2: waka-readme.yml:263
**Severity:** Error
**Message:** Implicit map keys need to be followed by map values
**Location:** `.github/workflows/waka-readme.yml`, line 263, column 1

**Analysis:** Same root cause as Error 1 (duplicate error from YAML linter)

### Error 3: docs-quality.yml:7
**Severity:** Error
**Message:** Unexpected value 'workflow_dispatch'
**Location:** `.github/workflows/docs-quality.yml`, line 7

**Code Context:**

```yaml
name: docs-quality

on:
  pull_request:
  push:
    branches: [ main ]
    workflow_dispatch:  <--- INCORRECT PLACEMENT
```

**Root Cause:** `workflow_dispatch:` is NESTED under `push:` instead of being sibling to `pull_request:` and `push:`

**Fix Required:**

```yaml
name: docs-quality

on:
  pull_request:
  push:
    branches: [ main ]
  workflow_dispatch:  # Sibling to pull_request and push
```

---

## Action Items

1. **Fix docs-quality.yml** (CONFIRMED ERROR)
   - Move `workflow_dispatch:` to correct indentation level
   - Should be sibling to `pull_request:` and `push:`, not child of `push:`

2. **Investigate waka-readme.yml warnings**
   - VSCode may be incorrectly parsing bash heredoc as YAML
   - Verify with: `yamllint .github/workflows/waka-readme.yml`
   - Test workflow execution (likely working despite VSCode warning)
   - Consider: May be false positive from VSCode YAML extension

---

## Test Commands

```bash
# Validate YAML syntax
yamllint .github/workflows/docs-quality.yml
yamllint .github/workflows/waka-readme.yml

# Test workflow dispatch (requires gh CLI + auth)
gh workflow run docs-quality.yml

# Check recent workflow runs
gh run list --workflow=docs-quality.yml --limit 5
gh run list --workflow=waka-readme.yml --limit 5
```
