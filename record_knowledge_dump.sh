#!/bin/bash
set -e
DUMP_DIR="codex/tasks"
mkdir -p "$DUMP_DIR"
FILE="${DUMP_DIR}/knowledge_dump_$(date +%Y-%m-%d_%H-%M-%S).md"

echo "Enter knowledge dump notes. Press Ctrl+D when done:"
NOTES=$(cat)

{
  echo "# Knowledge Dump - $(date)"
  echo
  echo "$NOTES"
} > "$FILE"

echo "Saved to $FILE"
