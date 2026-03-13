#!/bin/bash
# Setup symlinks for Claude Code ↔ GitHub Copilot compatibility
# Run once after cloning the repository
#
# Creates:
#   AGENTS.md                        → CLAUDE.MD (root, for Cursor)
#   .github/copilot-instructions.md  → ../.claude/CLAUDE.md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

echo "Setting up symlinks for AI Agent Team..."
echo "Root: $ROOT"
echo ""

setup_symlink() {
  local target="$1"
  local link="$2"
  local desc="$3"

  if [ -L "$link" ]; then
    echo "↺  $link already symlinked (skipping)"
    return
  fi

  if [ -e "$link" ]; then
    echo "⚠  $link exists as a real file/dir — skipping to avoid overwrite"
    echo "   To replace it, delete it manually first"
    return
  fi

  # Create parent directory if needed
  mkdir -p "$(dirname "$link")"

  ln -sf "$target" "$link"
  echo "✓  $link → $target ($desc)"
}

# AGENTS.md → CLAUDE.MD (for Cursor and other tools that read AGENTS.md)
setup_symlink "CLAUDE.MD" "AGENTS.md" "Cursor / OpenAI agents compatibility"

# .github/copilot-instructions.md → .claude/CLAUDE.md
setup_symlink "../.claude/CLAUDE.md" ".github/copilot-instructions.md" "GitHub Copilot instructions"

echo ""
echo "Symlinks configured. Now run:"
echo "  bash scripts/sync-commands.sh"
echo "to generate .github/prompts/ from plugin commands"
