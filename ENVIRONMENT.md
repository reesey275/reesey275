## \U0001f9e9 Repository Scaffolding: `reesey275`

This is a full setup plan for your **Codex-powered GitHub Profile Repository**, structured for long-term automation, visibility, and credibility. It also serves as a living technical resume and professional signal of Chad Reesey’s identity as an automation-first engineer, DevOps leader, and architect.

---

### \U0001f464 Chad Reesey – Technical Profile Overview

**Location:** Cocoa Beach, Florida 32931  
**Email:** creesey@wgu.edu / chad.reesey@outlook.com  
**LinkedIn:** [linkedin.com/in/chad-reesey](https://www.linkedin.com/in/chad-reesey)  
**Status:** U.S. Air Force Veteran | Pursuing B.S. in Computer Science, WGU (2024–2027)

#### \u2705 Core Strengths
- **Infrastructure & Automation:** 25+ years across civilian/government environments
- **DevOps Tooling:** Docker, Ansible, Kubernetes, Terraform, GitHub Actions, CI/CD design
- **Security & Admin:** Active Directory, Role-based Access, server hardening, secret management
- **Leadership:** Veteran leader, project manager, founder of multiple organizations including TAGS
- **Cloud & Virtualization:** Azure, Hyper-V, Citrix XenServer, Cloudflare Tunnels, TrueNAS SCALE
- **AI-Driven Automation:** Building Codex agents for self-documenting, self-healing infrastructure

---

### \U0001f4c1 Folder Structure

```text
reesey275/
├── .codex/
│   ├── agent_profile_writer.md
│   ├── agent_readme_composer.md
│   ├── agent_certs_sync.md
│   └── agent_pages_deployer.md
│
├── projects/
│   ├── devonboarder.md
│   ├── tags_auth_server.md
│   ├── ghostscript_ui.md
│   └── education_tools.md
│
├── resume/
│   ├── resume.pdf
│   └── certs.md
│
├── .github/
│   └── workflows/
│       └── codex-profile-update.yml
│
├── README.md
└── index.md
```

---

### \U0001f522 Environment Configuration Guidelines

You are currently working in a private GitHub profile repo connected to Codex, which will be made public once it’s production ready. Use the following guidance to bootstrap and secure the Codex environment effectively:

#### Environment Variables (non-sensitive)
Recommended for stable Codex execution and reproducible profile behavior:

```env
CODEX_ENV=profile
PROFILE_OWNER=reesey275
GITHUB_ORG=reesey275
PROJECT_LOG_LEVEL=info
ENABLE_MARKDOWN_LINT=true
```

> \u26a0\ufe0f Avoid using `GITHUB_TOKEN` directly in secrets—use dedicated CI tokens with minimal scopes when automation requires it.

#### Secrets (Optional, Scoped)
Only add if future agent pushes or GitHub API actions are needed:
- `CI_PROFILE_PUSH_TOKEN` – Scoped for `contents:write` to allow Codex commits
- `CODEX_AGENT_AUTH` – Only if running a self-hosted Codex runner

> Avoid using general-purpose tokens—explicitly scope all GitHub credentials used for automation.

#### Setup Script Enhancements
Consider updating auto setup to ensure Codex automation success:
- Install `markdownlint-cli2`, `vale`, `jq`, `yq`, `gh`
- Bootstrap `/logs/`, `/scripts/`, and `.codex/.state` folders

#### GitHub Pages
Enable once the profile is made public. Codex Agent `pages_deployer` can deploy `index.md` or a generated `docs/` site.

---

Let me know when you're ready to:
- Push this repo live
- Generate starter content for your key projects
- Set up automation for README and Pages deployment
