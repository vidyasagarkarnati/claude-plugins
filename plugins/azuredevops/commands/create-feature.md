---
description: "Create an Azure DevOps Feature with child User Stories and Tasks in one command (Corestack mandatory fields enforced)"
argument-hint: "--title <title> --description <text> [--assigned-to <email>] [--area-path <path>] [--bundle <value>] [--stories \"<s1>, <s2>\"] [--acceptance-criteria \"<ac>\"] [--tasks \"<t1>, <t2>\"] [--iteration <path>] [--project <name>]"
---

# Create Feature

Create a Feature work item in Azure DevOps with all Corestack mandatory fields, then create child User Stories and Tasks — all in a single command.

All Corestack mandatory fields are enforced. Missing required values will be prompted interactively before creation begins.

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
| `--title` | Required | Feature title |
| `--description` | Required | Feature description |
| `--assigned-to` | Optional | Assignee email; prompted if omitted |
| `--area-path` | Optional | ADO area path; prompted if omitted |
| `--iteration` | Optional | Iteration path; prompted if omitted |
| `--bundle` | Optional | Corestack Bundle value; prompted if omitted |
| `--stories` | Optional | Comma-separated User Story titles |
| `--acceptance-criteria` | Optional | Acceptance criteria applied to all child stories |
| `--tasks` | Optional | Comma-separated Task titles (created under each story) |
| `--estimate` | Optional | Task estimate in hours (default: 8) |
| `--project` | Optional | ADO project name (overrides env var) |

## Step 1: Parse Arguments

Extract all flags from `$ARGUMENTS`.

## Step 2: Run the script

```bash
python3 scripts/ado_create_feature.py \
  --title "$TITLE" \
  --description "$DESCRIPTION" \
  [--assigned-to "$ASSIGNED_TO"] \
  [--area-path "$AREA_PATH"] \
  [--iteration "$ITERATION"] \
  [--bundle "$BUNDLE"] \
  [--stories "$STORIES"] \
  [--acceptance-criteria "$AC"] \
  [--tasks "$TASKS"] \
  [--estimate "$ESTIMATE"] \
  [--project "$PROJECT"]
```

The script prompts for any missing mandatory fields (`assigned-to`, `area-path`, `iteration`, `bundle`) before making any API calls.

## Output Format

```
Feature #$FEATURE_ID: $FEATURE_TITLE
  User Story #$S1_ID: $STORY_1
    Task #$T1_ID: $TASK_1 [8h]
    Task #$T2_ID: $TASK_2 [8h]
  User Story #$S2_ID: $STORY_2
    Task #$T1_ID: $TASK_1 [8h]

Total: 1 Feature | $N User Stories | $M Tasks
Feature URL: https://dev.azure.com/{org}/{project}/_workitems/edit/$FEATURE_ID
```

## Error Handling

- Missing `--title` or `--description`: argparse exits with usage message
- Missing Corestack fields: script prompts interactively
- User Story creation fails: logs error, continues with remaining stories
- Task creation fails: logs error, continues

## Usage Examples

```
/azuredevops:create-feature --title "User Authentication" --description "Implement full auth flow" --assigned-to "dev@company.com" --area-path "MyProject\TeamA" --bundle "Q1-Release" --iteration "MyProject\Sprint 5"

/azuredevops:create-feature --title "User Authentication" --description "Implement full auth flow" --stories "Login, Signup, Forgot Password" --acceptance-criteria "User can log in with email and password"

/azuredevops:create-feature --title "User Authentication" --description "Implement full auth flow" --stories "Login, Signup" --tasks "Design, Implement, Write Tests"
```
