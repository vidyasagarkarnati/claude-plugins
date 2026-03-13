---
description: "Diagnose and fix a bug from a description, error log, or failing test"
argument-hint: "<bug-description-or-error-message>"
---

# Bug Fix

Systematically diagnose and fix a bug. No hand-holding — read the error, find the root cause, fix it, test it.

## Pre-flight Checks
1. Parse `$ARGUMENTS` for: error message, stack trace, failing test name, or symptom description
2. Read `.claude/memory/project-state.md` for tech stack
3. Search for recent related changes: `git log --oneline -20`

## Phase 1: Reproduce
- Identify exactly what triggers the bug (input, state, timing)
- If a test is failing, run it: `npm test -- --testNamePattern="<test>"` or `pytest -k "<test>"`
- If runtime error, locate the exact stack trace line
- Confirm the bug is reproducible before proceeding

## Phase 2: Root Cause Analysis
Work backwards from the symptom:
1. Identify the exact file and line where the error originates
2. Read the surrounding code — understand what it's supposed to do
3. Trace back through callers to find where the wrong value/state enters
4. Check recent git changes to the file: `git log -p --follow <file>`
5. Ask: is this a logic bug, data bug, race condition, or missing null check?

Document root cause in one sentence: "The bug is caused by X because Y."

## Phase 3: Fix
- Write the minimal change that fixes the root cause
- Do NOT fix unrelated issues in the same commit
- Ensure the fix handles all edge cases identified during analysis
- If the fix is non-obvious, add a comment explaining why

## Phase 4: Test
- Run the originally failing test to confirm it passes
- Run the full test suite for the affected module
- Write a new regression test if one doesn't exist:
  - Test name: `it('should <what the bug was>, <scenario>')`
  - Test should fail before the fix and pass after

## Phase 5: Document
- Write a one-paragraph explanation of root cause + fix
- Update `.claude/memory/decisions.md` if the fix reveals an architectural issue
- Suggest a follow-up ticket if the fix exposes a deeper systemic problem

## Output Format
```
## Bug Fix Report

**Root Cause**: [one sentence]
**Fix**: [what was changed and why]
**Files Modified**: [list]
**Tests Added/Updated**: [list]
**Regression Risk**: [LOW/MEDIUM/HIGH — what else could this affect]
**Follow-up**: [optional: ticket suggestion]
```

## Error Handling
- Cannot reproduce: document the attempted reproduction steps and ask for more context
- Root cause unclear after 3 levels of tracing: escalate to Technical Architect
- Fix requires breaking API change: document in ADR before proceeding
