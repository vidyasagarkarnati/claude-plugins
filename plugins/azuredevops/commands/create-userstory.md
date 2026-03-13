---
description: "Create an Azure DevOps User Story, optionally linked to a parent Feature"
argument-hint: "<title> [--project <name>] [--iteration <path>] [--parent <feature-id>] [--assigned-to <email>] [--description <text>]"
---

# Create User Story

Create a new User Story work item in Azure DevOps. Optionally link it to an existing Feature as a child.

## Pre-flight Checks
1. Confirm `az devops` extension is installed: `az extension list --query "[?name=='azure-devops']"`
2. Check defaults are set: `az devops configure --list`
3. If `--project` not provided and no default set, ask the user for the project name
4. If `--iteration` not provided, list available iterations and ask which to use:
   ```bash
   az boards iteration project list --output table
   ```

## Phase 1: Parse Arguments
Extract from `$ARGUMENTS`:
- `TITLE` — required, the story title (everything before the first flag)
- `--project` — optional, overrides default project
- `--iteration` — optional, iteration path (e.g., `MyProject\Sprint 5`)
- `--parent` — optional, parent Feature work item ID
- `--assigned-to` — optional, email/display name of assignee
- `--description` — optional, story description / acceptance criteria

## Phase 2: Create the User Story
```bash
az boards work-item create \
  --type "User Story" \
  --title "$TITLE" \
  [--iteration "$ITERATION"] \
  [--assigned-to "$ASSIGNED_TO"] \
  [--description "$DESCRIPTION"] \
  [--project "$PROJECT"] \
  --output json
```
Capture the returned `id` as `$STORY_ID`.

## Phase 3: Link to Parent Feature (if --parent provided)
```bash
az boards work-item relation add \
  --id $STORY_ID \
  --relation-type parent \
  --target-id $PARENT_ID \
  --output json
```
Confirm the relation was added successfully.

## Output Format
```
User Story Created

  ID:        #$STORY_ID
  Title:     $TITLE
  Iteration: $ITERATION
  Assigned:  $ASSIGNED_TO (or Unassigned)
  Parent:    Feature #$PARENT_ID (or None)
  URL:       https://dev.azure.com/{org}/{project}/_workitems/edit/$STORY_ID
```

## Error Handling
- Missing title: show usage and exit
- Invalid iteration path: run `az boards iteration project list` and show options
- Parent ID not found: show error, create story without parent and note it
- Auth failure: remind user to run `az login` or set `AZURE_DEVOPS_EXT_PAT`

## Usage Examples
```
/azuredevops:create-userstory "Add login page"
/azuredevops:create-userstory "Add login page" --iteration "MyProject\Sprint 5" --parent 42
/azuredevops:create-userstory "Add login page" --assigned-to "dev@company.com" --description "As a user, I want to log in so I can access my account"
```
