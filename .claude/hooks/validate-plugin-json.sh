#!/bin/bash
# PostToolUse: Write, Edit — Validates plugin.json files against the official schema
# and checks that plugin version matches the entry in marketplace.json
# Catches schema violations and version drift immediately after any manifest edit

INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""' 2>/dev/null || echo "")

MARKETPLACE="$CLAUDE_PROJECT_DIR/.claude-plugin/marketplace.json"

# ── Helper ────────────────────────────────────────────────────────────────────
check_version_sync() {
  local plugin_json="$1"
  [ ! -f "$MARKETPLACE" ] && return 0

  # Derive plugin name from the directory two levels up (plugins/<name>/.claude-plugin/plugin.json)
  local plugin_dir
  plugin_dir=$(dirname "$(dirname "$plugin_json")")
  local plugin_name
  plugin_name=$(basename "$plugin_dir")

  local plugin_ver marketplace_ver
  plugin_ver=$(jq -r '.version // empty' "$plugin_json")
  marketplace_ver=$(jq -r --arg name "$plugin_name" \
    '.plugins[] | select(.name == $name) | .version // empty' "$MARKETPLACE")

  [ -z "$marketplace_ver" ] && return 0   # plugin not listed in marketplace — skip

  if [ "$plugin_ver" != "$marketplace_ver" ]; then
    echo ""
    echo "VERSION MISMATCH DETECTED"
    echo "  plugin.json:      $plugin_json  →  $plugin_ver"
    echo "  marketplace.json: $MARKETPLACE  →  $marketplace_ver  (entry: $plugin_name)"
    echo ""
    echo "Update marketplace.json to version $plugin_ver for plugin '$plugin_name'."
    return 1
  fi
  return 0
}

check_marketplace_sync() {
  local market_file="$1"
  [ ! -f "$market_file" ] && return 0

  local EXIT_CODE=0
  while IFS= read -r entry; do
    local name source version
    name=$(echo "$entry" | jq -r '.name')
    source=$(echo "$entry" | jq -r '.source')
    version=$(echo "$entry" | jq -r '.version')

    # Resolve source relative to CLAUDE_PROJECT_DIR
    local plugin_json="$CLAUDE_PROJECT_DIR/${source#./}/.claude-plugin/plugin.json"
    [ ! -f "$plugin_json" ] && continue

    local plugin_ver
    plugin_ver=$(jq -r '.version // empty' "$plugin_json")

    if [ "$version" != "$plugin_ver" ]; then
      echo ""
      echo "VERSION MISMATCH DETECTED"
      echo "  marketplace.json: plugin '$name'  →  $version"
      echo "  plugin.json:      $plugin_json    →  $plugin_ver"
      echo ""
      echo "Update marketplace.json entry '$name' to version $plugin_ver."
      EXIT_CODE=1
    fi
  done < <(jq -c '.plugins[]' "$market_file")

  return $EXIT_CODE
}

# ── Route by file type ────────────────────────────────────────────────────────
if [[ "$FILE" == *"/.claude-plugin/plugin.json" ]]; then
  [ ! -f "$FILE" ] && exit 0

  # 1. Valid JSON?
  if ! python3 -m json.tool "$FILE" > /dev/null 2>&1; then
    echo "ERROR: $FILE is not valid JSON"
    exit 1
  fi

  # 2. No unknown fields
  UNKNOWN=$(jq -r 'keys[]' "$FILE" | grep -vE '^(name|version|description)$' || true)
  if [ -n "$UNKNOWN" ]; then
    echo ""
    echo "PLUGIN MANIFEST VALIDATION FAILED"
    echo "  File:             $FILE"
    echo "  Unknown field(s): $UNKNOWN"
    echo "  Allowed fields:   name, version, description"
    echo ""
    echo "Remove the unknown field(s) to avoid a validation error on plugin install."
    exit 1
  fi

  # 3. Required fields present
  MISSING=""
  for key in "name" "version"; do
    VAL=$(jq -r --arg k "$key" '.[$k] // empty' "$FILE")
    [ -z "$VAL" ] && MISSING="$MISSING $key"
  done
  if [ -n "$MISSING" ]; then
    echo ""
    echo "PLUGIN MANIFEST VALIDATION FAILED"
    echo "  File:                    $FILE"
    echo "  Missing required field(s): $MISSING"
    echo "  Required fields:         name, version"
    exit 1
  fi

  # 4. Version in sync with marketplace.json
  if ! check_version_sync "$FILE"; then
    exit 1
  fi

  echo "✓ plugin.json valid: $FILE"
  exit 0

elif [[ "$FILE" == *"/.claude-plugin/marketplace.json" ]]; then
  [ ! -f "$FILE" ] && exit 0

  # Valid JSON?
  if ! python3 -m json.tool "$FILE" > /dev/null 2>&1; then
    echo "ERROR: $FILE is not valid JSON"
    exit 1
  fi

  # All plugin versions in sync?
  if ! check_marketplace_sync "$FILE"; then
    exit 1
  fi

  echo "✓ marketplace.json versions in sync"
  exit 0
fi

# Not a file we care about
exit 0
