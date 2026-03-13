---
description: "Show current Azure DevOps sprint status: burndown, completion %, blockers, and health"
argument-hint: "[--sprint <iteration-path>] [--team <name>] [--project <name>]"
---

# Sprint Status

Fetch all work items in a sprint and produce a burndown summary: items by state, completion percentage, blocker flags, and overall sprint health.

## Pre-flight Checks
1. Check defaults: `az devops configure --list`
2. If `--team` not provided, use default team or ask

## Phase 1: Parse Arguments
- `--sprint` — iteration path; if omitted, resolve current sprint automatically
- `--team` — team name
- `--project` — optional project override

## Phase 2: Resolve Sprint
If `--sprint` not provided:
```bash
az boards iteration team list \
  --team "$TEAM" \
  --timeframe Current \
  --output json
```
Extract: `$SPRINT_NAME`, `$SPRINT_START`, `$SPRINT_END`, `$ITERATION_ID`.

## Phase 3: Query Sprint Work Items via WIQL
```bash
az boards query --wiql "
  SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo],
         [System.WorkItemType], [Microsoft.VSTS.Scheduling.StoryPoints],
         [System.ChangedDate], [System.Tags]
  FROM WorkItems
  WHERE [System.IterationPath] = '$SPRINT_PATH'
    AND [System.TeamProject] = '$PROJECT'
  ORDER BY [System.WorkItemType], [System.State]
" --output json
```

## Phase 4: Analyze Results

**Group by State:**
- New / Active / Resolved / Closed

**Group by Work Item Type:**
- Feature / User Story / Task / Bug

**Completion %:**
- By count: (Resolved + Closed) / Total × 100
- By story points: sum(Resolved + Closed story points) / sum(all story points) × 100

**Blocker Detection** — flag items as at-risk if:
- State is "Active" AND `ChangedDate` is > 3 days ago
- Tags contain "blocked" or "impediment"

**Days remaining:** working days from today to `$SPRINT_END`

## Output Format
```
Sprint Status — $SPRINT_NAME
$SPRINT_START → $SPRINT_END | $DAYS_REMAINING days remaining

Progress
  By Count:        [$DONE/$TOTAL] $COMPLETION_PCT%  ████████░░░
  By Story Points: [$DONE_PTS/$TOTAL_PTS pts] $PTS_PCT%  ███████░░░░

Work Item Breakdown
| Type        | New | Active | Resolved | Closed | Total |
|-------------|-----|--------|----------|--------|-------|
| User Story  |  2  |   4    |    1     |   3    |  10   |
| Task        |  5  |   8    |    2     |   6    |  21   |
| Bug         |  1  |   2    |    0     |   1    |   4   |

At-Risk / Blocked Items
| ID    | Title                        | Assignee     | Days Stale | Flag     |
|-------|------------------------------|--------------|------------|----------|
| #1234 | Implement OAuth flow         | alice@co.com | 4 days     | STALE    |
| #1256 | Fix DB connection pool       | bob@co.com   | 6 days     | STALE    |
| #1267 | Design review for checkout   | Unassigned   | —          | BLOCKED  |

Sprint Health: $HEALTH_EMOJI $HEALTH_STATUS
($COMPLETION_PCT% complete, $AT_RISK_COUNT items at risk, $DAYS_REMAINING days left)
```

Health thresholds:
- Healthy: completion% ≥ expected burn rate AND at-risk items ≤ 2
- At Risk: completion% < expected burn rate OR at-risk items 3–5
- Critical: completion% significantly behind OR at-risk items > 5

Expected burn rate = days elapsed / total sprint days × 100%

## Error Handling
- Sprint not found: list available sprints with `az boards iteration team list --output table`
- No story points set: show count-based completion only, note missing estimates
- Empty sprint: confirm sprint path, suggest checking `az boards iteration project list`

## Usage Examples
```
/azuredevops:sprint-status
/azuredevops:sprint-status --team "Backend Team"
/azuredevops:sprint-status --sprint "MyProject\Sprint 5" --team "Backend Team"
```
