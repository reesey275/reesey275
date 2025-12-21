# Governance Enforcement — 2025‑12

This issue tracks the enforcement of branch protection rules and remediation of the December 2025 governance breach.

## Background

Multiple commits were pushed directly to `main` while required CI checks (`Lint`, `docs-quality`) were failing. Branch protection was misconfigured with empty required status checks, allowing these merges to proceed.

## Documentation Artifacts

- Breach Report: [`docs/GOVERNANCE_BREACH_2025-12.md`](./GOVERNANCE_BREACH_2025-12.md)
  - Failed run details with SHAs and URLs
  - Root cause: empty required status checks contexts
  - Timeline and impact analysis
- Protection Rules: [`docs/BRANCH_PROTECTION_RULES.md`](./BRANCH_PROTECTION_RULES.md)
  - Required checks specification (Lint, docs-quality)
  - Strict mode, PR requirements, push restrictions
- Profile Lock: [`docs/PROFILE_LOCK_ISSUE_2025-12.md`](./PROFILE_LOCK_ISSUE_2025-12.md)
  - Lock artifacts and governance signals

## Actions Taken

- [x] Document governance breach with failed run SHAs (commit a0fc23d)
- [x] Define branch protection rules specification
- [x] Apply hardened protection to `main` branch via GitHub API:
  - Required status checks: `Lint`, `docs-quality` (strict mode enabled)
  - Required pull request reviews: 1 approval, dismiss stale reviews
  - Linear history enforcement
  - Required conversation resolution
  - Restrictions on force pushes and deletions
  - Enforce for administrators

## Verification

Branch protection now enforces:
- ✅ Strict status checks: `Lint` and `docs-quality` must pass
- ✅ Branch must be up-to-date before merging
- ✅ Pull request required (no direct pushes to `main`)
- ✅ 1 approval required, stale reviews dismissed
- ✅ Linear history maintained
- ✅ Conversation resolution required
- ✅ Force pushes and deletions blocked
- ✅ Applies to administrators

## Outstanding Work

- [ ] Fix or supersede the failing commits with a PR that passes both checks
- [ ] Verify protection by testing a failing PR (should be blocked)
- [ ] Consider adding link validation and spell check to required checks once stable

## Audit Trail

- Governance docs committed: a0fc23d (2025-12-20)
- Branch protection applied: 2025-12-20 (via GitHub API)
- Required checks configured: `Lint` (app_id: null), `docs-quality` (app_id: 15368)

---

This issue serves as the audit trail for governance enforcement and can be closed once verification is complete.
