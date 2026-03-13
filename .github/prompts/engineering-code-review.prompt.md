---
mode: agent
description: "Perform a comprehensive code review on staged changes or a PR"
# argument-hint: [--pr <number>] [--files <glob>] [--focus security|performance|style]
---


# Code Review

Perform a thorough code review covering code quality, security, performance, and test coverage. Uses a Technical Architect + Security Architect lens.

## Pre-flight Checks
1. Detect scope: if `--pr` flag, read PR diff via GitHub MCP; if `--files`, glob those paths; otherwise review `git diff HEAD`
2. Read `.claude/memory/project-state.md` for tech stack context
3. Note the `--focus` flag if provided to prioritize that dimension

## Phase 1: Scope Detection
- List all files changed and their change types (new/modified/deleted)
- Summarize what the PR/changeset is trying to accomplish
- Identify the highest-risk files (auth, data models, API contracts, config)

## Phase 2: Code Quality
For each file, check:
- **Correctness**: does the code do what it claims? Edge cases covered?
- **Readability**: are names clear? Are functions small and focused?
- **Complexity**: cyclomatic complexity, deeply nested logic
- **DRY violations**: duplicated logic that should be extracted
- **Error handling**: are failures handled gracefully?
- **Comments**: missing where logic is non-obvious; redundant elsewhere

## Phase 3: Security Scan
Apply OWASP Top 10 lens:
- Input validation at every boundary
- No hardcoded secrets or credentials
- SQL/NoSQL injection prevention (parameterized queries)
- XSS prevention in output rendering
- Authentication and authorization checks on every route
- Sensitive data in logs or responses
- Dependency vulnerabilities (flag any new packages added)

## Phase 4: Performance
- N+1 query patterns in loops
- Missing database indexes for new query patterns
- Synchronous calls that should be async
- Large data loads without pagination
- Missing caching opportunities
- Memory leaks (event listeners, open connections not closed)

## Phase 5: Test Coverage
- Are new code paths covered by tests?
- Are edge cases and error states tested?
- Are tests meaningful (not just coverage padding)?
- Are mocks appropriate or hiding real behavior?

## Phase 6: Review Summary
Output a structured review:

```markdown
## Code Review Summary

**Overall**: ✅ Approve | 🔄 Request Changes | ⚠️ Needs Discussion

### Critical Issues (must fix before merge)
- [ ] [file:line] [description]

### Suggestions (recommended improvements)
- [ ] [file:line] [description]

### Nits (optional, low priority)
- [ ] [file:line] [description]

### Security Findings
- [ ] [severity: HIGH/MED/LOW] [file:line] [description]

### Test Coverage
- Coverage: [N]% (target: 80%)
- Missing: [files/paths not covered]
```

## Error Handling
- No diff found: report "No staged changes detected"
- Binary files or generated code: skip and note in summary
- PR not accessible: fall back to local diff
