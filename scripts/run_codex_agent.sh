#!/usr/bin/env bash
set -euo pipefail

# Pre-flight GitHub authentication using CI tokens if available
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/gh-preflight.sh" ]]; then
  # shellcheck source=scripts/gh-preflight.sh
  source "$SCRIPT_DIR/gh-preflight.sh"
fi

AGENT_NAME="${1:-}"

if [[ -z "$AGENT_NAME" ]]; then
  echo "Usage: $0 <agent_name> [additional_args...] (requires npx and the Codex CLI)" >&2
  exit 1
fi

# Shift to remove the first argument (agent name), leaving additional args in $@
shift
ADDITIONAL_ARGS=("$@")

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
# Run the Codex agent while capturing the exit status separately from tee
set +e
npx codex exec "$AGENT_NAME" "${ADDITIONAL_ARGS[@]}" | tee -a "$LOG_FILE"
status=${PIPESTATUS[0]}
set -e

if [[ $status -ne 0 ]]; then
  if grep -q "401 Unauthorized" "$LOG_FILE"; then
    {
      echo "Warning: Codex agent request returned 401 Unauthorized."
      echo "The profile_writer workflow requires valid Codex credentials."
      echo "Skipping with success so CI can continue without Codex access."
    } | tee -a "$LOG_FILE"
    exit 0
  fi

  echo "Error: Codex agent exited with status $status. See $LOG_FILE for details." | tee -a "$LOG_FILE"
  exit "$status"
fi
