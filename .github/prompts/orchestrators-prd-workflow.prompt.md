---
mode: agent
description: "Full PRD workflow: PM gathers requirements, Tech Architect reviews feasibility, Scrum Master creates sprint plan"
# argument-hint: <feature-description>
---


# PRD Workflow

Full product requirements workflow. Chains Product Manager → Technical Architect → Scrum Master to produce a complete PRD with feasibility assessment and initial sprint plan.

## Chain

```
use_agent: product-manager
```
**Input**: `${input:arguments}` (feature description)
**Task**: Run `/create-prd ${input:arguments}` — produce a complete PRD saved to `docs/prd-<feature>.md`
**Handoff artifact**: path to PRD file + summary of key requirements and success metrics

---

```
use_agent: technical-architect
```
**Input**: PRD from previous step
**Task**: Review PRD for technical feasibility:
- Identify technical risks or blockers
- Estimate implementation complexity (S/M/L/XL)
- Flag any requirements that need architecture decisions
- Run `/create-tdd <feature> --prd <prd-path>` to produce a Technical Design Document
**Handoff artifact**: TDD path + list of open technical questions + feasibility assessment

---

```
use_agent: scrum-master
```
**Input**: PRD + TDD from previous steps
**Task**: Create initial sprint breakdown:
- Break TDD implementation plan into sprint-sized stories
- Estimate story points for each
- Propose sprint goal for MVP delivery
- Update `.claude/memory/sprint-context.md` with new stories
**Output**: Sprint plan printed to console + updated sprint context

## Output
By end of this workflow you will have:
1. `docs/prd-<feature>.md` — Product Requirements Document
2. `docs/tdd-<feature>.md` — Technical Design Document
3. Updated `.claude/memory/sprint-context.md` — Sprint stories

## Usage
```
/orchestrators:prd-workflow "user authentication with OAuth2 and MFA support"
```
