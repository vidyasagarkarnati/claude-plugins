---
description: "Show current Azure DevOps sprint status: burndown, completion %, blockers, and health"
argument-hint: "[--sprint <iteration-path>] [--team <name>] [--project <name>]"
---

# Sprint Status

Fetch all work items in a sprint and produce a burndown summary: items by state, completion percentage, blocker flags, and overall sprint health.

## Prerequisites

```bash
pip install azure-devops
export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-org"
export AZURE_PERSONAL_ACCESS_TOKEN="your-pat"
export AZURE_DEVOPS_PROJECT="YourProject"   # optional if --project is passed
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--sprint` | Optional | Iteration path; auto-resolves current sprint if omitted |
| `--team` | Optional | Team name (used for sprint auto-resolution) |
| `--project` | Optional | ADO project name (overrides env var) |

## Step 1: Parse Arguments

Extract `--sprint`, `--team`, `--project` from `$ARGUMENTS`.

## Step 2: Run the script

```bash
python3 scripts/ado_sprint_status.py \
  [--sprint "$SPRINT"] \
  [--team "$TEAM"] \
  [--project "$PROJECT"]
```

If `--sprint` is omitted, the script calls the ADO API to find the current active sprint for the team.

## Output Format

```
Sprint Status — $SPRINT_NAME
$SPRINT_START → $SPRINT_END | $DAYS_REMAINING days remaining

Progress
  By Count:        [$DONE/$TOTAL] $COMPLETION_PCT%  ████████░░░
  By Story Points: [$DONE_PTS/$TOTAL_PTS pts] $PTS_PCT%  ███████░░░░

Work Item Breakdown
Type            New      Active   Resolved   Closed   Total
----------------------------------------------------------------
User Story        2           4          1        3      10
Task              5           8          2        6      21
Bug               1           2          0        1       4

At-Risk / Blocked Items
#ID      Title                                    Assignee                  Days Stale Flag
----------------------------------------------------------------------------------------------------
#1234    Implement OAuth flow                     alice@co.com                  4 days STALE
#1267    Design review for checkout               Unassigned                         — BLOCKED

Sprint Health: At Risk
(55% complete, 2 items at risk, 4 days left)
```

Health thresholds:
- **Healthy**: completion% ≥ expected burn rate AND at-risk items ≤ 2
- **At Risk**: completion% < expected burn rate OR at-risk items 3–5
- **Critical**: completion% significantly behind OR at-risk items > 5

## Error Handling

- Sprint not found: use `--sprint` to specify the iteration path explicitly
- No story points set: count-based completion shown only
- Empty sprint: confirm sprint path is correct

## Usage Examples

```
/azuredevops:sprint-status
/azuredevops:sprint-status --team "Backend Team"
/azuredevops:sprint-status --sprint "MyProject\Sprint 5" --team "Backend Team"
```
