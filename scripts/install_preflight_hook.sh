#!/usr/bin/env bash
set -euo pipefail

mkdir -p "${HOME}/.config/codex"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
install -Dm0755 "${script_dir}/preflight_gh_auth.sh" "${HOME}/.config/codex/preflight_gh_auth.sh"

hook="source \"$HOME/.config/codex/preflight_gh_auth.sh\""
for rc in "${HOME}/.bashrc" "${HOME}/.zshrc"; do
  [ -f "$rc" ] || touch "$rc"
  grep -Fq "$hook" "$rc" || echo "$hook" >>"$rc"
done
