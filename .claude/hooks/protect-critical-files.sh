#!/bin/bash
# PreToolUse: Write, Edit — Guard critical files from accidental overwrites
# Blocks full Write to marketplace.json and settings.json; warns on hook edits

set -euo pipefail

INPUT=$(cat)
LOG_DIR="$CLAUDE_PROJECT_DIR/.claude/logs"
mkdir -p "$LOG_DIR"
LOGFILE="$LOG_DIR/security-audit.log"

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

log() {
  echo "[$(timestamp)] [PROTECT] $1" >> "$LOGFILE"
}

TOOL=$(echo "$INPUT" | jq -r '.tool_name // ""' 2>/dev/null || echo "")
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""' 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ]; then
  echo "$INPUT"
  exit 0
fi

# Normalize to basename + partial path for matching
BASENAME=$(basename "$FILE_PATH")
NORMALIZED=$(echo "$FILE_PATH" | sed 's|.*claude-plugins/||')

# Block full Write (overwrite) to marketplace.json — must go through plugin.json flow
if [ "$TOOL" = "Write" ] && [ "$BASENAME" = "marketplace.json" ]; then
  log "BLOCKED: Attempted full Write to $FILE_PATH"
  echo '{"decision": "block", "reason": "marketplace.json must not be overwritten directly. Update plugin.json versions instead — the validate-plugin-json hook enforces version sync automatically."}'
  exit 0
fi

# Block full Write (overwrite) to settings.json — overwriting disables all hooks
if [ "$TOOL" = "Write" ] && [ "$BASENAME" = "settings.json" ] && echo "$FILE_PATH" | grep -q "\.claude/settings\.json"; then
  log "BLOCKED: Attempted full Write to $FILE_PATH"
  echo '{"decision": "block", "reason": ".claude/settings.json must not be overwritten — it controls all hook configuration. Use Edit for targeted changes instead."}'
  exit 0
fi

# Warn (allow) on any edits to hook scripts themselves
if echo "$FILE_PATH" | grep -qE "\.claude/hooks/.*\.sh$"; then
  log "WARN: Hook script being modified: $FILE_PATH (tool=$TOOL)"
fi

log "ALLOWED: $TOOL on $FILE_PATH"
echo "$INPUT"
exit 0
