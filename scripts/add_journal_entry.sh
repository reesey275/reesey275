#!/usr/bin/env bash

set -euo pipefail

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <journal-file> \"Title\" \"Summary\"" >&2
  exit 1
fi

file="$1"
title="$2"
summary="$3"

base="$(basename "$file")"

readme="journal_logs/README.md"
docs="docs/Journal_Index.md"

link_readme="- [$title]($base)"
if ! grep -Fqx "$link_readme" "$readme"; then
  printf '%s\n' "$link_readme" >> "$readme"
fi

link_docs="- [$title](../journal_logs/$base)"
if ! grep -Fqx "$link_docs" "$docs"; then
  {
    printf '%s\n' "$link_docs"
    printf '%s\n' "  – $summary"
  } >> "$docs"
fi

echo "Appended $base to journal indexes"

