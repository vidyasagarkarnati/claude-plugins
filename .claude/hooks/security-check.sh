#!/bin/bash
# PreToolUse: Bash — Security gate before shell command execution
# Blocks dangerous patterns, logs all Bash tool invocations

set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""' 2>/dev/null || echo "")
LOG_DIR="$CLAUDE_PROJECT_DIR/.claude/logs"
mkdir -p "$LOG_DIR"
LOGFILE="$LOG_DIR/security-audit.log"

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

log() {
  echo "[$(timestamp)] [SECURITY] $1" >> "$LOGFILE"
}

# Patterns that require blocking
BLOCKED_PATTERNS=(
  "rm -rf /"
  "rm -rf \*"
  "dd if="
  "mkfs\."
  "> /dev/sd"
  "curl .* | bash"
  "curl .* | sh"
  "wget .* | bash"
  "wget .* | sh"
  ":(){:|:&};:"
  "chmod -R 777 /"
  "sudo rm -rf"
  "mv .* /dev/null"
)

# Patterns that require a warning (log but allow)
WARN_PATTERNS=(
  "sudo "
  "chmod 777"
  "curl "
  "wget "
  "eval "
  "exec "
  "base64 -d"
  "ssh "
  "scp "
  "aws.*delete"
  "aws.*destroy"
  "terraform destroy"
  "kubectl delete"
  "docker rm -f"
  "DROP TABLE"
  "DROP DATABASE"
)

if [ -z "$COMMAND" ]; then
  echo "$INPUT"
  exit 0
fi

log "Checking command: ${COMMAND:0:200}"

# Check blocked patterns
for pattern in "${BLOCKED_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qiE "$pattern" 2>/dev/null; then
    log "BLOCKED: Pattern '$pattern' matched in: ${COMMAND:0:200}"
    echo '{"decision": "block", "reason": "Security policy: potentially destructive command pattern detected. Pattern: '"$pattern"'"}'
    exit 0
  fi
done

# Check warning patterns
for pattern in "${WARN_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qiE "$pattern" 2>/dev/null; then
    log "WARN: Pattern '$pattern' matched in: ${COMMAND:0:200}"
    break
  fi
done

log "ALLOWED: ${COMMAND:0:200}"
echo "$INPUT"
exit 0
