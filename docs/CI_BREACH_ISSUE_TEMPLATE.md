# CI Breach — Unauthorized Merge to `main` with Failing Checks

This issue records a governance breach: a change landed on `main` while CI checks were failing or not enforced.

## Commit SHA(s)
- <!-- Fill with offending SHA(s), e.g., eb059b8, f7a9ddc, 903dca9, 1fb5c65, 1025d01 -->

## CI Checks (failed)
- <!-- List failing workflows: Lint, docs-quality, Waka Readme (if applicable) -->

## Root Cause
- Merge to `main` bypassed PR pipeline and/or required checks did not cover the failing workflows.

## Action Required
- The author must submit a PR that fully remediates the broken state or reverts their own changes.
- No excuses, no deferrals.

## Enforcement
- TAGS governance prohibits bypassing protected CI gates. This is a Class 1 breach.

## Deadline
- <!-- Set firm timestamp, e.g., 24 hours from incident time. -->

## Evidence
- Recent commits (no merges):
  - eb059b8 — DOCS(profile): add 2025-12 profile lock artifacts
  - f7a9ddc — DOCS(profile): minimalist polish (badges + optional header)
  - 903dca9 — DOCS(profile): unify voice to first-person and structure project sections
  - 1fb5c65 — DOCS(profile): unify project blurbs to tight one-liners
  - 1025d01 — DOCS(profile): standardize Shell (POSIX/Bash) and add Education & Certifications section
- Latest runs (sample):
  - Lint — failure (multiple)
  - docs-quality — failure (multiple)
  - Waka Readme — success (latest dispatch)

## Acceptance Criteria
- PR merged that restores green checks (Lint + docs-quality at minimum).
- Branch protection validated with required checks covering critical workflows.
- Incident closed with links to fix PR and postmortem notes.
