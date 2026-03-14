---
description: "Create an Azure DevOps Feature with child User Stories and Tasks in one command (Corestack mandatory fields enforced)"
argument-hint: "<feature-title> --assigned-to <email> --area-path <path> --bundle <value> [--description <text>] [--stories \"<s1>, <s2>\"] [--acceptance-criteria \"<ac>\"] [--tasks \"<t1>, <t2>\"] [--iteration <path>] [--project <name>]"
---

# Create Feature

Create a Feature work item in Azure DevOps with all Corestack mandatory fields, then create child User Stories and Tasks — all in a single command chain.

All Corestack mandatory fields are enforced. Missing required values will cause an early exit with a prompt to provide them.

## Pre-flight Checks
1. Confirm `az devops` extension is installed: `az extension list --query "[?name=='azure-devops']"`
2. Check defaults: `az devops configure --list`
3. If `--iteration` not provided, list available iterations:
   ```bash
   az boards iteration project list --output table
   ```

## Phase 1: Parse Arguments
Extract from `$ARGUMENTS`:
- `FEATURE_TITLE` — **required**
- `--assigned-to` — **required** (email or display name)
- `--area-path` — **required** (e.g., `MyProject\TeamA`)
- `--bundle` — **required** (Corestack custom field value)
- `--description` — **required** (feature description)
- `--stories` — comma-separated list of User Story titles (quoted string)
- `--acceptance-criteria` — acceptance criteria applied to all child User Stories (can be overridden per story)
- `--tasks` — comma-separated list of Task titles to create under EACH User Story
- `--iteration` — iteration path applied to Feature and all children
- `--project` — optional project override

## Phase 2: Validate Mandatory Fields
Before running any `az` command, verify all required fields are present:
- `FEATURE_TITLE` — error if empty
- `ASSIGNED_TO` — error if empty; do not create with Unassigned
- `AREA_PATH` — error if empty
- `BUNDLE` — error if empty
- `DESCRIPTION` — error if empty
- `ITERATION` — error if empty and no default set; run `az boards iteration project list` and ask user to pick one

If any required field is missing, print:
```
ERROR: Missing required field(s): <field list>
Usage: /azuredevops:create-feature "<title>" --assigned-to <email> --area-path <path> --bundle <value> --description "<text>" --iteration <path>
```
Then stop.

## Phase 3: Create the Feature
```bash
az boards work-item create \
  --type "Feature" \
  --title "$FEATURE_TITLE" \
  --assigned-to "$ASSIGNED_TO" \
  --description "$DESCRIPTION" \
  --iteration "$ITERATION" \
  --fields "System.AreaPath=$AREA_PATH" "Custom.Bundle=$BUNDLE" \
  [--project "$PROJECT"] \
  --output json
```
Capture returned `id` as `$FEATURE_ID`.

Print: `Feature #$FEATURE_ID created: $FEATURE_TITLE`

## Phase 4: Create User Stories (for each story in --stories)
If `--stories` not provided, stop after Phase 3.

For each `$STORY_TITLE` in the stories list, `ESTIMATE` defaults to `8` if not specified:

```bash
# Create User Story with all Corestack mandatory fields
az boards work-item create \
  --type "User Story" \
  --title "$STORY_TITLE" \
  --assigned-to "$ASSIGNED_TO" \
  --description "$STORY_TITLE" \
  --iteration "$ITERATION" \
  --fields "System.AreaPath=$AREA_PATH" \
           "Microsoft.VSTS.Common.AcceptanceCriteria=$ACCEPTANCE_CRITERIA" \
           "Custom.Bundle=$BUNDLE" \
  [--project "$PROJECT"] \
  --output json
# Capture $STORY_ID

# Link to parent Feature (required — no orphan User Stories)
az boards work-item relation add \
  --id $STORY_ID \
  --relation-type parent \
  --target-id $FEATURE_ID \
  --output json
```
Print: `  User Story #$STORY_ID created: $STORY_TITLE`

## Phase 5: Create Tasks under each User Story (if --tasks provided)
For each User Story created, for each `$TASK_TITLE` in the tasks list.
`ESTIMATE` defaults to `8` if not provided. `REMAINING_WORK` = `ESTIMATE`.

```bash
# Create Task with all Corestack mandatory fields
az boards work-item create \
  --type "Task" \
  --title "$TASK_TITLE" \
  --assigned-to "$ASSIGNED_TO" \
  --description "$TASK_TITLE" \
  --iteration "$ITERATION" \
  --fields "System.AreaPath=$AREA_PATH" \
           "Microsoft.VSTS.Scheduling.OriginalEstimate=8" \
           "Microsoft.VSTS.Scheduling.RemainingWork=8" \
  [--project "$PROJECT"] \
  --output json
# Capture $TASK_ID

# Link to parent User Story (required — no orphan Tasks)
az boards work-item relation add \
  --id $TASK_ID \
  --relation-type parent \
  --target-id $STORY_ID \
  --output json
```
Print: `    Task #$TASK_ID created: $TASK_TITLE`

## Output Format
```
Feature Hierarchy Created

Feature #$FEATURE_ID: $FEATURE_TITLE
  Assigned: $ASSIGNED_TO | Area: $AREA_PATH | Bundle: $BUNDLE
├── User Story #$S1_ID: $STORY_1
│   ├── Task #$T1_ID: $TASK_1 (Est: 8h)
│   └── Task #$T2_ID: $TASK_2 (Est: 8h)
├── User Story #$S2_ID: $STORY_2
│   ├── Task #$T1_ID: $TASK_1 (Est: 8h)
│   └── Task #$T2_ID: $TASK_2 (Est: 8h)
└── User Story #$S3_ID: $STORY_3
    ├── Task #$T1_ID: $TASK_1 (Est: 8h)
    └── Task #$T2_ID: $TASK_2 (Est: 8h)

Total: 1 Feature | $N User Stories | $M Tasks
Feature URL: https://dev.azure.com/{org}/{project}/_workitems/edit/$FEATURE_ID
```

## Error Handling
- Missing mandatory fields: fail early with usage message before creating anything
- If a User Story creation fails: log the error, continue with remaining stories, report failures at end
- If a Task creation fails: log it, continue, report at end
- If relation add fails: warn user but do not delete the work item — they can re-link manually with `az boards work-item relation add`

## Usage Examples
```
/azuredevops:create-feature "User Authentication" --assigned-to "dev@company.com" --area-path "MyProject\TeamA" --bundle "Q1-Release" --description "Implement full user authentication flow" --iteration "MyProject\Sprint 5"

/azuredevops:create-feature "User Authentication" --assigned-to "dev@company.com" --area-path "MyProject\TeamA" --bundle "Q1-Release" --description "Implement full user authentication flow" --stories "Login, Signup, Forgot Password" --acceptance-criteria "User can log in with email and password" --iteration "MyProject\Sprint 5"

/azuredevops:create-feature "User Authentication" --assigned-to "dev@company.com" --area-path "MyProject\TeamA" --bundle "Q1-Release" --description "Implement full user authentication flow" --stories "Login, Signup" --tasks "Design, Implement, Write Tests" --iteration "MyProject\Sprint 5"
```
