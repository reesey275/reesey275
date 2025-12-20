# Codex Agent Index

This document lists the Codex agents used in this repository and outlines their roles.

| Agent File | Role | Scope | Description |
| --- | --- | --- | --- |
| [agent_certs_sync][certs] | maintainer | credentials | Syncs certs and creds with external services. |
| [agent_pages_deployer][pages] | maintainer | website | Builds static site and deploys to GitHub Pages. |
| [agent_readme_composer][readme] | writer | docs | Composes project README files. |
| [agent_profile_writer][profile] | writer | portfolio | Writes project summaries for `/projects/*/README.md`. |

[certs]: ../.codex/agent_certs_sync.md
[pages]: ../.codex/agent_pages_deployer.md
[readme]: ../.codex/agent_readme_composer.md
[profile]: ../.codex/agent_profile_writer.md
