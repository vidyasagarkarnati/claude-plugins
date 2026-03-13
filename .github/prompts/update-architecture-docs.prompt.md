---
mode: agent
description: "Scan repo for architecture docs, detect drift from code, and update stale content"
# argument-hint: [--path <dir>] [--create-adrs] [--output-report]
---


# Update Architecture Docs

Scan the repository for architecture documentation, compare it against actual code structure, detect drift, update stale sections, and create missing ADRs. Uses Architecture Docs Agent persona.

## Pre-flight Checks
1. Parse `${input:arguments}` for `--path` (default: repo root), `--create-adrs` flag, `--output-report` flag
2. Read `.claude/memory/project-state.md` for known architecture
3. Read `.claude/memory/decisions.md` for existing ADRs

## Phase 1: Find Existing Docs
Search for documentation files:
```bash
find . -name "*.md" -not -path "*/node_modules/*" -not -path "*/.git/*"
find . -name "*.adoc" -name "architecture*"
find . -name "*.drawio" -name "*.puml" -name "*.mermaid"
```

Catalog found docs by type:
- **Architecture docs**: files in `docs/architecture/`, `docs/design/`, `ARCHITECTURE.md`
- **ADRs**: files matching `adr-*.md`, `decisions/`, `.claude/memory/decisions.md`
- **READMEs**: root and per-service `README.md`
- **API docs**: OpenAPI specs (`openapi.yaml`, `swagger.json`)
- **Runbooks**: files in `docs/runbooks/`, `docs/ops/`

## Phase 2: Analyze Code Structure
Map the actual code structure:
- List all services/packages (top-level directories with code)
- Identify API endpoints (route files, controllers)
- Read data models (schema files, model definitions)
- Check package.json / requirements.txt for key dependencies

## Phase 3: Detect Drift
Compare docs against code:
- **Service exists in code but not in docs** → missing documentation
- **Service in docs but not in code** → stale/removed reference
- **API endpoints in code not in OpenAPI spec** → undocumented endpoints
- **Data model changed but doc not updated** → stale schema doc
- **Dependencies in package.json differ from what docs describe** → stale stack description

Report drift as:
```
[STALE] README.md line 45: references service "auth-v1" which no longer exists
[MISSING] No ADR for MongoDB → PostgreSQL migration found in commit history
[OUTDATED] docs/architecture.md describes Node 16 but package.json uses Node 20
```

## Phase 4: Update Stale Docs
For each stale reference:
- Update the incorrect information
- Add a `> Last updated: YYYY-MM-DD by architecture-docs-agent` note
- Preserve the original intent; only change what's factually wrong

## Phase 5: Create Missing ADRs
If `--create-adrs` flag is set, for each significant undocumented decision found in git history:
- Search git log for commits mentioning architectural changes
- Write an ADR using the template in `.claude/memory/decisions.md`
- Mark status as "Accepted" with the approximate decision date

## Phase 6: Gap Report
If `--output-report` flag is set, generate `docs/architecture-gap-report.md`:
```markdown
# Architecture Documentation Gap Report
**Generated**: YYYY-MM-DD

## Coverage Summary
- Services documented: 8/10 (80%)
- API endpoints documented: 45/52 (87%)
- ADRs for major decisions: 3/7 (43%)

## Missing Documentation
[table of gaps with severity]

## Stale Documentation
[table of stale docs with drift description]

## Recommendations
[prioritized list of doc work]
```

## Error Handling
- No docs found: create a starter `docs/architecture.md` from project-state.md
- Cannot determine if doc is stale: flag with `[NEEDS REVIEW]` and explain
