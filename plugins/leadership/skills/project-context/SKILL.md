---
name: project-context
description: How to read and update project state from .claude/memory/, sprint context conventions, architecture decision logging, and shared state protocols
---

# Project Context

This skill governs how agents read, update, and share project state through the `.claude/memory/` directory. Consistent use of these conventions enables the entire agent team to stay synchronized.

## When to Use This Skill
- Starting a new session and loading project context
- Completing work and updating sprint or project state
- Recording a new architecture decision
- Handing off between agents in an orchestrator workflow
- Checking what the current sprint goal or tech stack is

## Core Concepts

### 1. Memory File Responsibilities
| File | Owner(s) | Updated When |
|------|----------|-------------|
| `project-state.md` | Technical Architect, CTO | Tech stack changes, new services, major decisions |
| `sprint-context.md` | Scrum Master, Engineering Manager | Sprint start/end, ticket status changes |
| `decisions.md` | Technical Architect, Architecture Docs Agent | New ADR added |

### 2. Read Protocol
Every agent should read relevant memory files at the start of a task:
1. `project-state.md` — for tech stack, services, and architecture context
2. `sprint-context.md` — for current sprint goal and active tickets
3. `decisions.md` — for recent ADRs that might constrain the work

### 3. Write Protocol
Only update memory files when you have new information that would help other agents. Don't write if the info is already there or will be outdated quickly.

## Quick Reference
```bash
# Read all memory at session start
cat .claude/memory/project-state.md
cat .claude/memory/sprint-context.md
grep "^## ADR-" .claude/memory/decisions.md | tail -5  # last 5 ADRs

# Check if sprint context is stale (older than 2 weeks)
stat .claude/memory/sprint-context.md | grep Modify
```

## Key Patterns

### Pattern 1: Session Start Context Load
```markdown
## At session start, agents should:

1. Read project-state.md → understand tech stack and current architecture
2. Read sprint-context.md → understand active sprint goal and tickets
3. Check decisions.md for ADRs added in the last 30 days
4. Set working context: "I'm working on [ticket] in [sprint] using [tech stack]"
```

### Pattern 2: Updating Sprint Context
```markdown
## When completing a ticket, update sprint-context.md:

BEFORE:
| PROJ-234 | Add CSV export | Alice | 5 | In Progress |

AFTER:
| PROJ-234 | Add CSV export | Alice | 5 | Done |

Also update "Done This Sprint" section.
Note: Don't update if you're not certain the ticket is actually complete.
```

### Pattern 3: Adding an ADR
```markdown
## When recording a new architecture decision in decisions.md:

1. Increment the ADR number (look at the last ADR in the file)
2. Use the template at the top of decisions.md
3. Set Status: Proposed (if still being discussed) or Accepted (if decided)
4. Include Deciders and Context that future readers will need
5. Reference the relevant code PR or branch in the ADR body

Example addition:
## ADR-002: Use Redis for session storage

**Date**: 2026-03-13
**Status**: Accepted
**Deciders**: Technical Architect

### Context
[...]
```

### Pattern 4: Agent Handoff Context
```markdown
## When handing off to the next agent in a chain:

Provide a handoff summary containing:
1. What was done (files changed, decisions made)
2. What was found (relevant context the next agent needs)
3. What is still open (questions, blockers, deferred items)
4. Where to find the artifacts (file paths)

Example:
"PRD complete at docs/prd-csv-export.md. Key constraints: max 1M rows,
must work for all user roles. Open question: should export be async
(email) or sync (download)? Tagged [NEEDS INPUT] in the PRD. TDD
should address both options. Tech stack: Node.js + MongoDB."
```

## Best Practices
1. Read before writing — don't overwrite sprint context that another agent updated
2. Be concise — memory files are read by every agent; keep them scannable
3. Use absolute dates, not relative ("2026-03-13" not "last Thursday")
4. Don't duplicate information that's in the codebase — memory is for context only
5. Mark open questions clearly with `[NEEDS INPUT: who]`
6. Clear stale sprint context at sprint start — old tickets confuse agents

## Common Issues
- **Agents using stale tech stack info**: ensure project-state.md is updated when stack changes
- **Sprint context shows completed sprints**: Scrum Master should archive and reset at sprint end
- **Duplicate ADRs**: always grep decisions.md for the topic before adding a new one
