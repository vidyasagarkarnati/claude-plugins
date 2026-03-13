#!/bin/bash
# SubagentStop — Log agent handoff when a subagent completes
# Records which agent completed, what it produced, timing

set -euo pipefail

INPUT=$(cat)
LOG_DIR="$CLAUDE_PROJECT_DIR/.claude/logs"
mkdir -p "$LOG_DIR"
HANDOFF_LOG="$LOG_DIR/handoffs.log"

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

AGENT_NAME=$(echo "$INPUT" | jq -r '.agent_name // "unknown"' 2>/dev/null || echo "unknown")
TASK_ID=$(echo "$INPUT" | jq -r '.task_id // "unknown"' 2>/dev/null || echo "unknown")
STATUS=$(echo "$INPUT" | jq -r '.status // "completed"' 2>/dev/null || echo "completed")

echo "[$(timestamp)] [HANDOFF] agent=$AGENT_NAME task=$TASK_ID status=$STATUS" >> "$HANDOFF_LOG"

echo "$INPUT"
exit 0
