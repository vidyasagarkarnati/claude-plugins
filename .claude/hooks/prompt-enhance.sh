#!/bin/bash
# UserPromptSubmit — Prompt Engineer quality gate
# Checks prompt quality, adds context if missing, logs prompt patterns

set -euo pipefail

INPUT=$(cat)
PROMPT=$(echo "$INPUT" | jq -r '.prompt // ""' 2>/dev/null || echo "")
LOG_DIR="$CLAUDE_PROJECT_DIR/.claude/logs"
mkdir -p "$LOG_DIR"

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[$(timestamp)] [PROMPT] $1" >> "$LOG_DIR/prompts.log"; }

if [ -z "$PROMPT" ]; then
  echo "$INPUT"
  exit 0
fi

WORD_COUNT=$(echo "$PROMPT" | wc -w | tr -d ' ')
log "Prompt received (${WORD_COUNT} words): ${PROMPT:0:100}"

# Flag very short prompts (may need more context)
if [ "$WORD_COUNT" -lt 5 ]; then
  log "WARN: Very short prompt (${WORD_COUNT} words) — may lack context"
fi

# Log if prompt references specific agents (for analytics)
for agent in cto vp-engineering technical-architect security-architect product-manager qa-engineer full-stack; do
  if echo "$PROMPT" | grep -qi "$agent"; then
    log "Agent reference detected: $agent"
    break
  fi
done

# Pass through unchanged — enhancement is informational/logging only
echo "$INPUT"
exit 0
