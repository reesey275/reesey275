# 👨‍💻 Chad Reesey | Mr. Potato 🥔

**Veteran. Architect. Automator.** Founder of The Angry Gamer Show Productions.

Welcome to my Codex-driven portfolio. Everything here is real and modular,
but most projects are still prototypes rather than fully battle-tested.

Read the [integration philosophy](PHILOSOPHY.md) for the guiding principles.

## Table of Contents
- [Featured Projects](#-featured-projects)
- [Engineering Impact & Project Outcomes](#-engineering-impact--project-outcomes)
- [Credentials & Resume](#-credentials--resume)
- [Learning Journal](#-learning-journal)
- [After Action Reviews](#-after-action-reviews)
- [Codex-Powered](#-codex-powered)
- [Summary & Testing Notes](#-summary--testing-notes)
- [Operational Philosophy: Codex as Second Brain](#-operational-philosophy-codex-as-second-brain)
- [What Needs to Happen Now](#what-needs-to-happen-now)
- [Knowledge Transfer & Onboarding](#knowledge-transfer--onboarding)
- [Contact](#-contact)

## 🚀 Featured Projects
- **[DevonBoarder](docs/PROJECTS/DevonBoarder.md)** – Devon coastline mapping experiments
  [project folder](projects/devonboarder/)
- **[core-instructions](docs/PROJECTS/core-instructions.md)** – Governance OS for Codex Agents
  [project folder](projects/core-instructions/)
- **[SquirrelFocus](docs/PROJECTS/SquirrelFocus.md)** – Task planning and focus tracker
  [project folder](projects/squirrel_focus/)

## 📊 Engineering Impact & Project Outcomes

For aspirational metrics and planned targets, see the
[Engineering Metrics Summary](codex_metrics_summary.md). Actual CI reports and
project statistics will replace these numbers once they're available.

### 🚀 DevonBoarder (in progress)
- Exploring web mapping tools for the Devon coastline.
- Aggregates walking routes, local attractions, and surf spots using OpenStreetMap data.
- Currently prototyping a front-end with **Leaflet** while sketching the architecture.
- **Outcome:** Early-stage experiment focused on planning and data integration.

### 📘 Core Instructions (Governance OS for Codex Agents)
- Authored **structured, CI-enforced documentation** for all C-Suite roles across two orgs (TAGS & CRFV), including:
  - `charter.md`, `checklist.md`, and `agent.md` per role.
- Created a **7-workflow GitHub Actions CI system** enforcing:
  - 95%+ coverage, metadata validation, PR-only changes, and full markdownlint/Vale compliance.
- Designed for agent lifecycle management, permission mapping, and secure
  governance across Codex-controlled infrastructure.
- **Outcome:** Built a CI-secured, fully auditable governance framework deployable across any automation-driven org.

### 🧠 Codex Agent Ecosystem & Philosophy
- Deployed 12+ Codex agents as modular infrastructure across systems,
  each bound to specific roles (e.g. CTO, CI Guard, Doc Validator).
- Built a **routing and metadata enforcement model** enabling Codex agents to
  self-audit, escalate, and follow runtime observability rules.
- Designed a philosophy of **"Ethical Automation"** and **"Codex-as-OS"**,
  replacing fragile human-in-loop processes with agent-first design.
- **Outcome:** Delivered the velocity of an 8-person team with ~5 weeks of solo execution and full reproducibility.

### 🗂️ ReC275 Profile (Codex-Powered Portfolio)
- Created a **self-maintaining GitHub portfolio** with integrated Codex agents for:
  - Automatic resume updates
  - Project summaries
  - Deployment sync via GitHub Actions
- Live `README.md` content is managed by AI and updates with project metadata automatically.
- **Outcome:** Developer branding and project tracking system that requires zero manual maintenance post-deploy.

## 🎓 Credentials & Resume

Seasoned veteran and software architect focused on automation and governance.
View the full [resume (PDF)](resume/resume.pdf) for detailed experience.

- Founder of The Angry Gamer Show Productions
- Architected a CI-secured governance framework for Codex agents
- Deployed 12+ Codex agents across infrastructure environments


## 📚 Learning Journal

Progress notes and lessons are captured in [journal_logs/](journal_logs/).

- [Journal Index](docs/Journal_Index.md) – complete list of journal entries
- [AAR Index](docs/AAR_Index.md) – After Action Reviews
- [2025-07-30 Portfolio Integrated Methodology](journal_logs/2025-07-30-portfolio-integrated-methodology.md)

## 📝 After Action Reviews

Post-project retrospectives will be tracked as AAR logs.
Browse the [AAR Index](docs/AAR_Index.md) for available entries.

## 🤖 Codex-Powered
This profile updates itself. Codex Agents handle:
- Project summaries
- Resume sync
- Pages deployment
- Manual notes via [`record_knowledge_dump.sh`](record_knowledge_dump.sh) \
  (use [`codex/tasks/knowledge_dump_TEMPLATE.md`](codex/tasks/knowledge_dump_TEMPLATE.md) as a starting point)

---
“Call it a Potato Stack if you want. It’s smarter every day.”

## ✅ Summary & Testing Notes

This repository currently reflects the initial Codex-driven portfolio template.
Automation scripts manage content updates, but no automated test suite exists yet.
Manual checks are performed before committing changes to ensure files render
correctly. The portfolio integration plan is documented in
[2025-07-30 Portfolio Integrated Methodology](journal_logs/2025-07-30-portfolio-integrated-methodology.md).

### 🧠 Operational Philosophy: Codex as Second Brain

Codex acts as a persistent automation layer for this repository. Treat it as your
second brain: capture decisions in Markdown, commit small updates frequently and
let the agents keep documentation and workflow files in sync. The goal is to
spend less time on rote maintenance and more on building.

### What Needs to Happen Now

- Review the current scaffold for accuracy and update any placeholder info.
- Populate each project page in `projects/*/README.md` with real descriptions and links.
- Configure required secrets (`CI_PROFILE_PUSH_TOKEN`, `CODEX_AGENT_AUTH`).
  `scripts/run_codex_agent.sh` now sources `scripts/gh-preflight.sh` to map
  `CI_PROFILE_PUSH_TOKEN` to `GH_TOKEN` (falling back to `CODEX_AGENT_AUTH`)
  and automatically log into `gh` when it isn't already authenticated. For
  interactive shells, run the helper to install the preflight automatically:

  ```bash
  scripts/install-gh-preflight.sh
  ```

  or source the script manually:

  ```bash
  echo 'source "$HOME/profile/scripts/gh-preflight.sh"' >> ~/.bashrc
  echo 'source "$HOME/profile/scripts/gh-preflight.sh"' >> ~/.zshrc
  ```

- Enable GitHub Pages once the repo is public and confirm the workflow deploys.
- Keep all Codex-related instructions under `.codex/` versioned with the repo.

### Knowledge Transfer & Onboarding

For collaborators:
- Review `.github/workflows` to see how Codex agents run.
- Ensure Node.js is installed so `npx` can invoke the Codex CLI (required for `scripts/run_codex_agent.sh`).
- Check [docs/AGENT_INDEX.md](docs/AGENT_INDEX.md) for each agent's role and configuration.
- Document any manual setup steps or secrets required.
- Capture decisions in Markdown so automation has context.

## 📬 Contact

- Email: [chad.reesey@outlook.com](mailto:chad.reesey@outlook.com)
- LinkedIn: [linkedin.com/in/chad-reesey](https://www.linkedin.com/in/chad-reesey)
