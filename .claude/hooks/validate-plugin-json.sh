#!/bin/bash
# PostToolUse: Write, Edit — Validates plugin.json files against the official schema
# Catches unknown or invalid fields immediately after Claude writes/edits a plugin manifest

INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""' 2>/dev/null || echo "")

# Only run on .claude-plugin/plugin.json files
if [[ "$FILE" != *"/.claude-plugin/plugin.json" ]]; then
  exit 0
fi

# File must exist
if [ ! -f "$FILE" ]; then
  exit 0
fi

# Validate JSON syntax first
if ! python3 -m json.tool "$FILE" > /dev/null 2>&1; then
  echo "ERROR: $FILE is not valid JSON" >&2
  exit 1
fi

# Allowed top-level keys per the official Claude plugin schema
ALLOWED_KEYS=("name" "version" "description")

# Find any keys not in the allowed list
UNKNOWN=$(jq -r 'keys[]' "$FILE" | grep -vE '^(name|version|description)$' || true)

if [ -n "$UNKNOWN" ]; then
  echo ""
  echo "PLUGIN MANIFEST VALIDATION FAILED"
  echo "  File:         $FILE"
  echo "  Unknown field(s): $UNKNOWN"
  echo "  Allowed fields:   name, version, description"
  echo ""
  echo "Remove the unknown field(s) to avoid a validation error on plugin install."
  exit 1
fi

# Validate required fields are present
MISSING=""
for key in "name" "version"; do
  VAL=$(jq -r --arg k "$key" '.[$k] // empty' "$FILE")
  if [ -z "$VAL" ]; then
    MISSING="$MISSING $key"
  fi
done

if [ -n "$MISSING" ]; then
  echo ""
  echo "PLUGIN MANIFEST VALIDATION FAILED"
  echo "  File:           $FILE"
  echo "  Missing required field(s):$MISSING"
  echo "  Required fields: name, version"
  exit 1
fi

echo "✓ plugin.json valid: $FILE"
exit 0
