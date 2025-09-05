#!/usr/bin/env bash
set -euo pipefail
# Assign GH_TOKEN from CI_PROFILE_PUSH_TOKEN or CODEX_AGENT_AUTH if not already set
if [ -z "${GH_TOKEN:-}" ]; then
  GH_TOKEN="${CI_PROFILE_PUSH_TOKEN:-${CODEX_AGENT_AUTH:-}}"
fi
if [ -n "${GH_TOKEN:-}" ] && command -v gh >/dev/null 2>&1; then
  if ! gh auth status >/dev/null 2>&1; then
    printf %s "$GH_TOKEN" | gh auth login --with-token
  fi
fi
