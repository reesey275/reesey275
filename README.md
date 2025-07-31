# 👨‍💻 Chad Reesey | Mr. Potato 🥔

**Veteran. Architect. Automator.** Founder of The Angry Gamer Show Productions.

Welcome to my Codex-driven portfolio. Everything here is real, modular, and battle-tested.

Read the [integration philosophy](PHILOSOPHY.md) for the guiding principles.

## 🚀 Featured Projects
- **[DevOnboarder](projects/devonboarder/)** – CI guardrails and automation with Codex
- **[TAGS Auth Server](projects/tags_auth_server/)** – Discord OAuth2 + Role-based Access
- **[Ghostscript UI](projects/ghostscript_ui/)** – PDF/PostScript conversion with Web UI
- **[Education Tools](projects/education_tools/)** – Algebra generators and learning platforms

## 📊 Engineering Impact & Project Outcomes
- **DevOnboarder:** Aggregates OpenStreetMap and local data into a spatial database served to a Leaflet front end. Development favors quick iterations documented in Markdown.
- **TAGS Auth Server:** Issues tag-based tokens via OAuth login backed by a Tag DB. Simplicity and clear documentation are prioritized for containerized deployments.
- **Ghostscript UI:** Provides a thin web interface to a Ghostscript container for straightforward batch conversions. Designed so non-technical users can operate it without complex setup.
- **Education Tools:** Routes requests through a gateway to micro services like AlgebraService and StudyService. Small, modular apps run on modest hardware with open documentation for collaboration.

## 🎓 Credentials & Resume
- **[Resume (PDF)](resume/resume.pdf)**

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
Manual checks are performed before committing changes to ensure files render correctly. The portfolio integration plan is documented in [journal_logs/2025-07-30-portfolio-integrated-methodology.md](journal_logs/2025-07-30-portfolio-integrated-methodology.md).

### 🧠 Operational Philosophy: Codex as Second Brain

Codex acts as a persistent automation layer for this repository. Treat it as your
second brain: capture decisions in Markdown, commit small updates frequently and
let the agents keep documentation and workflow files in sync. The goal is to
spend less time on rote maintenance and more on building.

### What Needs to Happen Now

- Review the current scaffold for accuracy and update any placeholder info.
- Populate each project page in `projects/*/README.md` with real descriptions and links.
- Configure required secrets (`CI_PROFILE_PUSH_TOKEN`, `CODEX_AGENT_AUTH`) if
  you plan to run agents automatically.
- Enable GitHub Pages once the repo is public and confirm the workflow deploys.
- Keep all Codex-related instructions under `.codex/` versioned with the repo.

### Knowledge Transfer & Onboarding

For collaborators:
- Review `.github/workflows` to see how Codex agents run.
- Check [docs/AGENT_INDEX.md](docs/AGENT_INDEX.md) for each agent's role and configuration.
- Document any manual setup steps or secrets required.
- Capture decisions in Markdown so automation has context.
