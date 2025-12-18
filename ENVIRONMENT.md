## \U0001f9e9 Repository Scaffolding: `reesey275`

This is a full setup plan for your **Codex-powered GitHub Profile Repository**, structured for long-term automation, visibility, and credibility. It also serves as a living technical resume and professional signal of Chad Reesey’s identity as an automation-first engineer, DevOps leader, and architect.

---

### 👤 Chad Reesey – Technical Profile Overview

**GitHub:** [reesey275](https://github.com/reesey275) | **Member Since:** June 2013  
**Location:** Cocoa Beach, Florida 32931  
**Email:** creesey@wgu.edu / chad.reesey@outlook.com  
**Company:** [The Angry Gamer Show Productions](https://theangrygamershow.com)  
**Status:** U.S. Air Force Veteran | Pursuing B.S. in Computer Science, WGU (2024–2027).

**Social Media:**
- **LinkedIn:** [in/chad-reesey](https://linkedin.com/in/chad-reesey)
- **Twitter/X:** [@reesey275](https://x.com/reesey275)
- **Facebook:** [Reesey275](https://facebook.com/Reesey275)
- **Instagram:** [reesey275](https://instagram.com/reesey275)

**GitHub Profile Stats:**
- **Public Repositories:** 2 active projects
- **Private Repositories:** 3 development repos
- **Primary Languages:** Python, Shell, JavaScript, PowerShell
- **Followers:** 13 | **Following:** 19
- **Bio:** Veteran software engineer and systems architect building secure, self-hosted tools and AI-integrated platforms. NSLS-inducted leader, founder of TAGS

#### ✅ Core Strengths
- **Infrastructure & Automation:** 25+ years across civilian/government environments
- **DevOps Tooling:** Docker, Ansible, Kubernetes, Terraform, GitHub Actions, CI/CD design
- **Security & Admin:** Active Directory, Role-based Access, server hardening, secret management
- **Leadership:** Veteran leader, project manager, founder of multiple organizations including TAGS
- **Cloud & Virtualization:** Azure, Hyper-V, Citrix XenServer, Cloudflare Tunnels, TrueNAS SCALE
- **AI-Driven Automation:** Building Codex agents for self-documenting, self-healing infrastructure

---

### 📁 Folder Structure

```text
reesey275/
├── .codex/
│   ├── agent_profile_writer.md
│   ├── agent_readme_composer.md
│   ├── agent_certs_sync.md
│   └── agent_pages_deployer.md
│
├── codex/
│   └── philosophy/
│       └── manifesto.md
│
├── projects/
│   ├── devonboarder/
│   │   ├── README.md
│   │   ├── docs/
│   │   ├── scripts/
│   │   └── .codex/philosophy/PHILOSOPHY.md
│   ├── tags_auth_server/
│   │   ├── README.md
│   │   ├── docs/
│   │   ├── scripts/
│   │   └── .codex/philosophy/PHILOSOPHY.md
│   ├── ghostscript_ui/
│   │   ├── README.md
│   │   ├── docs/
│   │   ├── scripts/
│   │   └── .codex/philosophy/PHILOSOPHY.md
│   └── education_tools/
│       ├── README.md
│       ├── docs/
│       ├── scripts/
│       └── .codex/philosophy/PHILOSOPHY.md
│
├── scripts/
│   └── run_codex_agent.sh
│
├── resume/
│   └── resume.pdf
│
├── PHILOSOPHY.md
│
├── .github/
│   └── workflows/
│       ├── codex-profile-update.yml
│       └── deploy-pages.yml
│
├── README.md
└── index.md
```

---

### 🔢 Environment Configuration Guidelines

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
- Each project contains a `scripts/` folder with helper setup scripts

#### GitHub Pages
Enable once the profile is public. Workflow `deploy-pages.yml` runs the Codex `pages_deployer` agent to publish `index.md` or a generated `docs/` site.

---

Let me know when you're ready to:
- Push this repo live
- Generate starter content for your key projects
- Set up automation for README and Pages deployment
### \U0001f9e0 Operational Philosophy: Codex as Second Brain

Codex acts as a persistent automation layer for this repository. Treat it as your
second brain: capture decisions in Markdown, commit small updates frequently and
let the agents keep documentation and workflow files in sync. The goal is to
spend less time on rote maintenance and more on building.

### What Needs to Happen Now

- Review the current scaffold for accuracy and update any placeholder info.
- Populate each project page in `projects/*/README.md` with real descriptions and links.
- Configure required secrets (`CI_PROFILE_PUSH_TOKEN`, `CODEX_AGENT_AUTH`) if
  you plan to run agents automatically.
- Enable GitHub Pages once the repo is public and confirm `deploy-pages.yml` publishes the site.
- Keep all Codex-related instructions under `.codex/` versioned with the repo.

### Knowledge Transfer & Onboarding

When sharing this repo with future collaborators:

- Walk through `.github/workflows` and explain how agents are triggered.
- Point to `.codex/` documents for agent roles and configuration.
- Document any manual steps for environment setup or secrets management.
- Encourage contributors to write changes in Markdown so Codex has context.
- Reference `PHILOSOPHY.md` and each project's `.codex/philosophy` folder for guiding principles.

