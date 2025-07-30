#!/usr/bin/env bash
set -euo pipefail

AGENT_NAME="${1:-}"

if [[ -z "$AGENT_NAME" ]]; then
  echo "Usage: $0 <agent_name>" >&2
  exit 1
fi

# Ensure runtime directories exist
mkdir -p logs
mkdir -p .codex/.state

LOG_FILE="logs/${AGENT_NAME}_$(date +%Y-%m-%d_%H-%M-%S).log"

{
  echo "[Codex] Running agent: $AGENT_NAME"
  echo "Logs: $LOG_FILE"
} | tee -a "$LOG_FILE"

# Attempt to run the Codex agent
npx codex run "$AGENT_NAME" --state "$(pwd)/.codex/.state" | tee -a "$LOG_FILE"
