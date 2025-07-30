# profile
codex/add-projects-and-resume-directories-with-files
This repository contains my personal profile information, projects, and resume.

## Projects

Project notes live in the [`projects/`](projects/) directory.
Some starter files include:

- [`projects/devonboarder.md`](projects/devonboarder.md)
- [`projects/tags_auth_server.md`](projects/tags_auth_server.md)
- [`projects/example_project.md`](projects/example_project.md)

## Resume

Resume materials are kept in the [`resume/`](resume/) directory.
Files include:

- [`resume/resume.pdf`](resume/resume.pdf)
- [`resume/certs.md`](resume/certs.md)
=======
## Automation

The `codex-profile-update` workflow automates updates using the OpenAI Codex
action. It requires two secrets to be configured in the repository settings:

* `CI_PROFILE_PUSH_TOKEN` – used to push commits created by the workflow.
* `CODEX_AGENT_AUTH` – authenticates the Codex agent to run profile tasks.

Without these secrets the workflow will skip pushing or fail to run the agent.
