# GitHub Actions Exceptions Registry

This document records approved third-party GitHub Actions used in this repository, along with the rationale for each exception and security considerations.

## Policy

All GitHub Actions MUST be pinned to full commit SHAs (not tags) to prevent supply chain attacks. Each third-party action must be documented here with:

- **Justification**: Why this action is needed
- **Alternatives considered**: What else was evaluated
- **Security review**: Verification of the action's trustworthiness
- **SHA pinning**: The specific commit SHA in use

---

## Approved Actions

### actions/checkout

| Field       | Value                                                           |
| ----------- | --------------------------------------------------------------- |
| Repository  | [actions/checkout](https://github.com/actions/checkout)         |
| Version     | v4                                                              |
| SHA         | `34e114876b0b11c390a56381ad16ebd13914f8d5`                      |
| Used in     | All workflows                                                   |
| Added       | 2025-12                                                         |

#### Why actions/checkout Is Used

Official GitHub action for repository checkout. Required for any workflow that needs to access repository contents.

#### Security Review for actions/checkout

- **Publisher**: GitHub (official first-party action)
- **Trust level**: Highest - maintained by GitHub
- **No additional review required**: First-party actions are implicitly trusted

---

## Removed Actions

### peter-evans/create-pull-request (REMOVED 2025-12-21)

**Removal Reason**: Branch protection `required_signatures` was disabled, making direct git operations viable. The action was originally added to work around unsigned commit blocking, but this is no longer necessary.

---

## Audit Log

| Date       | Action                          | Change                       | Reviewer  |
| ---------- | ------------------------------- | ---------------------------- | --------- |
| 2025-12-21 | peter-evans/create-pull-request | Removed - no longer needed   | reesey275 |
| 2025-12-20 | peter-evans/create-pull-request | Added v7 @ `22a9089...`      | reesey275 |
| 2025-12-20 | actions/checkout                | Documented v4 @ `34e1148...` | reesey275 |

---

## Review Schedule

- **Quarterly**: Review all pinned SHAs against latest releases
- **On CVE**: Immediately review affected actions
- **On major version**: Evaluate upgrade path and re-pin SHA
