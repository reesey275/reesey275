# Discord Bot Capabilities

The DevOnboarder Discord bot is the first-touch interface for new
contributors:

- **Role-aware intake:** The bot walks users through profile collection,
  access verification, and runbook selection for each service they join.
- **Hybrid automation bridge:** Commands hand off to the Python task runner that
  is replacing our legacy shell scripts. This keeps chat-first flows aligned
  with the broader automation migration.
- **Quality signal capture:** Conversations produce structured events that feed
  the AAR collector, allowing the platform to correlate chat-based questions
  with onboarding gaps and raise QC actions before launch readiness drops below
  95%.

See the [Three-Phase Program Management](./program-management.md) overview for
how the bot feeds orientation metrics into the planner.
