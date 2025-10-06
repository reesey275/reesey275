# DevOnboarder

DevOnboarder is the onboarding control plane for our multi-service platform. It
centralizes runbooks, Discord-first intake, and after action report (AAR)
automation so new contributors can ramp across public APIs, agent workflows, and
the knowledge base without context gaps. The program is migrating from a
collection of ad-hoc Bash scripts to a hybrid shell/Python framework, allowing
automation guardrails to enforce the platform's 95% quality threshold while we
keep legacy entry points online.

## Platform Snapshot

- Multi-service onboarding flows sync requirements across production services,
  documentation, and knowledge tooling.
- Hybrid automation migration keeps the existing shell harness functional while
  introducing the Python task runner that powers the Discord bot and program
  planner.
- Guardrails block promotion when checklists, tests, or docs dip below 95%
  completion, and they automatically raise QC tasks from recurring AAR signals.

## Key Program Elements

### Three-Phase Program Management

Onboarding is staged through orientation, immersion, and autonomy phases that
balance speed with guardrails. Each phase emits metrics to the planner and ties
back to the automation migration roadmap. See the
[Three-Phase Program Management](docs/program-management.md) briefing for
details.

### Discord Bot Capabilities

The Discord bot runs the first-touch intake experience, routes contributors to
the correct service playbooks, and bridges chat workflows into the automation
framework. Review the [Discord Bot Capabilities](docs/discord-bot.md)
documentation for supported commands and integration notes.

### AAR & QC Automation

AARs feed the QC guardrails that hold the 95% quality bar. When coverage dips,
the planner opens remediation tasks and keeps contributors in phase until the
gap is closed. The [AAR and Quality Automation](docs/automation.md) overview
captures the feedback loops.

## Automation Entry Points

- [`scripts/setup.sh`](scripts/setup.sh) – compatibility shim that keeps the
  legacy Bash harness available while delegating to the hybrid automation
  framework as services migrate.
- Shared program automation lives in the control plane task runner referenced
  throughout the docs above; use the Discord bot to trigger the latest flows.

## Additional Resources

- [Architecture](docs/architecture.md) – system-level view of the control plane
  and guardrails.
