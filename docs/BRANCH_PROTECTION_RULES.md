# Branch Protection Rules — reesey275/reesey275

This document defines the required branch protection settings for the profile repository to enforce quality gates and prevent governance breaches.

## Target Branch

- `main`

## Required Status Checks (Strict)

Enable “Require status checks to pass before merging” with strict mode:

- Required checks (contexts):
  - `Lint`
  - `docs-quality`
- Strict mode: `true` (require branch to be up-to-date before merging)

## Additional Protections

- Require pull request reviews before merging: `enabled`
  - Minimum approvals: `1` (adjust as needed)
  - Dismiss stale approvals: `enabled`
- Enforce administrators: `enabled`
- Require signed commits: `enabled` (already active via required signatures)
- Require linear history: `enabled` (optional, recommended)
- Restrict who can push to matching branches: `enabled` (no direct pushes to `main`)
- Require conversation resolution before merging: `enabled` (optional, recommended)

## Notes

- This profile repository is primarily documentation. Even so, quality gates should be enforced to maintain consistency and prevent broken links or lint violations from landing on `main`.
- If additional workflows are added (e.g., link check, spell check), include them in the required checks list once they are stable.
