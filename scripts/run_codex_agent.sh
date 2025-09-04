#!/usr/bin/env bash
set -euo pipefail

AGENT_NAME="${1:-}"

if [[ -z "$AGENT_NAME" ]]; then
  echo "Usage: $0 <agent_name> (requires npx and the Codex CLI)" >&2
  exit 1
fi

# Verify dependencies
if ! command -v npx >/dev/null 2>&1; then
  echo "Error: npx is required but not installed. Please install Node.js." >&2
  exit 1
fi

if ! npx --no-install codex --version >/dev/null 2>&1; then
  echo "Codex CLI not found; attempting installation..." >&2
  if ! npm install -g @openai/codex >/dev/null 2>&1; then
    echo "Error: Codex CLI installation failed. Please install it globally or locally in your project." >&2
    exit 1
  fi
fi

# Ensure runtime directories exist
mkdir -p logs

LOG_FILE="logs/${AGENT_NAME}_$(date +%Y-%m-%d_%H-%M-%S).log"

{
  echo "[Codex] Running agent: $AGENT_NAME"
  echo "Logs: $LOG_FILE"
} | tee -a "$LOG_FILE"

# Attempt to run the Codex agent
npx codex exec "$AGENT_NAME" | tee -a "$LOG_FILE"
