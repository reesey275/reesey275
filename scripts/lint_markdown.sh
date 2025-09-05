#!/usr/bin/env bash
set -euo pipefail

MAX_LEN=${MAX_LEN:-120}

files=("$@")
if [ ${#files[@]} -eq 0 ]; then
  mapfile -t files < <(git ls-files '*.md')
fi

status=0
for file in "${files[@]}"; do
  long_lines=$(awk -v max="$MAX_LEN" 'length($0) > max {print FNR":"$0}' "$file")
  if [ -n "$long_lines" ]; then
    echo "Lines longer than $MAX_LEN characters in $file:"
    echo "$long_lines"
    status=1
  fi
  trailing=$(grep -n '[[:blank:]]$' "$file" || true)
  if [ -n "$trailing" ]; then
    echo "Trailing whitespace in $file:"
    echo "$trailing"
    status=1
  fi
done

exit $status
