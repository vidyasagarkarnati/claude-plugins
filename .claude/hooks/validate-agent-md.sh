#!/bin/bash
# PostToolUse[Write,Edit] — Validate agent/skill/command Markdown frontmatter
# Fires when any .md file inside plugins/ is written or edited

set -euo pipefail

LOG_DIR="$CLAUDE_PROJECT_DIR/.claude/logs"
mkdir -p "$LOG_DIR"

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[$(timestamp)] [VALIDATE-MD] $1" >> "$LOG_DIR/audit.log"; }

# Read the file path from tool input (passed via stdin as JSON)
TOOL_INPUT=$(cat)
FILE_PATH=$(echo "$TOOL_INPUT" | grep -o '"file_path":"[^"]*"' | cut -d'"' -f4 2>/dev/null || true)
# Also check "path" key (Edit tool uses "file_path", Write uses "file_path")
if [ -z "$FILE_PATH" ]; then
  FILE_PATH=$(echo "$TOOL_INPUT" | grep -o '"path":"[^"]*"' | cut -d'"' -f4 2>/dev/null || true)
fi

# Only validate .md files inside plugins/
if [ -z "$FILE_PATH" ] || [[ "$FILE_PATH" != *"/plugins/"* ]] || [[ "$FILE_PATH" != *".md" ]]; then
  exit 0
fi

if [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# Determine file type by path segment
if [[ "$FILE_PATH" == */agents/* ]]; then
  TYPE="agent"
  REQUIRED_FIELDS=("name" "model" "description")
elif [[ "$FILE_PATH" == */skills/*/SKILL.md ]]; then
  TYPE="skill"
  REQUIRED_FIELDS=("name" "description")
elif [[ "$FILE_PATH" == */commands/* ]]; then
  TYPE="command"
  REQUIRED_FIELDS=("description")
else
  exit 0
fi

# Extract frontmatter (between first pair of ---)
FRONTMATTER=$(awk '/^---/{count++; if(count==2) exit} count==1 && !/^---/{print}' "$FILE_PATH")

ERRORS=0
for field in "${REQUIRED_FIELDS[@]}"; do
  if ! echo "$FRONTMATTER" | grep -q "^${field}:"; then
    echo "ERROR: $TYPE file missing required frontmatter field '${field}': $FILE_PATH" >&2
    log "FAIL missing field '${field}' in $FILE_PATH"
    ERRORS=$((ERRORS + 1))
  fi
done

# Validate model values for agents
if [ "$TYPE" = "agent" ]; then
  MODEL=$(echo "$FRONTMATTER" | grep "^model:" | cut -d: -f2 | tr -d ' "')
  if [ -n "$MODEL" ] && [[ "$MODEL" != "opus" && "$MODEL" != "sonnet" && "$MODEL" != "haiku" ]]; then
    echo "ERROR: agent 'model' must be opus, sonnet, or haiku — got '${MODEL}': $FILE_PATH" >&2
    log "FAIL invalid model '${MODEL}' in $FILE_PATH"
    ERRORS=$((ERRORS + 1))
  fi
fi

if [ "$ERRORS" -gt 0 ]; then
  exit 1
fi

log "OK $TYPE frontmatter valid: $FILE_PATH"
exit 0
