#!/usr/bin/env bash
set -euo pipefail

# This script mirrors the CI markdownlint step and can optionally flag long lines
# and trailing whitespace via RUN_LINE_CHECKS=1.

MAX_LEN=${MAX_LEN:-120}
RUN_LINE_CHECKS=${RUN_LINE_CHECKS:-0}

status=0

repo_root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$repo_root"

files=("$@")
if [ ${#files[@]} -eq 0 ]; then
  while IFS= read -r -d '' file; do
    files+=("$file")
  done < <(find . -name '*.md' -not -path './node_modules/*' -not -path './.git/*' -print0)
fi

if [ "$RUN_LINE_CHECKS" -eq 1 ]; then
  for file in "${files[@]}"; do
    long_lines=$(awk -v max="$MAX_LEN" 'length($0) > max {print FNR":"$0}' "$file")
    trailing=$(grep -n '[[:blank:]]$' "$file" || true)
    if [ -n "$long_lines" ]; then
      echo "Lines longer than $MAX_LEN characters in $file:"
      echo "$long_lines"
      status=1
    fi
    if [ -n "$trailing" ]; then
      echo "Trailing whitespace in $file:"
      echo "$trailing"
      status=1
    fi
    if [ -z "$long_lines" ] && [ -z "$trailing" ]; then
      echo "$file: OK"
    fi
  done
fi

lint_cmd=("**/*.md" "#node_modules" "#.git")
if command -v markdownlint-cli2 >/dev/null 2>&1; then
  if ! markdownlint-cli2 "${lint_cmd[@]}"; then
    status=1
  fi
else
  if ! npx --yes markdownlint-cli2@0.20.0 "${lint_cmd[@]}"; then
    status=1
  fi
fi

exit $status
