#!/bin/bash
# PostToolUse — Audit log all tool invocations
# Records tool name, inputs summary, and outcome for compliance

set -euo pipefail

INPUT=$(cat)
LOG_DIR="$CLAUDE_PROJECT_DIR/.claude/logs"
mkdir -p "$LOG_DIR"
AUDIT_LOG="$LOG_DIR/audit.log"

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

TOOL=$(echo "$INPUT" | jq -r '.tool_name // "unknown"' 2>/dev/null || echo "unknown")
STATUS=$(echo "$INPUT" | jq -r '.status // "unknown"' 2>/dev/null || echo "unknown")

# Summarize input (truncate for log readability)
INPUT_SUMMARY=$(echo "$INPUT" | jq -r '.tool_input // {}' 2>/dev/null | head -c 200 || echo "{}")

echo "[$(timestamp)] [AUDIT] tool=$TOOL status=$STATUS input=${INPUT_SUMMARY}" >> "$AUDIT_LOG"

echo "$INPUT"
exit 0
