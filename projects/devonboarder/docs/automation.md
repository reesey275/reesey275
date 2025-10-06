# AAR and Quality Automation

DevOnboarder bakes automation into every onboarding loop:

- **AAR capture:** After action reports generated during onboarding phases are
  normalized by the AAR collector service. Structured summaries land in the
  shared knowledge base and automatically raise backlog items when patterns
  repeat.
- **Guardrail enforcement:** The QC guardrail service blocks rollouts unless the
  combined checklist, test, and documentation completion rate stays at or above
  95%. When the threshold is missed, the planner opens targeted remediation
  tasks and prevents promotion to the next phase.
- **Hybrid execution framework:** Automation entry points are migrating from the
  legacy Bash harness into a Python-based task runner. Until the migration
  completes, the [`scripts/setup.sh`](../scripts/setup.sh) shim keeps shell-based
  teams online while delegating to the new runner when available.

These mechanisms ensure automation does more than lint documentation—it keeps
people, bots, and services synchronized while they learn how to build in the
platform.
