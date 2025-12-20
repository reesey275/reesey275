# Documentation Quality Gate — Implementation Checklist

## Status: CI Gate Deployed ✅

### What's In Place

1. **Automated CI Workflow** ✅
   - File: `.github/workflows/docs-quality.yml`
   - Tools: codespell, markdownlint-cli2, vale
   - Trigger: All PRs and pushes to `main`
   - Status: Active

2. **Tool Configuration** ✅
   - `.codespellrc` — spelling check patterns
   - `.markdownlint-cli2.yaml` — markdown structure rules
   - `.vale.ini` — style and terminology enforcement
   - `styles/vocab/base/accept.txt` — project-specific terminology whitelist (IaaS, DevOnboarder, TAGS, MCP, etc.)

3. **Smoke Test** ✅
   - Branch: `test/docs-quality-smoke-test`
   - Status: Pushed to origin; waiting for PR creation
   - Purpose: Verify workflow catches intentional typos (teh, recieve) <!-- codespell:ignore teh,recieve -->

### Next Steps (Manual, Requires GitHub UI)

#### Step 1: Create a Pull Request
The smoke test branch is already pushed. Create a PR:
- Navigate to: https://github.com/reesey275/reesey275/pulls
- Click "New Pull Request"
- Base: `main` | Compare: `test/docs-quality-smoke-test`
- Confirm the docs-quality workflow fails

**Expected behavior:**
- Codespell should fail on "teh" and "recieve" <!-- codespell:ignore teh,recieve -->
- PR should show red X on the docs-quality check

#### Step 2: Enable Branch Protection for `main`
Once you confirm the workflow runs:

1. Go to: **Settings → Branches**
2. Add rule for `main`:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - **Status checks required:**
     - `docs-quality / docs-quality`
3. Save

**Effect:** No PR can merge to `main` unless the docs-quality gate passes.

#### Step 3: Verify Protection Works
1. Try to merge the smoke test PR without fixing errors → should be blocked
2. Fix `SMOKE_TEST.md` (remove "teh", "recieve", "ISaaS") <!-- codespell:ignore teh,recieve -->
3. Verify workflow re-runs and passes
4. Merge succeeds → gate is working

#### Step 4: Delete Test Branch & File

Once verified:

```bash
git checkout main
git pull origin main
git branch -d test/docs-quality-smoke-test
git push origin --delete test/docs-quality-smoke-test
git rm SMOKE_TEST.md
git commit -m "test(cleanup): remove docs-quality smoke test"
git push origin main
```

### Workflow Execution Details

#### Codespell Check
- Catches: typos, misspellings, category errors like "ISaaS"
- Skip patterns: binaries, lock files, Git metadata
- Config: `.codespellrc`

#### Markdownlint Check
- Catches: malformed headers, inconsistent formatting, trailing whitespace
- Config: `.markdownlint-cli2.yaml`
- Globs: All `**/*.md`, excluding node_modules and .git

#### Vale Check
- Catches: terminology drift, tone inconsistency, style violations
- Config: `.vale.ini` + `styles/vocab/base/accept.txt`
- Vocabulary: Whitelists project acronyms and product names to prevent false positives

### Why This Matters

**Before:** Typos = "oops, my bad" → fixed manually when noticed
**After:** Typos = failed PR → must be fixed before merge → never ships to main

This transforms documentation quality from a *nice-to-have* into a *non-negotiable gate*.

### Troubleshooting

If the workflow fails unexpectedly:

1. **Check workflow logs:**
   - PR page → "Checks" tab → "docs-quality" → "View details"

2. **Test locally (optional):**

   ```bash
   # Codespell
   codespell --config .codespellrc .
   
   # Markdownlint
   markdownlint-cli2 --config .markdownlint-cli2.yaml "**/*.md"
   
   # Vale
   vale --config .vale.ini .
   ```

3. **Add to .codespellrc if false positive:**

   ```ini
   ignore-words-list = example-word
   ```

4. **Update vocabulary:**
   - Add new acceptable terms to `styles/vocab/base/accept.txt`
   - Commit and push
   - Workflow will pick up changes on next PR

---

**Session Status**: Docs-quality gate infrastructure deployed; Vale config established; smoke test pushed; ready for branch protection enforcement.
