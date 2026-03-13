---
description: "Create an Azure DevOps Feature with child User Stories and Tasks in one command"
argument-hint: "<feature-title> [--stories \"<s1>, <s2>\"] [--tasks \"<t1>, <t2>\"] [--iteration <path>] [--project <name>]"
---

# Create Feature

Create a Feature work item in Azure DevOps, then create child User Stories under it, and optionally create Tasks under each User Story — all in a single command chain.

## Pre-flight Checks
1. Confirm `az devops` extension is installed: `az extension list --query "[?name=='azure-devops']"`
2. Check defaults: `az devops configure --list`
3. If `--iteration` not provided, list available iterations:
   ```bash
   az boards iteration project list --output table
   ```

## Phase 1: Parse Arguments
Extract from `$ARGUMENTS`:
- `FEATURE_TITLE` — required
- `--stories` — comma-separated list of User Story titles (quoted string)
- `--tasks` — comma-separated list of Task titles to create under EACH User Story
- `--iteration` — iteration path applied to Feature and all children
- `--project` — optional project override

If `--stories` not provided, create just the Feature and stop.

## Phase 2: Create the Feature
```bash
az boards work-item create \
  --type "Feature" \
  --title "$FEATURE_TITLE" \
  [--iteration "$ITERATION"] \
  [--project "$PROJECT"] \
  --output json
```
Capture returned `id` as `$FEATURE_ID`.

Print: `Feature #$FEATURE_ID created: $FEATURE_TITLE`

## Phase 3: Create User Stories (for each story in --stories)
For each `$STORY_TITLE` in the stories list:

```bash
# Create User Story
az boards work-item create \
  --type "User Story" \
  --title "$STORY_TITLE" \
  [--iteration "$ITERATION"] \
  [--project "$PROJECT"] \
  --output json
# Capture $STORY_ID

# Link to Feature
az boards work-item relation add \
  --id $STORY_ID \
  --relation-type parent \
  --target-id $FEATURE_ID \
  --output json
```
Print: `  User Story #$STORY_ID created: $STORY_TITLE`

## Phase 4: Create Tasks under each User Story (if --tasks provided)
For each User Story created, for each `$TASK_TITLE` in the tasks list:

```bash
# Create Task
az boards work-item create \
  --type "Task" \
  --title "$TASK_TITLE" \
  [--iteration "$ITERATION"] \
  [--project "$PROJECT"] \
  --output json
# Capture $TASK_ID

# Link to User Story
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
├── User Story #$S1_ID: $STORY_1
│   ├── Task #$T1_ID: $TASK_1
│   └── Task #$T2_ID: $TASK_2
├── User Story #$S2_ID: $STORY_2
│   ├── Task #$T1_ID: $TASK_1
│   └── Task #$T2_ID: $TASK_2
└── User Story #$S3_ID: $STORY_3
    ├── Task #$T1_ID: $TASK_1
    └── Task #$T2_ID: $TASK_2

Total: 1 Feature | $N User Stories | $M Tasks
Feature URL: https://dev.azure.com/{org}/{project}/_workitems/edit/$FEATURE_ID
```

## Error Handling
- If a User Story creation fails: log the error, continue with remaining stories, report failures at end
- If a Task creation fails: log it, continue, report at end
- If relation add fails: warn user but do not delete the work item — they can re-link manually

## Usage Examples
```
/azuredevops:create-feature "User Authentication"
/azuredevops:create-feature "User Authentication" --stories "Login, Signup, Forgot Password"
/azuredevops:create-feature "User Authentication" --stories "Login, Signup" --tasks "Design, Implement, Write Tests" --iteration "MyProject\Sprint 5"
```
