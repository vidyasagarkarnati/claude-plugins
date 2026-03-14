---
name: corestack-workitems
description: Corestack mandatory field requirements for Azure DevOps work items (Feature, User Story, Task), hierarchy rules, ADO field reference names, and creation patterns
---

# Corestack Work Items

Mastery of this skill ensures all Azure DevOps work items created for Corestack projects comply with mandatory field requirements and enforced hierarchy rules. Every agent that creates or updates ADO work items must follow these standards.

## When to Use This Skill
- Creating Features, User Stories, or Tasks in Azure DevOps
- Reviewing work items for completeness before sprint planning
- Linking work items to ensure correct parent-child hierarchy
- Auditing existing work items for missing mandatory fields

## Hierarchy Rules

```
Feature
└── User Story          (every User Story must have a parent Feature)
    └── Task            (every Task must have a parent User Story)
```

**Never create orphan work items.** A User Story without a parent Feature and a Task without a parent User Story are both invalid in Corestack's ADO setup.

## Mandatory Fields by Work Item Type

### Feature
| Field | ADO Field Reference | Notes |
|-------|-------------------|-------|
| Title | `System.Title` | Required |
| Description | `System.Description` | Required |
| Assigned To | `System.AssignedTo` | Required — never leave Unassigned |
| Area Path | `System.AreaPath` | Required |
| Iteration Path | `System.IterationPath` | Required |
| Bundle | `Custom.Bundle` | Required — Corestack custom field |

### User Story
| Field | ADO Field Reference | Notes |
|-------|-------------------|-------|
| Title | `System.Title` | Required |
| Description | `System.Description` | Required |
| Assigned To | `System.AssignedTo` | Required — never leave Unassigned |
| Acceptance Criteria | `Microsoft.VSTS.Common.AcceptanceCriteria` | Required |
| Area Path | `System.AreaPath` | Required |
| Iteration Path | `System.IterationPath` | Required |
| Bundle | `Custom.Bundle` | Required — Corestack custom field |
| Parent Feature | relation: `parent` | Required — link to Feature ID |

### Task
| Field | ADO Field Reference | Notes |
|-------|-------------------|-------|
| Title | `System.Title` | Required |
| Description | `System.Description` | Required |
| Assigned To | `System.AssignedTo` | Required — never leave Unassigned |
| Area Path | `System.AreaPath` | Required |
| Iteration Path | `System.IterationPath` | Required |
| Original Estimate | `Microsoft.VSTS.Scheduling.OriginalEstimate` | Required — **default to 8 if unknown** |
| Remaining Work | `Microsoft.VSTS.Scheduling.RemainingWork` | Required — **set equal to Original Estimate at creation** |
| Parent User Story | relation: `parent` | Required — link to User Story ID |

## Quick Reference

```
Hierarchy:    Feature → User Story → Task
Bundle:       Required on Feature and User Story (Custom.Bundle)
Estimate:     Default 8h for Tasks when unknown
Remaining:    Always = Original Estimate at creation time
No orphans:   Never create a work item without a parent (except Features)
```

## Key Patterns

### Pattern 1: Create Feature (az CLI)
```bash
az boards work-item create \
  --type "Feature" \
  --title "$TITLE" \
  --assigned-to "$ASSIGNED_TO" \
  --description "$DESCRIPTION" \
  --iteration "$ITERATION" \
  --fields "System.AreaPath=$AREA_PATH" "Custom.Bundle=$BUNDLE" \
  --output json
```

### Pattern 2: Create User Story (az CLI)
```bash
STORY_ID=$(az boards work-item create \
  --type "User Story" \
  --title "$TITLE" \
  --assigned-to "$ASSIGNED_TO" \
  --description "$DESCRIPTION" \
  --iteration "$ITERATION" \
  --fields "System.AreaPath=$AREA_PATH" \
           "Microsoft.VSTS.Common.AcceptanceCriteria=$ACCEPTANCE_CRITERIA" \
           "Custom.Bundle=$BUNDLE" \
  --output json --query id -o tsv)

# Always link to parent Feature immediately after creation
az boards work-item relation add \
  --id $STORY_ID --relation-type parent --target-id $FEATURE_ID
```

### Pattern 3: Create Task (az CLI)
```bash
# ESTIMATE defaults to 8 if not provided
ESTIMATE=${ESTIMATE:-8}

TASK_ID=$(az boards work-item create \
  --type "Task" \
  --title "$TITLE" \
  --assigned-to "$ASSIGNED_TO" \
  --description "$DESCRIPTION" \
  --iteration "$ITERATION" \
  --fields "System.AreaPath=$AREA_PATH" \
           "Microsoft.VSTS.Scheduling.OriginalEstimate=$ESTIMATE" \
           "Microsoft.VSTS.Scheduling.RemainingWork=$ESTIMATE" \
  --output json --query id -o tsv)

# Always link to parent User Story immediately after creation
az boards work-item relation add \
  --id $TASK_ID --relation-type parent --target-id $STORY_ID
```

### Pattern 4: Audit for Missing Mandatory Fields (WIQL)
```bash
# Find User Stories missing Bundle or Acceptance Criteria
az boards query --wiql "
  SELECT [System.Id],[System.Title],[System.AssignedTo],[System.AreaPath]
  FROM WorkItems
  WHERE [System.WorkItemType] IN ('User Story','Feature')
  AND (
    [Custom.Bundle] = ''
    OR [Microsoft.VSTS.Common.AcceptanceCriteria] = ''
    OR [System.AssignedTo] = ''
  )
  AND [System.State] <> 'Closed'
" --output table

# Find Tasks missing Original Estimate or parent
az boards query --wiql "
  SELECT [System.Id],[System.Title],[System.AssignedTo]
  FROM WorkItems
  WHERE [System.WorkItemType] = 'Task'
  AND (
    [Microsoft.VSTS.Scheduling.OriginalEstimate] = 0
    OR [System.AssignedTo] = ''
  )
  AND [System.State] <> 'Closed'
" --output table
```

## Best Practices
1. Validate all mandatory fields *before* calling `az boards work-item create` — partial work items are hard to audit and break sprint planning
2. Set `Remaining Work = Original Estimate` at creation; update `Remaining Work` daily as work progresses — never touch `Original Estimate` after creation
3. Query open Features before creating a User Story — pick the right parent, don't create a new Feature just to have a parent
4. `Bundle` maps to a release or delivery milestone — confirm the value with the Product Manager before setting it; wrong Bundle silently misattributes work
5. `Area Path` determines which team board the item appears on — use the correct team's path, not the project root
6. Use `/azuredevops:create-feature` to build a full Feature → Story → Task tree in one command when planning a new body of work

## Common Issues
- **Missing Bundle on User Story/Feature**: item will not appear in bundle-filtered reports; always set before moving to Active
- **Task with no parent**: breaks sprint board hierarchy; use `az boards work-item relation add --relation-type parent` to fix
- **Original Estimate = 0**: capacity planning reports will show incorrect hours; update immediately when discovered
- **Remaining Work not updated**: sprint burndown will be flat until updated; remind developers to update daily
- **Wrong Area Path**: item appears on wrong team's board; correct with `az boards work-item update --id <id> --fields "System.AreaPath=<correct-path>"`
