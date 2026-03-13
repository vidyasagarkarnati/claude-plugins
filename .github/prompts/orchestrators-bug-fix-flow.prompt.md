---
mode: agent
description: "Systematic bug fix: Full-Stack Developer diagnoses and fixes, QA Engineer verifies, Test Coverage Agent adds regression test"
# argument-hint: <bug-description-or-error>
---


# Bug Fix Flow

End-to-end bug resolution workflow. Full-Stack Developer diagnoses and fixes the bug, QA Engineer verifies the fix and tests edge cases, Test Coverage Agent adds a regression test.

## Chain

```
use_agent: full-stack-developer
```
**Input**: `${input:arguments}` — bug description, error message, or failing test
**Task**: Diagnose and fix:
- Run `/bug-fix ${input:arguments}`
- Find root cause, implement minimal fix
- Run existing tests to confirm no regressions
- Write a brief root cause analysis
**Handoff artifact**: Root cause analysis + files changed + fix description

---

```
use_agent: qa-engineer
```
**Input**: Fix summary from Full-Stack Developer
**Task**: Verification and edge case testing:
- Verify the fix resolves the originally reported bug
- Test adjacent behavior that the fix might have affected
- Check that error messages/states are handled gracefully
- Verify on all supported environments/configurations if applicable
- Report any new issues discovered during verification
**Handoff artifact**: QA verification report (PASS/FAIL per scenario) + any new bugs found

---

```
use_agent: test-coverage-agent
```
**Input**: Root cause + fixed files from Full-Stack Developer
**Task**: Regression test coverage:
- Identify the specific code path that contained the bug
- Verify a regression test exists that would have caught this bug
- If no regression test exists: write one that reproduces the original bug scenario
- Run `/coverage-audit --path <fixed-files>` to confirm coverage improved
**Output**: Regression test added (or confirmation it already existed) + coverage before/after

## Output
```
## Bug Fix Report: [bug description]

### Root Cause
[one sentence from Full-Stack Developer]

### Fix Summary
[what was changed]

### QA Verification
- Scenario 1: [description] → PASS
- Scenario 2: [edge case] → PASS

### Regression Test
- Added: [test file:test name]
- Coverage: [before]% → [after]%

### Status: RESOLVED ✅
```

## Usage
```
/orchestrators:bug-fix-flow "users getting 500 on /api/orders when cart is empty"
```
