#!/bin/bash
# TeammateIdle / TaskCompleted — Agent Teams coordination
# Syncs state between team members, updates shared task board

set -euo pipefail

INPUT=$(cat)
LOG_DIR="$CLAUDE_PROJECT_DIR/.claude/logs"
STATE_DIR="$CLAUDE_PROJECT_DIR/.claude/team-state"
mkdir -p "$LOG_DIR" "$STATE_DIR"

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[$(timestamp)] [TEAM-SYNC] $1" >> "$LOG_DIR/team.log"; }

EVENT=$(echo "$INPUT" | jq -r '.event // "unknown"' 2>/dev/null || echo "unknown")
AGENT=$(echo "$INPUT" | jq -r '.agent_name // "unknown"' 2>/dev/null || echo "unknown")
TASK=$(echo "$INPUT" | jq -r '.task_id // ""' 2>/dev/null || echo "")
STATUS=$(echo "$INPUT" | jq -r '.status // ""' 2>/dev/null || echo "")

case "$EVENT" in
  "TeammateIdle")
    log "Agent idle: $AGENT — checking for available tasks"
    ;;
  "TaskCompleted")
    log "Task completed: agent=$AGENT task=$TASK status=$STATUS"
    # Write completion record
    echo "{\"agent\":\"$AGENT\",\"task\":\"$TASK\",\"status\":\"$STATUS\",\"timestamp\":\"$(timestamp)\"}" \
      >> "$STATE_DIR/completions.jsonl"
    ;;
  *)
    log "Unknown event: $EVENT for agent $AGENT"
    ;;
esac

echo "$INPUT"
exit 0
