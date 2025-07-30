# profile

## Automation

The `codex-profile-update` workflow automates updates using the OpenAI Codex
action. It requires two secrets to be configured in the repository settings:

* `CI_PROFILE_PUSH_TOKEN` – used to push commits created by the workflow.
* `CODEX_AGENT_AUTH` – authenticates the Codex agent to run profile tasks.

Without these secrets the workflow will skip pushing or fail to run the agent.
