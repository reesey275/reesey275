#!/usr/bin/env bash
set -euo pipefail

files=("$@")
if [ ${#files[@]} -eq 0 ]; then
  files=(README.md)
  while IFS= read -r -d '' file; do
    files+=("$file")
  done < <(find docs -name '*.md' -print0)
fi

status=0
transient_status=0

connect_timeout=${LINK_CONNECT_TIMEOUT:-5}
max_time=${LINK_MAX_TIME:-15}
retry_count=${LINK_RETRIES:-2}

for file in "${files[@]}"; do
  mapfile -t urls < <(grep -oE 'https?://[^)>"]+' "$file" | sort -u || true)
  if [ ${#urls[@]} -eq 0 ]; then
    echo "$file: no links found"
    continue
  fi
  for url in "${urls[@]}"; do
    if ! code=$(curl \
      --connect-timeout "$connect_timeout" \
      --location \
      --max-time "$max_time" \
      --output /dev/null \
      --retry "$retry_count" \
      --retry-all-errors \
      --retry-delay 1 \
      --retry-max-time 30 \
      --silent \
      --show-error \
      --write-out '%{http_code}' \
      "$url"); then
      echo "$file: $url -> verification unavailable (transient/network failure)"
      transient_status=1
      continue
    fi
    if [[ $code =~ ^2[0-9]{2}$ || $code =~ ^3[0-9]{2}$ ]]; then
      echo "$file: $url -> $code"
    elif [[ $code == 401 || $code == 403 || $code == 408 || $code == 429 || $code =~ ^5[0-9]{2}$ ]]; then
      echo "$file: $url -> $code (verification unavailable; access blocked or transient)"
      transient_status=1
    else
      echo "$file: $url -> $code (confirmed accessibility failure)"
      status=1
    fi
  done
done

if ((status != 0)); then
  exit 1
fi
if ((transient_status != 0)); then
  exit 2
fi
exit 0
