---
description: "Run sprint planning: break down tickets, estimate, and assign capacity"
argument-hint: "[--sprint <name>] [--capacity <points>]"
---

# Sprint Planning

Facilitate a full sprint planning session: review and refine the backlog, estimate stories, check team capacity, and produce a sprint plan. Uses Scrum Master + Engineering Manager persona.

## Pre-flight Checks
1. Read `.claude/memory/sprint-context.md` for current sprint state and team capacity
2. Read `.claude/memory/project-state.md` for tech context
3. Note `--capacity` override if provided (default: read from sprint-context.md)

## Phase 1: Backlog Review
- List all stories/tickets in the backlog sorted by priority
- Flag stories that are NOT ready for sprint (missing AC, design, dependencies)
- Identify stories with blockers and note the blocker owner
- Confirm sprint goal with the team (ask if not provided in context)

## Phase 2: Story Refinement
For each story entering the sprint:
- Verify acceptance criteria are clear and testable
- Break down any story estimated > 8 points into sub-tasks
- Identify technical risks or unknowns that need spikes
- Note dependencies on other teams or external systems

## Phase 3: Estimation
Use Fibonacci scale: 1, 2, 3, 5, 8, 13 (anything >13 needs splitting)

| Story | Estimate | Rationale |
|-------|----------|-----------|
| [PROJ-xxx] | N pts | [brief rationale] |

Estimation guidelines:
- 1 pt: trivial change, < 2 hours
- 2 pts: simple, well-understood, < 4 hours
- 3 pts: straightforward, 1 day
- 5 pts: moderate complexity, 2-3 days
- 8 pts: complex, full week, consider splitting
- 13 pts: too big, must split

## Phase 4: Capacity Check
- Total team capacity = (team size × sprint days × 0.7) - time off - ceremonies
- Compare total estimated points vs capacity
- If over capacity: remove lowest-priority stories to a future sprint
- If under capacity: pull in next-priority backlog items

## Phase 5: Sprint Goal
Write a sprint goal: one sentence describing the value delivered this sprint.
Example: "Complete user authentication flow so engineers can test end-to-end login"

## Output Format
Update `.claude/memory/sprint-context.md` with:
- Sprint name, dates, goal
- Committed stories table
- Team capacity calculation
- Removed stories (with reason)
- Risks

Print summary to console.

## Error Handling
- No backlog provided: ask user to paste ticket titles or descriptions
- Incomplete acceptance criteria: flag tickets with `[NEEDS REFINEMENT]`
- Over-committed sprint: automatically suggest which stories to defer with rationale
