#!/bin/bash
set -euo pipefail

trap 'echo "Error: devonboarder setup failed at line $LINENO" >&2' ERR

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

readonly LEGACY_TASKS=("phase-status" "list-guardrails")

show_help() {
  cat <<'EOF'
DevOnboarder setup shim
-----------------------
This script keeps the legacy Bash entry point available while the onboarding
automation migrates to the shared Python runner.

Usage: scripts/setup.sh [command]

Commands:
  phase-status     Print the current onboarding phase configuration.
  list-guardrails  Show the guardrail checks enforced locally.
  help             Display this message.

If the Python runner is installed, the command will be delegated to it.
EOF
}

delegate_to_python() {
  if [[ -x "${ROOT_DIR}/.venv/bin/devonboarder" ]]; then
    "${ROOT_DIR}/.venv/bin/devonboarder" "$@"
    exit 0
  fi

  if command -v devonboarder >/dev/null 2>&1; then
    devonboarder "$@"
    exit 0
  fi
}

command="${1:-help}"
shift || true

delegate_to_python "${command}" "$@"

case "${command}" in
  phase-status)
    cat <<EOF
Phases: orientation → immersion → autonomy
Quality threshold: 95%
Hybrid framework: Bash shim delegating to Python runner when available.
EOF
    ;;
  list-guardrails)
    cat <<'EOF'
Guardrail checks:
- Phase progression blocked when readiness drops below 95%.
- QC backlog auto-created from recurring AAR signals.
- Discord bot access audit runs before immersion tasks.
EOF
    ;;
  help|-h|--help)
    show_help
    ;;
  *)
    echo "Unknown command: ${command}" >&2
    printf 'Available commands: %s help\n' "${LEGACY_TASKS[*]}" >&2
    echo >&2
    show_help >&2
    exit 1
    ;;
esac
