#!/usr/bin/env bash
set -euo pipefail

files=("$@")
if [ ${#files[@]} -eq 0 ]; then
  files=(README.md)
  while IFS= read -r -d '' file; do
    files+=("$file")
  done < <(find docs -name '*.md' -print0)
fi

for file in "${files[@]}"; do
  mapfile -t urls < <(grep -oE 'https?://[^)>"]+' "$file" | sort -u || true)
  if [ ${#urls[@]} -eq 0 ]; then
    echo "$file: no links found"
    continue
  fi
  for url in "${urls[@]}"; do
    code=$(curl -o /dev/null -s -w '%{http_code}' "$url") || code=000
    if [[ $code =~ ^2[0-9]{2}$ || $code =~ ^3[0-9]{2}$ ]]; then
      echo "$file: $url -> $code"
    else
      echo "$file: $url -> $code (broken)"
    fi
  done
done

exit 0
