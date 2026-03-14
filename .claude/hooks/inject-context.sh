#!/bin/bash
# SessionStart — Inject project context into session
# Reads sprint-context.md and project-state.md, outputs as context

set -euo pipefail

MEMORY_DIR="$CLAUDE_PROJECT_DIR/.claude/memory"
LOG_DIR="$CLAUDE_PROJECT_DIR/.claude/logs"
mkdir -p "$LOG_DIR"

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[$(timestamp)] [INJECT] $1" >> "$LOG_DIR/session.log"; }

log "Session started"

CONTEXT=""

# Load project state if exists
if [ -f "$MEMORY_DIR/project-state.md" ]; then
  CONTEXT="${CONTEXT}\n\n## Project State\n$(cat "$MEMORY_DIR/project-state.md")"
  log "Loaded project-state.md"
fi

# Load sprint context if exists
if [ -f "$MEMORY_DIR/sprint-context.md" ]; then
  CONTEXT="${CONTEXT}\n\n## Sprint Context\n$(cat "$MEMORY_DIR/sprint-context.md")"
  log "Loaded sprint-context.md"
fi

# Load recent decisions (last 5 ADRs) if exists
if [ -f "$MEMORY_DIR/decisions.md" ]; then
  RECENT=$(grep -A 20 "^## ADR-" "$MEMORY_DIR/decisions.md" | tail -80)
  CONTEXT="${CONTEXT}\n\n## Recent Architecture Decisions\n${RECENT}"
  log "Loaded decisions.md"
fi

# Warn if memory files are empty/template only
TEMPLATE_MARKER="<!-- Replace this"
for f in project-state.md sprint-context.md decisions.md; do
  fpath="$MEMORY_DIR/$f"
  if [ -f "$fpath" ]; then
    wc=$(wc -w < "$fpath")
    if [ "$wc" -lt 20 ] || grep -q "$TEMPLATE_MARKER" "$fpath" 2>/dev/null; then
      echo "WARNING: $f appears to be an unpopulated template. Run /project-memory-init to bootstrap agent memory." >&2
      log "Memory file $f is unpopulated (${wc} words)"
    fi
  fi
done

if [ -n "$CONTEXT" ]; then
  echo "CONTEXT_INJECTED=true"
  log "Context injection complete"
else
  log "No context files found, skipping injection"
fi

exit 0
