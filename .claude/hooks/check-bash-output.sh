#!/bin/bash
# PostToolUse: Bash — Detect and surface silent script failures
# Logs failures to bash-failures.log; emits visible warning for critical scripts

set -euo pipefail

INPUT=$(cat)
LOG_DIR="$CLAUDE_PROJECT_DIR/.claude/logs"
mkdir -p "$LOG_DIR"
FAILURES_LOG="$LOG_DIR/bash-failures.log"

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

STATUS=$(echo "$INPUT" | jq -r '.status // "unknown"' 2>/dev/null || echo "unknown")
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""' 2>/dev/null || echo "")
OUTPUT=$(echo "$INPUT" | jq -r '.tool_response // ""' 2>/dev/null | head -c 500 || echo "")

# Critical scripts whose failures must be surfaced loudly
CRITICAL_PATTERNS=(
  "sync-commands.sh"
  "setup-symlinks.sh"
  "\.claude/hooks/"
  "validate-plugin-json"
  "validate-agent-md"
)

is_critical() {
  for pattern in "${CRITICAL_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qE "$pattern"; then
      return 0
    fi
  done
  return 1
}

if [ "$STATUS" = "error" ]; then
  echo "[$(timestamp)] [BASH-FAIL] status=error cmd=${COMMAND:0:200} output=${OUTPUT:0:300}" >> "$FAILURES_LOG"

  if is_critical; then
    # Print to stdout so Claude sees it in the tool result context
    echo "WARNING: Critical script failed — '$COMMAND' exited with error. Check .claude/logs/bash-failures.log for details." >&2
  fi

  echo "$INPUT"
  exit 0
fi

# Success path: check output for soft failure patterns (log only, non-blocking)
SOFT_FAIL_PATTERNS=("Error:" "FAILED" "command not found" "No such file" "Permission denied")
for pattern in "${SOFT_FAIL_PATTERNS[@]}"; do
  if echo "$OUTPUT" | grep -qi "$pattern"; then
    echo "[$(timestamp)] [BASH-WARN] Soft failure pattern '$pattern' in output of: ${COMMAND:0:200}" >> "$FAILURES_LOG"

    if is_critical; then
      echo "WARNING: Possible failure in critical script '$COMMAND' — pattern '$pattern' detected in output." >&2
    fi
    break
  fi
done

echo "$INPUT"
exit 0
