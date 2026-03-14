---
description: "Create an Azure DevOps User Story linked to a required parent Feature (Corestack mandatory fields enforced)"
argument-hint: "--title <title> --description <text> --acceptance-criteria \"<ac>\" [--parent <feature-id>] [--assigned-to <email>] [--area-path <path>] [--bundle <value>] [--iteration <path>] [--project <name>]"
---

# Create User Story

Create a new User Story work item in Azure DevOps with all Corestack mandatory fields. A parent Feature is **required** — User Stories must not exist without a parent Feature. If `--parent` is not provided, the script queries open Features and prompts you to select one.

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
| `--title` | Required | Story title |
| `--description` | Required | Story description |
| `--acceptance-criteria` | Required | Acceptance criteria (Given/When/Then) |
| `--parent` | Optional | Parent Feature ID; script lists open Features if omitted |
| `--assigned-to` | Optional | Assignee email; prompted if omitted |
| `--area-path` | Optional | ADO area path; prompted if omitted |
| `--iteration` | Optional | Iteration path; prompted if omitted |
| `--bundle` | Optional | Corestack Bundle value; prompted if omitted |
| `--project` | Optional | ADO project name (overrides env var) |

## Step 1: Parse Arguments

Extract all flags from `$ARGUMENTS`.

## Step 2: Run the script

```bash
python3 scripts/ado_create_userstory.py \
  --title "$TITLE" \
  --description "$DESCRIPTION" \
  --acceptance-criteria "$AC" \
  [--parent "$PARENT_ID"] \
  [--assigned-to "$ASSIGNED_TO"] \
  [--area-path "$AREA_PATH"] \
  [--iteration "$ITERATION"] \
  [--bundle "$BUNDLE"] \
  [--project "$PROJECT"]
```

If `--parent` is omitted, the script fetches the 20 most recent open Features and asks you to enter an ID. Corestack mandatory fields (`assigned-to`, `area-path`, `iteration`, `bundle`) are prompted interactively if not provided.

## Output Format

```
User Story Created

  ID:                  #$STORY_ID
  Title:               $TITLE
  Assigned:            $ASSIGNED_TO
  Area Path:           $AREA_PATH
  Iteration:           $ITERATION
  Bundle:              $BUNDLE
  Acceptance Criteria: $ACCEPTANCE_CRITERIA
  Parent Feature:      #$PARENT_ID
  URL:                 https://dev.azure.com/{org}/{project}/_workitems/edit/$STORY_ID
```

## Error Handling

- Missing `--title`, `--description`, or `--acceptance-criteria`: argparse exits with usage message
- `--parent` not provided: queries open Features interactively — does not create without parent
- Missing Corestack fields: prompted interactively

## Usage Examples

```
/azuredevops:create-userstory --title "Add login page" --parent 42 --assigned-to "dev@company.com" --area-path "MyProject\TeamA" --bundle "Q1-Release" --acceptance-criteria "User can log in with valid credentials" --description "As a user, I want to log in so I can access my account" --iteration "MyProject\Sprint 5"

/azuredevops:create-userstory --title "User profile settings" --description "Profile settings page" --acceptance-criteria "User can update name and email"
```
