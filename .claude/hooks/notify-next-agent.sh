#!/bin/bash
# SubagentStop — Notify next agent in an orchestrator chain
# Reads orchestrator chain config and signals the next agent

set -euo pipefail

INPUT=$(cat)
LOG_DIR="$CLAUDE_PROJECT_DIR/.claude/logs"
mkdir -p "$LOG_DIR"

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[$(timestamp)] [NOTIFY] $1" >> "$LOG_DIR/handoffs.log"; }

AGENT_NAME=$(echo "$INPUT" | jq -r '.agent_name // "unknown"' 2>/dev/null || echo "unknown")
WORKFLOW=$(echo "$INPUT" | jq -r '.workflow // ""' 2>/dev/null || echo "")
NEXT_AGENT=$(echo "$INPUT" | jq -r '.next_agent // ""' 2>/dev/null || echo "")

if [ -n "$NEXT_AGENT" ]; then
  log "Chain notification: $AGENT_NAME → $NEXT_AGENT (workflow: ${WORKFLOW:-direct})"
else
  log "No next agent in chain for $AGENT_NAME"
fi

echo "$INPUT"
exit 0
