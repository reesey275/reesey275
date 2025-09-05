#!/usr/bin/env bash
set -euo pipefail

files=("$@")
if [ ${#files[@]} -eq 0 ]; then
  mapfile -t files < <(git ls-files '*.md')
fi

status=0
for file in "${files[@]}"; do
  mapfile -t urls < <(grep -oE '(https?://|mailto:)[^)>"]+' "$file" | sort -u)
  for url in "${urls[@]}"; do
    if [[ $url == mailto:* ]]; then
      continue
    fi
    if ! code=$(curl -o /dev/null -s -w '%{http_code}' "$url"); then
      code=000
    fi
    if [[ $code == 000 ]]; then
      echo "$file: $url -> $code (skipped)"
      continue
    fi
    if [[ ! $code =~ ^2[0-9]{2}$ && ! $code =~ ^3[0-9]{2}$ ]]; then
      echo "$file: $url -> $code"
      status=1
    fi
  done
done

exit $status
