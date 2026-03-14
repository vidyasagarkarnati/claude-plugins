---
description: "Show team capacity vs workload for the current or specified Azure DevOps sprint"
argument-hint: "[--sprint <iteration-path>] [--team <name>] [--project <name>] [--hours-per-day <n>]"
---

# Capacity Plan

Fetch all active work items in a sprint, group by assignee, and compare remaining work against available sprint capacity. Highlights over/under-allocated team members.

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
| `--hours-per-day` | Optional | Working hours per day (default: 6) |

## Step 1: Parse Arguments

Extract all flags from `$ARGUMENTS`.

## Step 2: Run the script

```bash
python3 scripts/ado_capacity_plan.py \
  [--sprint "$SPRINT"] \
  [--team "$TEAM"] \
  [--project "$PROJECT"] \
  [--hours-per-day "$HOURS"]
```

If `--sprint` is omitted, the script auto-resolves the current sprint.

## Output Format

```
Sprint Capacity Plan — $SPRINT_NAME
Sprint End: $FINISH_DATE | Days Remaining: $SPRINT_DAYS_REMAINING | Hours/Day: $HOURS_PER_DAY

Assignee                  Active Items   Remaining Hrs   Available Hrs   Utilization   Status
---------------------------------------------------------------------------------------------------
alice@company.com                    4            28h             24h          117%   OVER-ALLOCATED
bob@company.com                      2            16h             24h           67%   Under-allocated
carol@company.com                    3            22h             24h           92%   Fully Loaded
Unassigned                           2              —               —             —   NEEDS ASSIGNMENT

Team Total: $TOTAL_ITEMS items | $TOTAL_REMAINING_HRS hrs remaining

Recommendations:
- Reduce load for alice@company.com (28h remaining vs 24h available)
- Assign 2 unassigned items before sprint end
```

Utilization thresholds:
- **> 110%**: OVER-ALLOCATED
- **90–110%**: Fully Loaded
- **60–90%**: On Track
- **< 60%**: Under-allocated

## Error Handling

- Sprint not found: use `--sprint` to specify explicitly
- No `RemainingWork` on items: count-based view only
- Team not found: omit `--team` to query whole project

## Usage Examples

```
/azuredevops:capacity-plan
/azuredevops:capacity-plan --team "Backend Team"
/azuredevops:capacity-plan --sprint "MyProject\Sprint 5" --team "Backend Team" --hours-per-day 7
```
