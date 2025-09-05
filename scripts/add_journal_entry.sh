#!/usr/bin/env bash

set -euo pipefail

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <journal-file> \"Title\" \"Summary\" [readme-path] [docs-path]" >&2
  exit 1
fi

file="$1"
title="$2"
summary="$3"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(realpath "$script_dir/..")"
readme="${4:-$repo_dir/journal_logs/README.md}"
docs="${5:-$repo_dir/docs/Journal_Index.md}"

rel_readme="$(realpath --relative-to "$(dirname "$readme")" "$file")"
link_readme="- [$title]($rel_readme)"
if ! grep -Fqx "$link_readme" "$readme"; then
  printf '%s\n' "$link_readme" >> "$readme"
fi

rel_docs="$(realpath --relative-to "$(dirname "$docs")" "$file")"
link_docs="- [$title]($rel_docs)"
if ! grep -Fqx "$link_docs" "$docs"; then
  {
    printf '%s\n' "$link_docs"
    printf '%s\n' "  – $summary"
  } >> "$docs"
fi

echo "Appended $(basename "$file") to journal indexes"

