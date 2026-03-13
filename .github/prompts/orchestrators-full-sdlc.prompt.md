---
mode: agent
description: "Full development cycle: Full-Stack Developer implements, QA Engineer tests, MongoDB DBA reviews data layer"
# argument-hint: <feature-or-ticket> [--tdd <path/to/tdd.md>]
---


# Full SDLC

End-to-end development workflow. Full-Stack Developer implements the feature, QA Engineer writes and runs tests, MongoDB DBA reviews the data layer if the feature touches the database.

## Chain

```
use_agent: full-stack-developer
```
**Input**: `${input:arguments}` — feature description or ticket reference; optionally the TDD path via `--tdd`
**Task**: Implement the feature end-to-end:
- Read the TDD (if provided) or infer requirements from the ticket
- Implement backend API changes first, then frontend
- Write unit tests alongside implementation (TDD style where possible)
- Follow existing code conventions (read 2–3 existing files first)
- Commit with descriptive message: `feat(<scope>): <what and why>`
**Handoff artifact**: List of files changed + summary of implementation decisions

---

```
use_agent: qa-engineer
```
**Input**: Implementation summary from Full-Stack Developer
**Task**: Quality assurance pass:
- Run existing test suite — confirm no regressions
- Write integration tests for new API endpoints
- Run E2E test for the primary user journey affected
- Check for edge cases not covered by unit tests
- Run `/coverage-audit --path <changed-dirs>` to verify coverage ≥ 80%
**Handoff artifact**: Test results summary + any failing tests + coverage report

---

```
use_agent: mongodb-dba
```
**Input**: Implementation summary (conditional — only if DB changes were made)
**Task**: Data layer review (only if schema/query changes detected):
- Review new/changed MongoDB schemas for design anti-patterns
- Check that indexes exist for all new query patterns
- Analyze aggregation pipeline performance (use `explain()`)
- Verify migration script (if schema change) is safe for production
- Flag any N+1 query patterns or missing projections
**Output**: Data layer review report (or "No DB changes detected — skipping")

## Output
By end of this workflow:
1. Feature implemented and committed
2. Tests written and passing (≥ 80% coverage on changed files)
3. Data layer reviewed (if applicable)
4. Summary report with implementation notes and any follow-up tickets

## Usage
```
/orchestrators:full-sdlc "PROJ-234: add export to CSV feature" --tdd docs/tdd-csv-export.md
```
