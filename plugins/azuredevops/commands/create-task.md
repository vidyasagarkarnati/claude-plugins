---
description: "Create an Azure DevOps Task under a required parent User Story (Corestack mandatory fields enforced)"
argument-hint: "<title> --parent <story-id> --assigned-to <email> --area-path <path> --iteration <path> [--description <text>] [--estimate <hours>] [--project <name>]"
---

# Create Task

Create a new Task work item in Azure DevOps with all Corestack mandatory fields. A parent User Story is **required** — Tasks must not exist without a parent User Story.

Original Estimate defaults to **8 hours** if not provided. Remaining Work is always set equal to Original Estimate at creation.

## Pre-flight Checks
1. Confirm `az devops` extension is installed: `az extension list --query "[?name=='azure-devops']"`
2. Check defaults are set: `az devops configure --list`
3. If `--iteration` not provided, list available iterations:
   ```bash
   az boards iteration project list --output table
   ```

## Phase 1: Parse Arguments
Extract from `$ARGUMENTS`:
- `TITLE` — **required**, the task title (everything before the first flag)
- `--parent` — **required**, parent User Story work item ID (no orphan Tasks allowed)
- `--assigned-to` — **required**, email/display name of assignee
- `--area-path` — **required** (e.g., `MyProject\TeamA`)
- `--iteration` — **required**, iteration path (e.g., `MyProject\Sprint 5`)
- `--description` — **required**, task description
- `--estimate` — optional, original estimate in hours; **defaults to 8 if not provided**
- `--project` — optional, overrides default project

Set: `ESTIMATE=${estimate:-8}` and `REMAINING_WORK=$ESTIMATE`

## Phase 2: Validate Mandatory Fields
Before running any `az` command, verify all required fields are present:
- `TITLE` — error if empty
- `PARENT` — **required**; if missing, query open User Stories and ask user to pick one:
  ```bash
  az boards query --wiql "SELECT [System.Id],[System.Title] FROM WorkItems WHERE [System.WorkItemType]='User Story' AND [System.State]<>'Closed'" --output table
  ```
  Do not create the Task without a parent User Story.
- `ASSIGNED_TO` — error if empty
- `AREA_PATH` — error if empty
- `DESCRIPTION` — error if empty
- `ITERATION` — error if empty and no default set

If any required field is missing, print:
```
ERROR: Missing required field(s): <field list>
Usage: /azuredevops:create-task "<title>" --parent <story-id> --assigned-to <email> --area-path <path> --iteration <path> --description "<text>" [--estimate <hours>]
```
Then stop.

## Phase 3: Create the Task
```bash
az boards work-item create \
  --type "Task" \
  --title "$TITLE" \
  --assigned-to "$ASSIGNED_TO" \
  --description "$DESCRIPTION" \
  --iteration "$ITERATION" \
  --fields "System.AreaPath=$AREA_PATH" \
           "Microsoft.VSTS.Scheduling.OriginalEstimate=$ESTIMATE" \
           "Microsoft.VSTS.Scheduling.RemainingWork=$REMAINING_WORK" \
  [--project "$PROJECT"] \
  --output json
```
Capture the returned `id` as `$TASK_ID`.

## Phase 4: Link to Parent User Story (always required)
```bash
az boards work-item relation add \
  --id $TASK_ID \
  --relation-type parent \
  --target-id $PARENT_ID \
  --output json
```
Confirm the relation was added successfully. If this step fails, warn the user and provide the manual command to re-link.

## Output Format
```
Task Created

  ID:                #$TASK_ID
  Title:             $TITLE
  Assigned:          $ASSIGNED_TO
  Area Path:         $AREA_PATH
  Iteration:         $ITERATION
  Original Estimate: ${ESTIMATE}h
  Remaining Work:    ${REMAINING_WORK}h
  Parent Story:      #$PARENT_ID
  URL:               https://dev.azure.com/{org}/{project}/_workitems/edit/$TASK_ID
```

## Error Handling
- Missing mandatory fields: fail early with usage message before creating anything
- `--parent` not provided: query open User Stories, display list, ask user to choose — do not create without parent
- Invalid iteration path: run `az boards iteration project list` and show options
- Parent User Story ID not found: show error and stop — do not create orphan Task
- Auth failure: remind user to run `az login` or set `AZURE_DEVOPS_EXT_PAT`

## Usage Examples
```
/azuredevops:create-task "Implement login API" --parent 55 --assigned-to "dev@company.com" --area-path "MyProject\TeamA" --iteration "MyProject\Sprint 5" --description "Build POST /auth/login endpoint with JWT response"

/azuredevops:create-task "Write unit tests for login" --parent 55 --assigned-to "qa@company.com" --area-path "MyProject\TeamA" --iteration "MyProject\Sprint 5" --description "Unit tests covering valid/invalid credentials, token expiry" --estimate 4

/azuredevops:create-task "Design login UI mockup" --parent 56 --assigned-to "designer@company.com" --area-path "MyProject\TeamB" --iteration "MyProject\Sprint 5" --description "Figma mockup for login page responsive design" --estimate 6
```
