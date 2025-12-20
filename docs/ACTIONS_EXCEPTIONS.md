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

### peter-evans/create-pull-request

| Field       | Value                                                                                 |
| ----------- | ------------------------------------------------------------------------------------- |
| Repository  | [peter-evans/create-pull-request](https://github.com/peter-evans/create-pull-request) |
| Version     | v7                                                                                    |
| SHA         | `22a9089034f40e5a961c8808d113e2c98fb63676`                                            |
| Used in     | `.github/workflows/waka-readme.yml`                                                   |
| Added       | 2025-12-20                                                                            |

#### Why This Action Is Needed

This action is required because:

1. **Signed commits requirement**: Branch protection on `main` requires signed commits (`required_signatures: enabled`)
2. **GITHUB_TOKEN limitations**: Commits made via `git commit` with `GITHUB_TOKEN` are **unsigned** - they only authenticate the push, they don't sign the commit
3. **GitHub API signing**: The `create-pull-request` action uses the GitHub API to create commits, which GitHub automatically signs and verifies as coming from `github-actions[bot]`

Without this action, automated PRs from workflows would be blocked by the signed commit requirement.

#### Alternatives Considered

| Alternative                 | Why Rejected                                                           |
| --------------------------- | ---------------------------------------------------------------------- |
| Disable signed commits      | Weakens security posture; signed commits provide audit trail           |
| GPG key in workflow         | Complex setup; requires secrets management; key rotation burden        |
| Manual git commit + push    | Produces unsigned commits; blocked by branch protection                |
| Squash merge workaround     | GitHub still blocks merge when unsigned commits exist in PR history    |

#### Security Review for create-pull-request

- **Stars**: 2,200+ (as of 2025-12)
- **Open issues**: ~40 (reasonable for a popular action)
- **Maintenance**: Actively maintained by Peter Evans
- **Dependencies**: Minimal; uses `@actions/core`, `@actions/exec`, `@actions/github`
- **Permissions required**: `contents: write`, `pull-requests: write`
- **Code audit**: Action source is readable TypeScript; no obfuscation

#### Risks and Mitigations

| Risk                        | Mitigation                                        |
| --------------------------- | ------------------------------------------------- |
| Supply chain attack via tag | SHA pinning prevents this                         |
| Malicious code injection    | Reviewed action source; limited permissions       |
| Token exposure              | Action only uses standard `GITHUB_TOKEN`          |

---

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

## Audit Log

| Date       | Action                         | Change                        | Reviewer  |
| ---------- | ------------------------------ | ----------------------------- | --------- |
| 2025-12-20 | peter-evans/create-pull-request | Added v7 @ `22a9089...`      | reesey275 |
| 2025-12-20 | actions/checkout               | Documented v4 @ `34e1148...` | reesey275 |

---

## Review Schedule

- **Quarterly**: Review all pinned SHAs against latest releases
- **On CVE**: Immediately review affected actions
- **On major version**: Evaluate upgrade path and re-pin SHA
