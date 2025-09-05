#!/usr/bin/env bash
set -euo pipefail

# Map CI_PROFILE_PUSH_TOKEN or CODEX_AGENT_AUTH to the standard GH_TOKEN
if [[ -z "${GH_TOKEN:-}" ]]; then
  token="${CI_PROFILE_PUSH_TOKEN:-${CODEX_AGENT_AUTH:-}}"
  if [[ -n "$token" ]]; then
    export GH_TOKEN="$token"
  fi
  unset token
fi

# If gh is installed and a token is available, authenticate non-interactively
if [[ -n "${GH_TOKEN:-}" ]] && command -v gh >/dev/null 2>&1; then
  if ! gh auth status >/dev/null 2>&1; then
    printf %s "$GH_TOKEN" | gh auth login --with-token >/dev/null 2>&1
  fi
fi

