#!/bin/bash
# Sync plugin commands → .github/prompts/*.prompt.md
# Translates Claude Code command syntax to GitHub Copilot prompt syntax
#
# Sources:
#   plugins/leadership/commands/*.md    → /leadership:* commands
#   plugins/architecture/commands/*.md  → /architecture:* commands
#   plugins/cloud/commands/*.md         → /cloud:* commands
#   plugins/engineering/commands/*.md   → /engineering:* commands
#   plugins/orchestrators/commands/*.md → /orchestrators:* commands
#
# Differences handled:
#   Claude Code: $ARGUMENTS
#   Copilot:     ${input:arguments}
#
#   Claude Code: no frontmatter required (description is inline)
#   Copilot:     requires YAML frontmatter with mode and description

set -euo pipefail

PROMPTS_DIR="${1:-.github/prompts}"

# Change to repo root if running from scripts/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

mkdir -p "$PROMPTS_DIR"

COUNT=0
ERRORS=0

sync_command() {
  local file="$1"
  local prefix="$2"
  local name
  name=$(basename "$file" .md)
  local output="$PROMPTS_DIR/${prefix}-${name}.prompt.md"

  # Extract description from frontmatter or first H1
  local desc=""
  if grep -q "^description:" "$file"; then
    desc=$(grep "^description:" "$file" | head -1 | sed 's/^description: *//;s/^"//;s/"$//')
  else
    desc=$(grep "^# " "$file" | head -1 | sed 's/^# //')
  fi
  [ -z "$desc" ] && desc="$name"

  # Extract argument-hint if present
  local arg_hint=""
  if grep -q "^argument-hint:" "$file"; then
    arg_hint=$(grep "^argument-hint:" "$file" | head -1 | sed 's/^argument-hint: *//;s/^"//;s/"$//')
  fi

  # Build body: strip existing frontmatter, replace $ARGUMENTS with ${input:arguments}
  local body
  body=$(awk '/^---/{found++; if(found==2){skip=0; next}} found<2{next} {print}' "$file" | \
    sed 's/\$ARGUMENTS/${input:arguments}/g')

  # If no frontmatter, use whole file
  if [ -z "$body" ]; then
    body=$(sed 's/\$ARGUMENTS/${input:arguments}/g' "$file")
  fi

  {
    echo "---"
    echo "mode: agent"
    echo "description: \"${desc}\""
    [ -n "$arg_hint" ] && echo "# argument-hint: ${arg_hint}"
    echo "---"
    echo ""
    echo "$body"
  } > "$output"

  echo "✓ /${prefix}:${name} → $output"
  COUNT=$((COUNT + 1))
}

# Sync each plugin's commands
for plugin in leadership architecture cloud engineering; do
  if [ -d "plugins/${plugin}/commands" ]; then
    for file in "plugins/${plugin}/commands"/*.md; do
      [ -f "$file" ] || continue
      sync_command "$file" "$plugin"
    done
  fi
done

# Sync orchestrators
if [ -d "plugins/orchestrators/commands" ]; then
  for file in "plugins/orchestrators/commands"/*.md; do
    [ -f "$file" ] || continue
    sync_command "$file" "orchestrators"
  done
fi

echo ""
echo "Synced $COUNT commands to $PROMPTS_DIR"
if [ "$ERRORS" -gt 0 ]; then
  echo "Errors: $ERRORS"
  exit 1
fi
