---
description: "Generate a weekly Azure DevOps progress report ready to send as email or Teams message"
argument-hint: "[--project <name>] [--sprint <iteration-path>] [--team <name>] [--area-path <path>] [--week-start <YYYY-MM-DD>] [--milestone <name>] [--description <text>]"
---

# Weekly Status Report

Aggregate Azure DevOps work item activity for the past week and generate a formatted status email covering: completed work, in-progress items, blockers, and next week's focus.

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
| `--project` | Optional | ADO project name (overrides env var) |
| `--sprint` | Optional | Iteration path; auto-resolves current sprint if omitted |
| `--team` | Optional | Team name (used for sprint auto-resolution and board URL) |
| `--area-path` | Optional | ADO area path filter (e.g. `Product_Mgmt\Core`); filters all queries to that team's area |
| `--week-start` | Optional | YYYY-MM-DD; default: most recent Monday |
| `--milestone` | Optional | Milestone name for subject line |
| `--description` | Optional | Additional narrative appended after auto-generated executive summary |

## Step 1: Parse Arguments

Extract all flags from `$ARGUMENTS`. Default `--week-start` to last Monday if not provided.

## Step 2: Run the script

```bash
python3 scripts/ado_weekly_status.py \
  [--project "$PROJECT"] \
  [--sprint "$SPRINT"] \
  [--team "$TEAM"] \
  [--area-path "$AREA_PATH"] \
  [--week-start "$WEEK_START"] \
  [--milestone "$MILESTONE"] \
  [--description "$DESCRIPTION"]
```

The script runs 8 WIQL queries (completed, in-progress, blocked, upcoming, all items, scope creep, capacity, features) and outputs a leadership-ready Markdown email.

## Output Format (email-ready Markdown)

```
Subject: Weekly Engineering Status — $SPRINT_NAME | Week of $WEEK_START

---

## Engineering Status Update
**Sprint:** $SPRINT_NAME ($SPRINT_START → $SPRINT_END)
**Week:** $WEEK_START – $WEEK_END
**Sprint Progress:** $COMPLETION_PCT% complete ($COMPLETED_PTS / $TOTAL_PTS pts)

---

### Completed This Week ($N items)
| #      | Title                                         | Type         | Owner                | Points |
...

### In Progress ($N items)
| #      | Title                                         | Type         | Owner                | Last Updated    |
...

### Blockers / At-Risk ($N items)
| #      | Title                                         | Owner                | Stale      | Action Needed        |
...

### Coming Up Next Week ($N items)
| #      | Title                                         | Type         | Owner                |
...

### Summary
- $N items completed this week ($PTS pts)
- $N items in flight
- $N items need attention
- Sprint is **on track** — on track to finish $SPRINT_END
```

## Error Handling

- No completed items: shows "No items closed this week" — still shows in-progress and blockers
- Missing story points: count-based metrics only
- Sprint not found: falls back to querying the whole project iteration tree

## Usage Examples

```
/azuredevops:weekly-status
/azuredevops:weekly-status --team "Core" --area-path "Product_Mgmt\Core"
/azuredevops:weekly-status --sprint "Product_Mgmt\6.0\2601" --team "Core" --area-path "Product_Mgmt\Core" --milestone "Phase 1"
```
