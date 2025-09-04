#!/usr/bin/env bash
set -euo pipefail

# Map CI_PROFILE_PUSH_TOKEN or CODEX_AGENT_AUTH to GH_TOKEN for gh CLI
TOKEN="${CI_PROFILE_PUSH_TOKEN:-${CODEX_AGENT_AUTH:-}}"
if [[ -n "$TOKEN" ]]; then
  export GH_TOKEN="$TOKEN"
fi

# Create Codex issue to track gh auth preflight if token available
if [[ -n "${GH_TOKEN:-}" ]]; then
  curl -sS \
    -H "Authorization: token $GH_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    -d '{"title":"Embed gh auth preflight","body":"Map CI_PROFILE_PUSH_TOKEN/CODEX_AGENT_AUTH to GH_TOKEN and run gh auth login --with-token on session start."}' \
    https://api.github.com/repos/reesey275/profile/issues >/dev/null || true
else
  echo "GH_TOKEN not set; skipping issue creation." >&2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRE_CMD="source \"$SCRIPT_DIR/gh-preflight.sh\""

for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
  if [[ -f "$rc" ]] && ! grep -Fq "$PRE_CMD" "$rc"; then
    printf '\n%s\n' "$PRE_CMD" >>"$rc"
  fi
done
