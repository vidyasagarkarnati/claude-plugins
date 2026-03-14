---
description: "Create an Azure DevOps Task under a required parent User Story (Corestack mandatory fields enforced)"
argument-hint: "--title <title> --description <text> [--parent <story-id>] [--assigned-to <email>] [--area-path <path>] [--iteration <path>] [--estimate <hours>] [--project <name>]"
---

# Create Task

Create a new Task work item in Azure DevOps with all Corestack mandatory fields. A parent User Story is **required** — Tasks must not exist without a parent User Story. If `--parent` is not provided, the script queries open User Stories and prompts you to select one.

Original Estimate defaults to **8 hours** if not provided. Remaining Work is always set equal to Original Estimate at creation.

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
| `--title` | Required | Task title |
| `--description` | Required | Task description |
| `--parent` | Optional | Parent User Story ID; script lists open stories if omitted |
| `--assigned-to` | Optional | Assignee email; prompted if omitted |
| `--area-path` | Optional | ADO area path; prompted if omitted |
| `--iteration` | Optional | Iteration path; prompted if omitted |
| `--estimate` | Optional | Original estimate in hours (default: 8) |
| `--project` | Optional | ADO project name (overrides env var) |

## Step 1: Parse Arguments

Extract all flags from `$ARGUMENTS`.

## Step 2: Run the script

```bash
python3 scripts/ado_create_task.py \
  --title "$TITLE" \
  --description "$DESCRIPTION" \
  [--parent "$PARENT_ID"] \
  [--assigned-to "$ASSIGNED_TO"] \
  [--area-path "$AREA_PATH"] \
  [--iteration "$ITERATION"] \
  [--estimate "$ESTIMATE"] \
  [--project "$PROJECT"]
```

If `--parent` is omitted, the script fetches the 20 most recent open User Stories and asks you to enter an ID. Mandatory fields (`assigned-to`, `area-path`, `iteration`) are prompted interactively if not provided.

## Output Format

```
Task Created

  ID:                #$TASK_ID
  Title:             $TITLE
  Assigned:          $ASSIGNED_TO
  Area Path:         $AREA_PATH
  Iteration:         $ITERATION
  Original Estimate: ${ESTIMATE}h
  Remaining Work:    ${ESTIMATE}h
  Parent Story:      #$PARENT_ID
  URL:               https://dev.azure.com/{org}/{project}/_workitems/edit/$TASK_ID
```

## Error Handling

- Missing `--title` or `--description`: argparse exits with usage message
- `--parent` not provided: queries open User Stories interactively — does not create without parent
- Missing mandatory fields: prompted interactively

## Usage Examples

```
/azuredevops:create-task --title "Implement login API" --parent 55 --assigned-to "dev@company.com" --area-path "MyProject\TeamA" --iteration "MyProject\Sprint 5" --description "Build POST /auth/login endpoint with JWT response"

/azuredevops:create-task --title "Write unit tests for login" --description "Unit tests covering valid/invalid credentials" --estimate 4

/azuredevops:create-task --title "Design login UI mockup" --parent 56 --description "Figma mockup for login page" --estimate 6
```
