---
name: project-memory-init
description: Bootstrap the three Claude agent memory files (project-state.md, sprint-context.md, decisions.md) by scanning the repo structure, git history, and any existing docs. Run this when memory files are empty or when starting fresh on a project.
disable-model-invocation: false
---

# Project Memory Init

You are bootstrapping the Claude agent memory system for this project. Your job is to populate all three memory files with real, accurate content derived from the repository — not generic templates.

## Memory Files to Populate

All three live in `.claude/memory/`:

1. **project-state.md** — Tech stack, services, integrations, known debt
2. **sprint-context.md** — Active sprint context (or note if no sprint system is in use)
3. **decisions.md** — Architecture decision log (ADR format)

## Research Steps

### Step 1: Gather Project Facts
Read these files (if present) to understand the project:
- `CLAUDE.md` and `.claude/CLAUDE.md` (agent team and tech stack defaults)
- `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml` (dependencies and runtime)
- `README.md` or `docs/` (project overview)
- `.mcp.json` (integrations)
- `azure-pipelines/` or `.github/workflows/` (CI/CD setup)

### Step 2: Scan Git History
Run `git log --oneline -20` to understand recent activity and infer what's being worked on.

### Step 3: Identify Architecture Decisions
Look for evidence of major decisions in commit messages, docs, or config files. Each becomes an ADR entry.

## Output

Write populated content to all three memory files. Use the formats below.

### project-state.md format
```markdown
# Project State

## Tech Stack
- **Runtime**: [detected]
- **Framework**: [detected]
- **Database**: [detected]
- **Cloud**: [detected]
- **CI/CD**: [detected]

## Services & Integrations
- [list MCP servers, external APIs, etc.]

## Key Directories
- [important paths and what they contain]

## Known Debt / Watchpoints
- [anything flagged in docs or commit messages]

_Last updated: [date]_
```

### sprint-context.md format
```markdown
# Sprint Context

## Current Sprint
[Sprint name/number or "No active sprint tracking detected"]

## Active Work
[From recent git commits or docs]

## Blockers
[None known / list if found]

## Notes
[Anything else relevant to active development]

_Last updated: [date]_
```

### decisions.md format
```markdown
# Architecture Decision Log

## ADR-001: [Title]
- **Date**: [date]
- **Status**: Accepted
- **Context**: [why this decision was made]
- **Decision**: [what was decided]
- **Consequences**: [what changes as a result]

[Add more ADRs as discovered]
```

## Rules
- Only write what you can actually observe in the repo — no hallucinated content
- If you can't determine a value, write "Unknown — update manually"
- After writing all three files, print a summary of what was populated
