# PR Thread Resolution Policy

## Purpose

Review-thread state must distinguish technical work from the human governance
checkpoint. A changed diff hunk can make a thread outdated without proving that
the concern was addressed, and GitHub can report a thread as resolved without a
useful audit record.

## Thread states

| GitHub state | Repository meaning | Required action |
| --- | --- | --- |
| `isResolved=false`, `isOutdated=false` | Current actionable feedback | Correct, explain, or defer the concern and add an inline audit reply. |
| `isResolved=false`, `isOutdated=true` | Technical fix may be present; human handoff is pending | The owner inspects the corrective commit and audit reply, then resolves the thread in GitHub UI. |
| `isResolved=true` | Human checkpoint complete | No further thread action is required. |

Outdated is not equivalent to resolved. It only means the original diff anchor
changed.

## Mode semantics

`scripts/pr_threads_guard.sh` has two explicit check modes:

```bash
# Standard operator inspection: only current unresolved threads return 1.
scripts/pr_threads_guard.sh <PR_NUMBER> --check

# Merge governance: every unresolved thread returns 1.
scripts/pr_threads_guard.sh <PR_NUMBER> --check --strict
```

Generic environment variables such as `CI=true` and `AGENT_CONTEXT=true` do not
select strict mode. The caller must pass `--strict` deliberately. The Quality
Gate does so in `.github/workflows/quality.yml` because repository policy
requires human resolution before merge.

This separation makes the result testable and keeps an addressed, outdated
thread from being reported as a code-quality failure. In strict mode it still
blocks, but the output identifies the block as a human handoff.

## Line-drift audit procedure

When a corrective commit changes the reviewed lines and makes a thread
outdated:

1. Reply on the original thread.
2. Identify the corrective commit or commits.
3. Describe the behavioral change.
4. Record the relevant test and validation evidence.
5. Record the current `isOutdated` and `isResolved` values.
6. Stop for owner inspection and manual resolution in GitHub UI.

An audit reply should be specific to one thread. A PR-level summary alone does
not preserve the necessary review context.

## Human and agent boundaries

- Agents may inspect threads, implement fixes, and post explanatory replies.
- Agents must not resolve or reopen review threads.
- The human owner performs the final resolution in GitHub UI.
- Automated or batch resolution is not a substitute for owner inspection.

The legacy resolution helpers remain human-only administrative tools. Their
existence does not authorize an agent or CI job to mutate thread state.

## CI reporting contract

The guard reports three separate outcomes:

- **Actionable review feedback:** current unresolved comments need technical
  disposition.
- **Human handoff pending/required:** addressed or outdated comments still need
  owner inspection and resolution.
- **No unresolved review threads:** the thread gate is complete.

The Quality Gate invokes explicit strict mode, so either unresolved category
fails the `quality` job. The wording identifies whether the failure represents
current technical feedback or the human-resolution checkpoint.

## Regression coverage

`scripts/tests/test_pr_threads_guard.py` exercises:

- current unresolved feedback in standard mode;
- outdated unresolved feedback in standard mode;
- outdated unresolved feedback in explicit strict mode;
- resolved feedback in strict mode;
- the absence of implicit strict selection from `CI=true`; and
- explicit strict selection in the Quality Gate workflow.

## Ownership boundary

This policy covers `.github/workflows/quality.yml` and
`scripts/pr_threads_guard.sh` in this repository. Broader shared-governance or
upstream behavior requires separate evidence, scope, and authorization.

## References

- [GitHub GraphQL `PullRequestReviewThread`](https://docs.github.com/en/graphql/reference/objects#pullrequestreviewthread)
- [GitHub GraphQL `resolveReviewThread`](https://docs.github.com/en/graphql/reference/mutations#resolvereviewthread)

## Changelog

- **2026-08-07:** Defined explicit standard and strict modes, human-handoff
  terminology, the line-drift audit procedure, and behavioral regression tests.
- **2025-12-21:** Established the audit-trail requirement for thread resolution.
