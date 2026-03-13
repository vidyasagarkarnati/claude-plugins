#!/bin/bash
# Stop — Validate output before marking task complete
# Checks for common incompleteness signals

set -euo pipefail

INPUT=$(cat)
RESPONSE=$(echo "$INPUT" | jq -r '.response // ""' 2>/dev/null || echo "")
LOG_DIR="$CLAUDE_PROJECT_DIR/.claude/logs"
mkdir -p "$LOG_DIR"

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[$(timestamp)] [VALIDATE] $1" >> "$LOG_DIR/validation.log"; }

if [ -z "$RESPONSE" ]; then
  echo "$INPUT"
  exit 0
fi

WORD_COUNT=$(echo "$RESPONSE" | wc -w | tr -d ' ')
log "Validating output (${WORD_COUNT} words)"

# Check for incompleteness signals
INCOMPLETE_PATTERNS=(
  "TODO:"
  "FIXME:"
  "placeholder"
  "not implemented"
  "coming soon"
  "\.\.\.$"
  "to be continued"
)

for pattern in "${INCOMPLETE_PATTERNS[@]}"; do
  if echo "$RESPONSE" | grep -qi "$pattern"; then
    log "WARN: Possible incomplete output — found pattern: '$pattern'"
  fi
done

# Check for very short responses on likely code tasks
if echo "$RESPONSE" | grep -qi "```" && [ "$WORD_COUNT" -lt 20 ]; then
  log "WARN: Code block present but very short response (${WORD_COUNT} words)"
fi

log "Validation complete"
echo "$INPUT"
exit 0
