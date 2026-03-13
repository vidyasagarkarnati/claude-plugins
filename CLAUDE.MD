# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# One-time setup after clone (creates symlinks for Copilot + Cursor compatibility)
bash scripts/setup-symlinks.sh

# Sync plugin commands → GitHub Copilot prompt format
bash scripts/sync-commands.sh
```

CI is handled by two Azure Pipelines workflows:
- `azure-pipelines/agent-team-ci.yml` — validates agent definitions and hook scripts
- `azure-pipelines/sync-prompts.yml` — auto-syncs plugin commands to Copilot on push

No traditional build/test/lint pipeline exists — the project is configuration-as-code (Markdown agent definitions).

## Architecture

This repo implements a **25-agent AI engineering team** for Claude Code and GitHub Copilot. Agents cover the full software engineering lifecycle across 7 plugin domains.

### Plugin Structure

Each plugin lives in `plugins/{domain}/` and follows this layout:

```
plugins/{domain}/
├── .claude-plugin/plugin.json   # Glob patterns registering agents, skills, commands
├── agents/{name}.md             # Agent definition (frontmatter: name, model, color)
├── skills/{name}/SKILL.md       # Reusable knowledge package
└── commands/{name}.md           # Slash-command workflow (frontmatter: description, argument-hint)
```

**7 Plugins:** `leadership`, `architecture`, `cloud`, `engineering`, `platform`, `marketing`, `orchestrators`

### Agents

Agent files use YAML frontmatter (`name`, `model`, `description`) followed by sections: Core Mission, Capabilities, Behavioral Traits, Response Approach. The `description` field is the auto-activation trigger Claude reads to decide which agent to invoke.

Models are assigned by complexity: `opus` for strategic/architectural agents, `sonnet` for engineering/product agents, `haiku` for lightweight coordination agents.

Invoke with `/plugin:agent-name` or let Claude auto-select based on task keywords.

### Commands & Orchestrators

**12 commands** across domains (e.g., `/leadership:create-prd`, `/architecture:create-tdd`, `/engineering:code-review`).

**8 orchestrators** in `plugins/orchestrators/commands/` chain multiple agents sequentially:
- `prd-workflow` → PM → Tech Architect → Scrum Master
- `full-sdlc` → Full-Stack Dev → QA → MongoDB DBA
- `code-review-flow` → Tech Architect → Security Architect → Full-Stack Dev
- `bug-fix-flow` → Full-Stack Dev → QA → Test Coverage Agent
- `deploy-flow` → Cloud Architect → FinOps → QA
- (plus `brainstorm`, `doc-flow`, `sprint-workflow`)

### Hook System

`.claude/settings.json` registers 8 automation hooks in `.claude/hooks/`:

| Hook | Trigger | Purpose |
|------|---------|---------|
| `inject-context.sh` | SessionStart | Loads `.claude/memory/` into session context |
| `security-check.sh` | PreToolUse[Bash] | Blocks dangerous shell patterns |
| `audit-log.sh` | PostToolUse | Logs all tool invocations to `.claude/logs/` |
| `validate-output.sh` | Stop | Checks for incomplete output signals |
| `log-handoff.sh` + `notify-next-agent.sh` | SubagentStop | Tracks agent-to-agent handoffs |
| `teammate-sync.sh` | TeammateIdle/TaskCompleted | Syncs sprint state across agents |

### Memory System

`.claude/memory/` holds three files agents read and update:
- `project-state.md` — tech stack, services, integrations, known debt
- `sprint-context.md` — active sprint, tickets, blockers, velocity (managed by Scrum Master agent)
- `decisions.md` — ADR log (Michael Nygard format; every architectural decision gets an entry)

`.claude/CLAUDE.md` is the shared agent memory foundation (agent roster, orchestrator chains, quality standards, MCP assignments). Do not confuse it with this file.

### MCP Tools

Configured in `.mcp.json` — 5 tools with API keys via env vars: `firecrawl`, `perplexity`, `playwright`, `hunter`, `azure-devops`. See `.claude/CLAUDE.md` for which agents use which tools.

### Dual-Tool Compatibility

`scripts/setup-symlinks.sh` creates symlinks so the same agent/command definitions work in GitHub Copilot Chat (`@workspace /command`) and Cursor. `scripts/sync-commands.sh` translates plugin commands to Copilot `.github/prompts/` format.

---

## Workflow Orchestration

### 1. Plan Node Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately – don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

### 3. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes – don't over-engineer
- Challenge your own work before presenting it

### 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests – then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

## Task Management

1. **Plan First**: Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to `tasks/todo.md`
6. **Capture Lessons**: Update `tasks/lessons.md` after corrections

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.
