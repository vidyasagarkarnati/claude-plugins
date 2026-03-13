# Architecture Decision Records

> Format: Michael Nygard ADR template
> Managed by: Technical Architect, Architecture Docs Agent
> New ADRs added by: `/update-architecture-docs` command or directly

---

## ADR Template

```
## ADR-NNN: [Title]

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-NNN
**Deciders:** [Names or roles]

### Context
[What is the issue that motivates this decision?]

### Decision
[What is the change being proposed/made?]

### Consequences
**Positive:**
- [Benefit]

**Negative:**
- [Trade-off]

**Risks:**
- [Risk]
```

---

## ADR-001: AI Agent Team Architecture

**Date:** 2026-03-13
**Status:** Accepted
**Deciders:** Technical Architect, CTO

### Context
Need a consistent agent system that works across Claude Code and GitHub Copilot without maintaining duplicate configurations.

### Decision
Use `.claude/` as the single source of truth. Symlink `.github/agents/` and `.github/skills/` to the Claude directories. Use a sync script to translate commands to Copilot prompt format (different syntax requirements).

### Consequences
**Positive:**
- Single place to update agent definitions
- Works on both platforms with zero duplication for agents/skills
- Commands auto-translated via pre-commit hook

**Negative:**
- Command syntax translation adds a build step
- Symlinks require setup script after clone

**Risks:**
- If Copilot changes its prompt format, sync script needs updating

---

<!-- Add new ADRs below this line -->
