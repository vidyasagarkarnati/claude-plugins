---
mode: agent
description: "Audit test coverage and generate missing tests for low-coverage files"
# argument-hint: [--threshold 80] [--path <dir>] [--framework jest|pytest|go]
---


# Coverage Audit

Audit test coverage across the codebase, identify under-covered files, generate missing tests, and verify improvement. Uses Test Coverage Agent persona.

## Pre-flight Checks
1. Parse `${input:arguments}` for `--threshold` (default: 80), `--path` (default: src/), `--framework` (auto-detect)
2. Auto-detect test framework: check for `jest.config.*`, `pytest.ini`, or `go.mod`
3. Confirm test runner is available

## Phase 1: Run Coverage Tool

### Jest (Node/TypeScript)
```bash
npx jest --coverage --coverageDirectory=coverage --coverageReporters=json-summary
cat coverage/coverage-summary.json | jq '.total'
```

### pytest (Python)
```bash
pytest --cov=src --cov-report=json --cov-report=term-missing
```

### Go
```bash
go test ./... -coverprofile=coverage.out
go tool cover -func=coverage.out
```

## Phase 2: Parse Report
Extract files below threshold:
```
File                    | Statements | Branches | Coverage |
------------------------|------------|----------|----------|
src/auth/service.ts     | 45/60      | 8/15     | 62%      ← BELOW
src/orders/handler.ts   | 72/80      | 20/22    | 91%      ✓
```

Sort by coverage percentage ascending (lowest first = highest priority).

## Phase 3: Prioritize
Focus on files that are:
1. **Critical path** (auth, payments, data mutations) — prioritize regardless of current coverage
2. **Complex** (high cyclomatic complexity, many branches)
3. **Recently changed** (new code with no tests)

Skip or deprioritize:
- Auto-generated files
- Simple getters/setters with no logic
- Third-party integration stubs

## Phase 4: Generate Tests
For each priority file:
- Read the source file
- Identify untested functions and branches
- Write tests covering:
  - Happy path for each public function
  - Error states (null inputs, invalid data, network failures)
  - Boundary conditions (empty arrays, zero values, max values)

Test naming convention: `describe('[function]', () => { it('[does X when Y]', ...) })`

## Phase 5: Re-Run and Verify
After adding tests, re-run coverage:
- Confirm overall coverage improved
- Confirm each targeted file is now above threshold
- Show before/after comparison

## Output Format
```markdown
## Coverage Audit Report

**Overall**: 73% → 84% (threshold: 80%) ✅

### Files Fixed
| File | Before | After |
|------|--------|-------|
| src/auth/service.ts | 62% | 88% |

### Files Still Below Threshold
| File | Coverage | Reason |
|------|----------|--------|
| src/legacy/parser.ts | 45% | Complex legacy code, needs refactor |

### Tests Added
- src/auth/service.test.ts: 6 new test cases
```

## Error Handling
- Coverage tool not installed: provide install command for the detected framework
- Tests fail after generation: report which tests fail and why
- No test framework detected: ask user to specify with `--framework`
