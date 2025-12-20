# Governance Breach Report — 2025-12-20

This document records a governance breach on the `reesey275/reesey275` profile repository where commits were pushed directly to `main` while required quality checks were failing.

## Summary

- Date: 2025-12-20 (UTC)
- Branch: `main`
- Event type: direct pushes (no PR gate)
- Observed failures: Lint and Docs Quality workflows
- Branch protection: required status checks contexts were empty, allowing merges/pushes despite failures

## Signals Observed

The following GitHub Actions runs concluded with `failure` on `main`:

- docs-quality — DOCS(profile): add 2025-12 profile lock artifacts
  - Run: https://github.com/reesey275/reesey275/actions/runs/20392262276
  - Head SHA: `eb059b8fb329dfc280ad1817db9b5066b6e31647`
- Lint — DOCS(profile): add 2025-12 profile lock artifacts
  - Run: https://github.com/reesey275/reesey275/actions/runs/20392262269
  - Head SHA: `eb059b8fb329dfc280ad1817db9b5066b6e31647`
- Lint — DOCS(profile): minimalist polish (badges + optional header)
  - Run: https://github.com/reesey275/reesey275/actions/runs/20392225668
  - Head SHA: `f7a9ddc2db8a42c3542dba5a30292a298a84954c`
- docs-quality — DOCS(profile): minimalist polish (badges + optional header)
  - Run: https://github.com/reesey275/reesey275/actions/runs/20392225655
  - Head SHA: `f7a9ddc2db8a42c3542dba5a30292a298a84954c`
- Lint — DOCS(profile): unify voice to first-person and structure project sections
  - Run: https://github.com/reesey275/reesey275/actions/runs/20392190266
  - Head SHA: `903dca9c2d40c25b55390a77b0b2a1c33c9467f8`
- docs-quality — DOCS(profile): unify voice to first-person and structure project sections
  - Run: https://github.com/reesey275/reesey275/actions/runs/20392190262
  - Head SHA: `903dca9c2d40c25b55390a77b0b2a1c33c9467f8`
- docs-quality — DOCS(profile): unify project blurbs to tight one-liners
  - Run: https://github.com/reesey275/reesey275/actions/runs/20392165598
  - Head SHA: `1fb5c65adbd6a21572bf24b123e1be57d57b27a8`
- Lint — DOCS(profile): unify project blurbs to tight one-liners
  - Run: https://github.com/reesey275/reesey275/actions/runs/20392165595
  - Head SHA: `1fb5c65adbd6a21572bf24b123e1be57d57b27a8`
- docs-quality — DOCS(profile): standardize Shell (POSIX/Bash) and add Education & Certifications
  - Run: https://github.com/reesey275/reesey275/actions/runs/20392136162
  - Head SHA: `1025d01a8ae8a753e09fa09fa6c02c4cd80b947e`

## Root Cause

Branch protection for `main` did not enforce required status checks (contexts list was empty). As a result, direct pushes proceeded even when quality gates were failing.

## Impact

- The `main` branch contains documentation commits that failed lint/docs-quality checks.
- Risk of presenting inconsistent or non-conforming documentation on the public profile.

## Remediation Plan

1. Enforce branch protection rules on `main` (see `docs/BRANCH_PROTECTION_RULES.md`):
   - Require status checks: `Lint` and `docs-quality` (strict mode enabled)
   - Require pull request before merging (disable direct pushes to `main`)
   - Enforce admins; retain required signatures
2. Open a governance issue to track enforcement and remediation.
3. Fix failing checks on the listed SHAs or supersede with a PR that passes lint/docs-quality.
4. Verify protection by attempting a failing change in a test PR (should be blocked).

## Timeline (UTC)

- 09:02–09:13 on 2025-12-20: Multiple push-triggered runs failed on `main` (Lint, docs-quality).
- 09:26 on 2025-12-20: Waka Readme workflow completed successfully (non-blocking signal).

## Appendix: Branch Protection Snapshot

- Required status checks: contexts = `[]` (empty), strict = `false`
- Required signatures: `enabled = true`
- Enforce admins: `enabled = true`
