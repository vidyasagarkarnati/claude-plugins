---
mode: agent
description: "Sprint planning and kick-off: Scrum Master runs ceremony, Engineering Manager assigns capacity, PM confirms priorities"
# argument-hint: [--sprint <name>] [--capacity <points>] [--duration <weeks>]
---


# Sprint Workflow

Complete sprint planning and kick-off ceremony. Scrum Master runs the ceremony, Engineering Manager assigns capacity and resolves conflicts, Product Manager confirms and finalizes priorities.

## Chain

```
use_agent: scrum-master
```
**Input**: `${input:arguments}` — sprint name, capacity, duration
**Task**: Sprint ceremony facilitation:
- Read `.claude/memory/sprint-context.md` for current state
- Review backlog for groomed, ready stories
- Calculate team velocity (average of last 3 sprints if available)
- Identify stories that are NOT ready (missing AC, blocked, needs splitting)
- Propose sprint goal based on highest-priority ready stories
- Create initial story list for the sprint
**Handoff artifact**: Proposed sprint goal + candidate story list + NOT-READY list

---

```
use_agent: engineering-manager
```
**Input**: Proposed sprint plan from Scrum Master
**Task**: Capacity planning and assignment:
- Map each story to an engineer based on domain knowledge and availability
- Account for: planned time off, on-call rotation, 20% buffer for unplanned work
- Check for team members over/under-allocated
- Flag stories that have external dependencies (other teams, design, legal)
- Confirm capacity vs commitment numbers
**Handoff artifact**: Assigned sprint board + capacity utilization breakdown + dependency flags

---

```
use_agent: product-manager
```
**Input**: Assigned sprint plan from Engineering Manager
**Task**: Priority confirmation and finalization:
- Confirm the sprint goal aligns with current product priorities
- If capacity requires descoping: make the priority call on which stories move out
- Add any missing context to stories (user impact, deadlines)
- Confirm acceptance criteria are testable
- Sign off on the sprint plan
**Output**: Final sprint plan written to `.claude/memory/sprint-context.md` + summary printed to console

## Output
```
## Sprint [Name] Plan

**Goal**: [one sentence]
**Dates**: [start] → [end]
**Capacity**: [N] pts

### Committed Stories
| Ticket | Title | Points | Assignee |
|--------|-------|--------|----------|
...

### Deferred to Next Sprint
| Ticket | Reason |
...

### Dependencies
| Story | Depends On | Owner | ETA |
...

Status: READY TO START ✅
```

## Usage
```
/orchestrators:sprint-workflow --sprint "Sprint 14" --capacity 40
```
