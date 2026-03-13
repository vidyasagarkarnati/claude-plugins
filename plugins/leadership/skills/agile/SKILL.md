---
name: agile
description: Scrum ceremonies, sprint planning, story pointing with Fibonacci, DORA metrics, retrospective formats, and Definition of Done
---

# Agile

Mastery of this skill enables you to facilitate effective Scrum ceremonies, structure high-quality user stories, track team health using DORA metrics, and continuously improve team processes.

## When to Use This Skill
- Running sprint planning, retrospectives, or standups
- Writing or reviewing user stories and acceptance criteria
- Tracking team velocity and DORA metrics
- Improving team processes or resolving process dysfunction
- Estimating work with story points

## Core Concepts

### 1. Scrum Ceremonies
| Ceremony | Frequency | Duration (2-week sprint) | Purpose |
|----------|-----------|--------------------------|---------|
| Sprint Planning | Start of sprint | 4 hours | Commit to sprint goal + stories |
| Daily Standup | Daily | 15 minutes | Sync, surface blockers |
| Sprint Review | End of sprint | 2 hours | Demo to stakeholders |
| Retrospective | End of sprint | 1.5 hours | Improve the process |
| Backlog Refinement | Mid-sprint | 1 hour | Groom upcoming stories |

### 2. Story Structure
```
As a <persona>,
I want to <action/goal>,
So that <outcome/value>.

Acceptance Criteria (Given/When/Then):
Given [initial context]
When [action taken]
Then [observable outcome]
```

### 3. DORA Metrics (Team Health)
| Metric | Elite | High | Medium | Low |
|--------|-------|------|--------|-----|
| Deployment Frequency | Multiple/day | Weekly | Monthly | < Monthly |
| Lead Time for Changes | < 1 hour | 1 day-1 week | 1 week-1 month | > 1 month |
| Change Failure Rate | 0-5% | 5-10% | 10-15% | > 15% |
| Time to Restore | < 1 hour | < 1 day | 1 day-1 week | > 1 week |

## Quick Reference
```
Fibonacci scale: 1, 2, 3, 5, 8, 13, 21 (> 13 = must split)

Velocity = average story points completed per sprint (last 3 sprints)
Capacity = team_size × sprint_days × 0.7 (30% buffer for unplanned)

Sprint goal formula: "By the end of this sprint, [team] will [delivered value]
as demonstrated by [measurable outcome]."
```

## Key Patterns

### Pattern 1: Sprint Planning Agenda
```
1. Review Sprint Goal (5 min) — Product Owner presents
2. Backlog walkthrough (45 min) — PO explains top stories
3. Estimation (45 min) — team points stories
4. Capacity check (15 min) — compare points to capacity
5. Commitment (10 min) — team commits to sprint goal
```

### Pattern 2: Good vs Bad User Stories
```
BAD: "As a user, I want a dashboard so that I can see things."
GOOD: "As a premium subscriber, I want to see my monthly spending
      by category in a bar chart, so I can identify where I'm
      overspending and adjust my budget."

BAD AC: "The feature should work correctly."
GOOD AC:
  Given I am logged in as a premium subscriber
  When I navigate to the Dashboard
  Then I see a bar chart showing my last 30 days of spending
  And each bar is labeled with a category name
  And I can hover over a bar to see the exact amount
```

### Pattern 3: Retrospective (Start/Stop/Continue)
```
Timebox: 5 min per section

START doing:
- [team adds sticky notes]
- Automated integration tests before PR merge
- Weekly architecture sync

STOP doing:
- Skipping retros when we're busy
- Merging without code review

CONTINUE doing:
- Pair programming on complex features
- Daily standups at 9am
```

### Pattern 4: Definition of Done
```markdown
## Definition of Done (DoD)

A story is Done when ALL of the following are true:
- [ ] Code written and peer-reviewed (2 reviewers)
- [ ] Unit tests written, all tests passing
- [ ] Test coverage ≥ 80% on changed files
- [ ] Security review done (if auth/data/API changes)
- [ ] Documentation updated (API docs, README, ADR if needed)
- [ ] Feature flag configured (if applicable)
- [ ] Deployed to staging and smoke-tested
- [ ] Product Owner has accepted the story
- [ ] No known bugs introduced
```

## Best Practices
1. Sprint goal first — never plan a sprint without a clear goal
2. Stories ready when planned — if a story needs design or AC, it's not ready
3. Protect the retrospective — don't skip it when under pressure; that's when you need it most
4. Velocity is a planning tool, not a performance metric — never use it to compare teams
5. Fix Definition of Done violations immediately — technical debt compounds
6. Keep standups short and async if the team prefers — the goal is blocker visibility
7. DORA metrics improve when you reduce batch sizes and increase deploy frequency

## Common Issues
- **Team consistently over-commits**: use 70% capacity rule strictly for 2 sprints to recalibrate
- **No story points consensus**: use Planning Poker; resolve divergence by having extremes explain their reasoning
- **Retrospectives feel pointless**: pick ONE action item per retro, assign an owner, review it next retro
- **Velocity wildly variable**: check for unplanned work, unclear stories, or lack of DoD compliance
