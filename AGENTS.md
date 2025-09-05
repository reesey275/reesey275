# Contributing Guidelines

## Required Checks
- `./scripts/lint_markdown.sh [files]` – ensures Markdown lines stay within 120 characters
  and do not contain trailing spaces. When no files are provided, all tracked `*.md`
  files are scanned.
- `./scripts/check_links.sh [files]` – validates that every HTTP(S) link returns a
  successful status. When no files are provided, all tracked `*.md` files are scanned.

Run both scripts and confirm they pass before opening a pull request.

## Pull Request Rules
- Commit directly to the main branch; do not create new branches.
- Use descriptive commit messages and keep commits focused.
- Include confirmation of the required checks in the PR body.

## Journal Entries
- Add new entries in `journal_logs/` using the naming convention `YYYY-MM-DD-title.md`.
- Run `./scripts/add_journal_entry.sh <path> "Title" "Summary"` to update both
  `journal_logs/README.md` and `docs/Journal_Index.md`.
