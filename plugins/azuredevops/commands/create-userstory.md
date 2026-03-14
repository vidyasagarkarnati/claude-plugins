---
description: "Create an Azure DevOps User Story linked to a required parent Feature (Corestack mandatory fields enforced)"
argument-hint: "<title> --parent <feature-id> --assigned-to <email> --area-path <path> --bundle <value> --acceptance-criteria \"<ac>\" [--description <text>] [--iteration <path>] [--project <name>]"
---

# Create User Story

Create a new User Story work item in Azure DevOps with all Corestack mandatory fields. A parent Feature is **required** — User Stories must not exist without a parent Feature.

## Pre-flight Checks
1. Confirm `az devops` extension is installed: `az extension list --query "[?name=='azure-devops']"`
2. Check defaults are set: `az devops configure --list`
3. If `--iteration` not provided, list available iterations and ask which to use:
   ```bash
   az boards iteration project list --output table
   ```

## Phase 1: Parse Arguments
Extract from `$ARGUMENTS`:
- `TITLE` — **required**, the story title (everything before the first flag)
- `--parent` — **required**, parent Feature work item ID (no orphan User Stories allowed)
- `--assigned-to` — **required**, email/display name of assignee
- `--area-path` — **required** (e.g., `MyProject\TeamA`)
- `--bundle` — **required** (Corestack custom field value)
- `--acceptance-criteria` — **required**, acceptance criteria for the story
- `--description` — **required**, story description
- `--iteration` — **required**, iteration path (e.g., `MyProject\Sprint 5`)
- `--project` — optional, overrides default project

## Phase 2: Validate Mandatory Fields
Before running any `az` command, verify all required fields are present:
- `TITLE` — error if empty
- `PARENT` — **required**; if missing, query open Features and ask user to pick one:
  ```bash
  az boards query --wiql "SELECT [System.Id],[System.Title] FROM WorkItems WHERE [System.WorkItemType]='Feature' AND [System.State]<>'Closed'" --output table
  ```
  Do not create the User Story without a parent Feature.
- `ASSIGNED_TO` — error if empty
- `AREA_PATH` — error if empty
- `BUNDLE` — error if empty
- `ACCEPTANCE_CRITERIA` — error if empty
- `DESCRIPTION` — error if empty
- `ITERATION` — error if empty and no default set

If any required field is missing, print:
```
ERROR: Missing required field(s): <field list>
Usage: /azuredevops:create-userstory "<title>" --parent <feature-id> --assigned-to <email> --area-path <path> --bundle <value> --acceptance-criteria "<ac>" --description "<text>" --iteration <path>
```
Then stop.

## Phase 3: Create the User Story
```bash
az boards work-item create \
  --type "User Story" \
  --title "$TITLE" \
  --assigned-to "$ASSIGNED_TO" \
  --description "$DESCRIPTION" \
  --iteration "$ITERATION" \
  --fields "System.AreaPath=$AREA_PATH" \
           "Microsoft.VSTS.Common.AcceptanceCriteria=$ACCEPTANCE_CRITERIA" \
           "Custom.Bundle=$BUNDLE" \
  [--project "$PROJECT"] \
  --output json
```
Capture the returned `id` as `$STORY_ID`.

## Phase 4: Link to Parent Feature (always required)
```bash
az boards work-item relation add \
  --id $STORY_ID \
  --relation-type parent \
  --target-id $PARENT_ID \
  --output json
```
Confirm the relation was added successfully. If this step fails, warn the user and provide the manual command to re-link.

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
- Missing mandatory fields: fail early with usage message before creating anything
- Missing title: show usage and exit
- `--parent` not provided: query open Features, display list, ask user to choose — do not create without parent
- Invalid iteration path: run `az boards iteration project list` and show options
- Parent Feature ID not found: show error and stop — do not create orphan User Story
- Auth failure: remind user to run `az login` or set `AZURE_DEVOPS_EXT_PAT`

## Usage Examples
```
/azuredevops:create-userstory "Add login page" --parent 42 --assigned-to "dev@company.com" --area-path "MyProject\TeamA" --bundle "Q1-Release" --acceptance-criteria "User can log in with valid credentials" --description "As a user, I want to log in so I can access my account" --iteration "MyProject\Sprint 5"

/azuredevops:create-userstory "User profile settings" --parent 10 --assigned-to "dev@company.com" --area-path "MyProject\TeamB" --bundle "Q2-Release" --acceptance-criteria "User can update name, email, and avatar" --description "Profile settings page with CRUD operations" --iteration "MyProject\Sprint 6"
```
