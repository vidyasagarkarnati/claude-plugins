---
description: "Generate a weekly Azure DevOps progress report ready to send as email or Teams message"
argument-hint: "[--project <name>] [--sprint <iteration-path>] [--team <name>] [--week-start <YYYY-MM-DD>]"
---

# Weekly Status Report

Aggregate Azure DevOps work item activity for the past week and generate a formatted status email covering: completed work, in-progress items, blockers, and next week's focus.

## Pre-flight Checks
1. Check defaults: `az devops configure --list`
2. Calculate `$WEEK_START` — if not provided, use last Monday's date
3. Calculate `$WEEK_END` — today's date

## Phase 1: Parse Arguments
- `--project` — optional project override
- `--sprint` — iteration path; if omitted, use current sprint
- `--team` — team name
- `--week-start` — YYYY-MM-DD; default: most recent Monday

## Phase 2: Resolve Current Sprint (if needed)
```bash
az boards iteration team list \
  --team "$TEAM" \
  --timeframe Current \
  --output json
```

## Phase 3: Run WIQL Queries

**Completed this week** (state changed to Closed/Resolved between week-start and today):
```bash
az boards query --wiql "
  SELECT [System.Id], [System.Title], [System.WorkItemType], [System.AssignedTo],
         [Microsoft.VSTS.Scheduling.StoryPoints], [Microsoft.VSTS.Common.ClosedDate]
  FROM WorkItems
  WHERE [System.IterationPath] UNDER '$SPRINT_PATH'
    AND [System.State] IN ('Closed', 'Resolved')
    AND [Microsoft.VSTS.Common.ClosedDate] >= '$WEEK_START'
  ORDER BY [Microsoft.VSTS.Common.ClosedDate] DESC
" --output json
```

**In Progress** (currently Active):
```bash
az boards query --wiql "
  SELECT [System.Id], [System.Title], [System.WorkItemType], [System.AssignedTo],
         [Microsoft.VSTS.Scheduling.StoryPoints], [System.ChangedDate]
  FROM WorkItems
  WHERE [System.IterationPath] UNDER '$SPRINT_PATH'
    AND [System.State] = 'Active'
  ORDER BY [System.AssignedTo]
" --output json
```

**Blocked / At-Risk** (Active AND not changed in 3+ days, OR tagged blocked):
```bash
az boards query --wiql "
  SELECT [System.Id], [System.Title], [System.AssignedTo], [System.ChangedDate], [System.Tags]
  FROM WorkItems
  WHERE [System.IterationPath] UNDER '$SPRINT_PATH'
    AND [System.State] = 'Active'
    AND (
      [System.ChangedDate] <= '$THREE_DAYS_AGO'
      OR [System.Tags] CONTAINS 'blocked'
    )
" --output json
```

**Upcoming** (New, not yet started):
```bash
az boards query --wiql "
  SELECT [System.Id], [System.Title], [System.WorkItemType], [System.AssignedTo],
         [Microsoft.VSTS.Scheduling.StoryPoints]
  FROM WorkItems
  WHERE [System.IterationPath] UNDER '$SPRINT_PATH'
    AND [System.State] = 'New'
  ORDER BY [System.AssignedTo]
" --output json
```

## Phase 4: Compose the Report

Calculate sprint completion %:
- `$COMPLETED_COUNT` + `$TOTAL_COUNT`
- `$COMPLETED_PTS` + `$TOTAL_PTS` (if story points exist)

## Output Format (email-ready Markdown)

```
Subject: Weekly Engineering Status — $SPRINT_NAME | Week of $WEEK_START

---

## Engineering Status Update
**Sprint:** $SPRINT_NAME ($SPRINT_START → $SPRINT_END)
**Week:** $WEEK_START – $WEEK_END
**Sprint Progress:** $COMPLETION_PCT% complete ($COMPLETED_PTS / $TOTAL_PTS pts)

---

### Completed This Week ($COMPLETED_COUNT items)
| # | Title | Type | Owner | Points |
|---|-------|------|-------|--------|
| #1234 | Implement login API | User Story | alice@ | 5 |
| #1235 | Add unit tests for auth | Task | bob@ | 2 |

---

### In Progress ($IN_PROGRESS_COUNT items)
| # | Title | Type | Owner | Last Updated |
|---|-------|------|-------|-------------|
| #1240 | Build checkout flow | User Story | carol@ | 2 days ago |
| #1241 | Database migration | Task | dave@ | 1 day ago |

---

### Blockers / At-Risk ($BLOCKED_COUNT items)
| # | Title | Owner | Stale | Action Needed |
|---|-------|-------|-------|---------------|
| #1256 | Payment gateway integration | alice@ | 5 days | Needs 3rd-party API key |
| #1267 | Design sign-off | Unassigned | — | Awaiting design review |

---

### Coming Up Next Week
| # | Title | Type | Owner |
|---|-------|------|-------|
| #1270 | Email notifications | User Story | bob@ |
| #1271 | Error logging setup | Task | carol@ |

---

### Summary
- $COMPLETED_COUNT items completed this week ($COMPLETED_PTS pts)
- $IN_PROGRESS_COUNT items in flight
- $BLOCKED_COUNT items need attention
- Sprint is **$HEALTH_STATUS** — on track to finish $SPRINT_END

---
*Generated from Azure DevOps | $PROJECT | $SPRINT_NAME*
```

## Error Handling
- No completed items this week: note "No items closed this week" — still show in-progress and blockers
- Missing story points: show count-based metrics only
- Week-start in the future: error and show correct date range

## Usage Examples
```
/azuredevops:weekly-status
/azuredevops:weekly-status --team "Backend Team"
/azuredevops:weekly-status --sprint "MyProject\Sprint 5" --week-start 2025-03-10
```
