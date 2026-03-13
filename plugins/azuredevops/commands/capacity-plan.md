---
description: "Show team capacity vs workload for the current or specified Azure DevOps sprint"
argument-hint: "[--sprint <iteration-path>] [--team <name>] [--project <name>] [--hours-per-day <n>]"
---

# Capacity Plan

Fetch all work items in a sprint, group by assignee, and compare remaining work against available sprint capacity. Highlights over/under-allocated team members.

## Pre-flight Checks
1. Check defaults: `az devops configure --list`
2. If `--team` not provided, ask the user for the team name or use the default team

## Phase 1: Parse Arguments
- `--sprint` — iteration path (e.g., `MyProject\Sprint 5`); if omitted, use current sprint
- `--team` — team name; required if no default
- `--project` — optional project override
- `--hours-per-day` — working hours per day (default: 6, accounting for meetings/overhead)

## Phase 2: Resolve Current Sprint (if --sprint not provided)
```bash
az boards iteration team list \
  --team "$TEAM" \
  --timeframe Current \
  --output json
```
Extract the current iteration `id`, `name`, `startDate`, and `finishDate`.
Calculate `$SPRINT_DAYS_REMAINING` = working days from today to `finishDate`.

## Phase 3: Get Sprint Work Items
```bash
az boards iteration team list-work-items \
  --id $ITERATION_ID \
  --team "$TEAM" \
  [--project "$PROJECT"] \
  --output json
```

For each work item ID returned, fetch remaining work:
```bash
az boards work-item show --id $ID \
  --fields "System.AssignedTo,System.Title,System.State,System.WorkItemType,Microsoft.VSTS.Scheduling.RemainingWork,Microsoft.VSTS.Scheduling.StoryPoints" \
  --output json
```

## Phase 4: Calculate Capacity
For each team member:
- `$TOTAL_REMAINING` = sum of `RemainingWork` hours across all their active items
- `$AVAILABLE_HOURS` = `$SPRINT_DAYS_REMAINING` × `$HOURS_PER_DAY`
- `$UTILIZATION` = ($TOTAL_REMAINING / $AVAILABLE_HOURS) × 100%
- Status:
  - > 110%: OVER-ALLOCATED
  - 90–110%: Fully Loaded
  - 60–90%: On Track
  - < 60%: UNDER-ALLOCATED

## Output Format
```
Sprint Capacity Plan — $SPRINT_NAME
Sprint End: $FINISH_DATE | Days Remaining: $SPRINT_DAYS_REMAINING | Hours/Day: $HOURS_PER_DAY

| Assignee          | Active Items | Remaining Hrs | Available Hrs | Utilization | Status           |
|-------------------|-------------|---------------|---------------|-------------|------------------|
| alice@company.com | 4           | 28h           | 24h           | 117%        | OVER-ALLOCATED   |
| bob@company.com   | 2           | 16h           | 24h           | 67%         | Under-allocated  |
| carol@company.com | 3           | 22h           | 24h           | 92%         | Fully Loaded     |
| Unassigned        | 2           | —             | —             | —           | NEEDS ASSIGNMENT |

Team Total: $TOTAL_ITEMS items | $TOTAL_REMAINING_HRS hrs remaining

Recommendations:
- Move 1-2 items from alice@ to bob@ to balance load
- Assign 2 unassigned items before sprint end
```

## Error Handling
- No `RemainingWork` field on items: note that estimates are missing, show item count only
- Empty sprint: confirm sprint name/path is correct, list available sprints
- Team not found: list available teams with `az devops team list --output table`

## Usage Examples
```
/azuredevops:capacity-plan
/azuredevops:capacity-plan --team "Backend Team"
/azuredevops:capacity-plan --sprint "MyProject\Sprint 5" --team "Backend Team" --hours-per-day 7
```
