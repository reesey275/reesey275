#!/usr/bin/env bash
set -euo pipefail

MAX_LEN=${MAX_LEN:-120}

files=("$@")
if [ ${#files[@]} -eq 0 ]; then
  files=(README.md)
  while IFS= read -r -d '' file; do
    files+=("$file")
  done < <(find docs -name '*.md' -print0)
fi

for file in "${files[@]}"; do
  long_lines=$(awk -v max="$MAX_LEN" 'length($0) > max {print FNR":"$0}' "$file")
  trailing=$(grep -n '[[:blank:]]$' "$file" || true)
  if [ -n "$long_lines" ]; then
    echo "Lines longer than $MAX_LEN characters in $file:"
    echo "$long_lines"
  fi
  if [ -n "$trailing" ]; then
    echo "Trailing whitespace in $file:"
    echo "$trailing"
  fi
  if [ -z "$long_lines" ] && [ -z "$trailing" ]; then
    echo "$file: OK"
  fi
done

exit 0
