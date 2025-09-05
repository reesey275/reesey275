#!/usr/bin/env bash
set -euo pipefail
: "${GH_TOKEN:=${CI_PROFILE_PUSH_TOKEN:-${CODEX_AGENT_AUTH:-}}}"
if [ -n "${GH_TOKEN:-}" ] && command -v gh >/dev/null 2>&1; then
  if ! gh auth status >/dev/null 2>&1; then
    printf %s "$GH_TOKEN" | gh auth login --with-token
  fi
fi
