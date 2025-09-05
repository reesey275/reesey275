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

if ! grep -Fq "$base" "$readme"; then
  printf '%s\n' "- [$title]($base)" >> "$readme"
fi

if ! grep -Fq "$base" "$docs"; then
  {
    printf '%s\n' "- [$title](../journal_logs/$base)"
    printf '%s\n' "  – $summary"
  } >> "$docs"
fi

echo "Appended $base to journal indexes"

