# Three-Phase Program Management

DevOnboarder structures onboarding into three repeatable phases that balance
speed with guardrails:

1. **Orientation (Phase 0):** Discord bot prompts new contributors to self-
   identify their service focus and validates required access across GitHub,
   observability dashboards, and the knowledge base. The bot records completion
   in the Task API so we can measure readiness before deep work begins.
2. **Immersion (Phase 1):** Service-specific playbooks move contributors through
   environment bootstrap, golden-path walkthroughs, and pairing sessions. AARs
   captured during immersion train the automation rules that surface common
   blockers and codify fixes into guardrails.
3. **Autonomy (Phase 2):** Contributors graduate to scoped production work.
   Guardrails enforce the 95% quality threshold across checklists, integration
   tests, and documentation updates. Any miss automatically generates a QC task
   that loops back into the planner.

Each phase is tracked inside the program planner and emits metrics consumed by
our quality dashboards. The hybrid shell/Python automation framework keeps the
phases reproducible while we migrate legacy scripts into the shared runner.
