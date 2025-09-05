# Chad Reesey | Mr. Potato 🥔

**Automating the boring stuff so teams can ship.**

I'm a veteran turned software architect who builds Codex-driven systems that keep
docs, code, and infrastructure in lockstep.

## Philosophy
Curious how these pieces fit together? Explore the guiding
[integration philosophy](PHILOSOPHY.md).

## Table of Contents
- [Philosophy](#philosophy)
- [Featured Projects](#featured-projects)
- [Engineering Impact & Project Outcomes](#engineering-impact--project-outcomes)
- [Credentials & Resume](#credentials--resume)
- [Learning Journal](#learning-journal)
- [Journal Index](#journal-index)
- [AAR Index](#aar-index)
- [After Action Reviews](#after-action-reviews)
- [Codex-Powered](#codex-powered)
- [Summary & Testing Notes](#summary--testing-notes)
- [Operational Philosophy: Codex as Second Brain](#operational-philosophy-codex-as-second-brain)
- [What Needs to Happen Now](#what-needs-to-happen-now)
- [Knowledge Transfer & Onboarding](#knowledge-transfer--onboarding)
- [Contact](#contact)

## Featured Projects
### [DevonBoarder](docs/PROJECTS/DevonBoarder.md)
Prototype mapping project charting the Devon coastline.
It blends OpenStreetMap data with Leaflet to map walking routes,
surf spots, and local attractions while experimenting with data
integration strategies.

### [core-instructions](docs/PROJECTS/core-instructions.md)
Governance OS that turns role documentation into code.
CI-enforced charters, checklists, and agent specs ensure every
Codex agent runs with auditable permissions and repeatable workflows.

### [SquirrelFocus](docs/PROJECTS/SquirrelFocus.md)
A task planning and focus tracker for scattered developers.
Built with Next.js, Supabase, and OpenAI, it corrals stray to-dos,
provides gentle nudges, and tracks progress so attention stays on
what matters.

## Engineering Impact & Project Outcomes

For aspirational metrics and planned targets, see the
[Engineering Metrics Summary](codex_metrics_summary.md). Actual CI reports and
project statistics will replace these numbers once they're available.

### DevonBoarder (in progress)
- Exploring web mapping tools for the Devon coastline.
- Aggregates walking routes, local attractions, and surf spots using OpenStreetMap data.
- Currently prototyping a front-end with **Leaflet** while sketching the architecture.
- **Outcome:** Early-stage experiment focused on planning and data integration.

### Core Instructions (Governance OS for Codex Agents)
- Authored **structured, CI-enforced documentation** for all C-Suite roles across two orgs (TAGS & CRFV), including:
  - `charter.md`, `checklist.md`, and `agent.md` per role.
- Created a **7-workflow GitHub Actions CI system** enforcing:
  - 95%+ coverage, metadata validation, PR-only changes, and full markdownlint/Vale compliance.
- Designed for agent lifecycle management, permission mapping, and secure
  governance across Codex-controlled infrastructure.
- **Outcome:** Built a CI-secured, fully auditable governance framework deployable across any automation-driven org.

### Codex Agent Ecosystem & Philosophy
- Deployed 12+ Codex agents as modular infrastructure across systems,
  each bound to specific roles (e.g. CTO, CI Guard, Doc Validator).
- Built a **routing and metadata enforcement model** enabling Codex agents to
  self-audit, escalate, and follow runtime observability rules.
- Designed a philosophy of **"Ethical Automation"** and **"Codex-as-OS"**,
  replacing fragile human-in-loop processes with agent-first design.
- **Outcome:** Delivered the velocity of an 8-person team with ~5 weeks of solo execution and full reproducibility.

### ReC275 Profile (Codex-Powered Portfolio)
- Created a **self-maintaining GitHub portfolio** with integrated Codex agents for:
  - Automatic resume updates
  - Project summaries
  - Deployment sync via GitHub Actions
- Live `README.md` content is managed by AI and updates with project metadata automatically.
- **Outcome:** Developer branding and project tracking system that requires zero manual maintenance post-deploy.

## Credentials & Resume

Seasoned veteran and software architect focused on automation and governance.
View the full [resume (PDF)](resume/resume.pdf) for detailed experience.

- Founder of The Angry Gamer Show Productions
- Architected a CI-secured governance framework for Codex agents
- Deployed 12+ Codex agents across infrastructure environments


## Learning Journal

Progress notes and lessons are captured in [journal_logs/](journal_logs/).

- [2025-07-30 Portfolio Integrated Methodology](journal_logs/2025-07-30-portfolio-integrated-methodology.md)

## Journal Index
Browse the full list of journal entries in the
[Journal Index](docs/Journal_Index.md).

## AAR Index
After-action reviews are catalogued in the
[AAR Index](docs/AAR_Index.md).

## After Action Reviews

Post-project retrospectives will be tracked as AAR logs.

## Codex-Powered
This profile updates itself. Codex Agents handle:
- Project summaries
- Resume sync
- Pages deployment
- Manual notes via [`record_knowledge_dump.sh`](record_knowledge_dump.sh) \
  (use [`codex/tasks/knowledge_dump_TEMPLATE.md`](codex/tasks/knowledge_dump_TEMPLATE.md) as a starting point)

---
“Call it a Potato Stack if you want. It’s smarter every day.”

## Summary & Testing Notes

This repository currently reflects the initial Codex-driven portfolio template.
Automation scripts manage content updates, but no automated test suite exists yet.
Manual checks are performed before committing changes to ensure files render
correctly. The portfolio integration plan is documented in
[2025-07-30 Portfolio Integrated Methodology](journal_logs/2025-07-30-portfolio-integrated-methodology.md).

### Operational Philosophy: Codex as Second Brain

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

## Contact

- Email: [your.email@example.com](mailto:your.email@example.com)
- LinkedIn: [linkedin.com/in/your-linkedin-handle](https://www.linkedin.com/in/your-linkedin-handle)
