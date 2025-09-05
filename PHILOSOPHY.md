# Integration Philosophy

The project is guided by three principles: visible learning, doctrine, and automation.
Each principle keeps work transparent, consistent, and scalable.

## Visible Learning
Make insights observable so others can learn quickly and decisions remain traceable.

- Commit messages and pull requests describe intent, making every change easy to understand.
- Journal logs and design documents record experiments, providing context for future iterations.
- Code comments capture edge cases so lessons from bugs persist in the codebase.

## Doctrine
Shared rules provide structure and reduce ambiguity across contributions.

- `AGENTS.md` files define local conventions so contributors work from the same playbook.
- Naming and file organization follow established patterns, simplifying navigation and reviews.
- Decisions reference documented principles, preventing ad-hoc changes that drift from goals.

## Automation
Automate routine tasks while keeping behavior transparent and controllable.

- Scripts like `lint_markdown.sh` and `check_links.sh` enforce quality checks consistently.
- The journaling script adds entries and updates indexes, saving time without hiding logic.
- Codex agents handle repetitive edits, but configuration lives in the repo for auditability.
