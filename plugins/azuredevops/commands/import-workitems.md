---
description: "Bulk-create Azure DevOps Features, User Stories, and Tasks from PRD/TDD docs or an ad-hoc description — uses Python SDK, no MCP tokens, no per-item confirmation"
argument-hint: "[<feature-name> | --adhoc] [--prd <path>] [--tdd <path>] [--assigned-to <email>] [--area-path <path>] [--iteration <path>] [--bundle <value>] [--project <name>]"
---

# Import Work Items

Bulk-create Azure DevOps work items (Features, User Stories, Tasks) in a single pass. Two modes:

- **Document mode** (default): reads an existing PRD and/or TDD markdown file, extracts work items, creates them all at once
- **Ad-hoc mode** (`--adhoc`): you describe what to create conversationally, Claude structures the JSON, then creates everything

All creation is handled by `scripts/ado_bulk_create.py` using the `azure-devops` Python SDK — no MCP tool calls, no `az` CLI, no per-item confirmation.

## Prerequisites

```bash
pip install -r scripts/requirements.txt
export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-org"
export AZURE_PERSONAL_ACCESS_TOKEN="your-pat"
export AZURE_DEVOPS_PROJECT="YourProject"   # optional if --project is passed
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<feature-name>` | Mode A only | Base name matching `docs/prd-<name>.md` and `docs/tdd-<name>.md` |
| `--adhoc` | Mode B only | Switch to ad-hoc conversational mode |
| `--prd <path>` | Optional | Explicit path to PRD file (overrides name-based lookup) |
| `--tdd <path>` | Optional | Explicit path to TDD file (overrides name-based lookup) |
| `--assigned-to` | Optional | Default assignee for all items (e.g. `dev@company.com`); prompted if omitted |
| `--area-path` | Optional | ADO area path (e.g. `MyProject\TeamA`); prompted if omitted |
| `--iteration` | Optional | ADO iteration path (e.g. `MyProject\Sprint 5`); prompted if omitted |
| `--bundle` | Optional | Corestack Bundle field value (e.g. `Q1-Release`); prompted if omitted |
| `--project` | Optional | ADO project name (overrides `AZURE_DEVOPS_PROJECT` env var) |

## Mode A — Document Mode

### Step 1: Parse arguments

Extract `<feature-name>`, `--prd`, `--tdd`, and all defaults from `$ARGUMENTS`.

- If `--prd` is given, use that path directly.
- Otherwise, infer PRD path as `docs/prd-<feature-name>.md`
- If `--tdd` is given, use that path directly.
- Otherwise, infer TDD path as `docs/tdd-<feature-name>.md`

### Step 2: Read documents

Use the Read tool to load both files. If either file does not exist, report which file is missing and stop.

### Step 3: Extract Features and User Stories from PRD

Scan the PRD for:

- **Features / Epics**: top-level section headings (`##`) that represent a feature or capability area
- **User Stories**: any line or block matching `As a <persona>, I want <action>` pattern, or bullet points under feature sections describing user-facing behaviour
- **Acceptance Criteria**: `Given/When/Then` blocks or bullet lists labelled "Acceptance Criteria" associated with each story

For each story, `acceptance_criteria` is **mandatory**. If a story has no explicit acceptance criteria in the PRD, derive it from the story description (write one sentence in Given/When/Then format). Do not skip the field.

### Step 4: Extract Tasks from TDD

Scan the TDD's **Implementation Plan** section for:

- Ordered task list entries (numbered or bulleted)
- Complexity indicators: `S` or `small` → 4h, `M` or `medium` → 8h, `L` or `large` → 16h; absent → 8h
- Map each task to its parent User Story by matching the section heading or story reference in the TDD

If the TDD has no Implementation Plan section, skip tasks (create Feature + Stories only).

### Step 5: Build JSON manifest

Assemble the manifest following this schema:

Only include a `defaults` key if at least one of `--assigned-to`, `--area-path`, `--iteration`, or `--bundle` was provided. Omit any field not supplied — the script will prompt interactively for missing values.

```json
{
  "project": "<project or env default>",
  "defaults": {
    "assigned_to": "<--assigned-to value, if provided>",
    "area_path": "<--area-path value, if provided>",
    "iteration_path": "<--iteration value, if provided>",
    "bundle": "<--bundle value, if provided>"
  },
  "features": [
    {
      "title": "...",
      "description": "...",
      "stories": [
        {
          "title": "...",
          "description": "...",
          "acceptance_criteria": "...",
          "tasks": [
            { "title": "...", "description": "...", "estimate": 8 }
          ]
        }
      ]
    }
  ]
}
```

### Step 6: Preview and confirm (once)

Print the extracted hierarchy:

```
Extracted from docs:
  Feature: User Authentication
    Story: Login Page
      AC: Given valid creds, user is authenticated.
      Task: Implement POST /auth/login [6h]
      Task: Write unit tests [4h]
    Story: Logout Flow
      AC: Given authenticated session, logout clears token.
      Task: Implement DELETE /auth/session [4h]

  2 Features | 4 Stories | 8 Tasks
  Defaults: assigned=dev@company.com | area=MyProject\TeamA | iteration=MyProject\Sprint 5 | bundle=Q1-Release

Proceed with bulk creation? [y/N]
```

Wait for user confirmation before calling the script.

### Step 7: Write JSON and call script

Write the manifest to `/tmp/ado_import_<timestamp>.json`, then run:

```bash
python3 scripts/ado_bulk_create.py --input /tmp/ado_import_<timestamp>.json
```

The script prints its own progress and summary. Do not echo each creation — the script handles output.

---

## Mode B — Ad-hoc Mode

### Step 1: Collect description

If `--adhoc` is in `$ARGUMENTS`, prompt the user:

```
Describe the work items to create. Include:
- Feature name(s) and description
- User Stories under each feature (with acceptance criteria)
- Tasks under each story (with estimated hours if known)

Example:
  Feature "Notification System":
    Story "Email Alerts": users receive email when assigned a task
      AC: Given task assigned, email sent within 30s
      Tasks: SMTP config (4h), email templates (6h), retry logic (4h)
    Story "In-app Badges": unread count shown in nav
      AC: Given new notification, badge count increments
      Tasks: websocket listener (8h), badge UI component (4h)
```

### Step 2: Structure the description

From the user's response, build the same JSON manifest schema as Mode A. Apply all defaults from command arguments.

For any missing `acceptance_criteria`, derive from the story description in Given/When/Then format. Do not skip.
For any missing task `estimate`, default to 8.

### Step 3: Preview and confirm (once)

Same preview format as Mode A Step 6. Wait for user confirmation.

### Step 4: Write JSON and call script

Same as Mode A Step 7.

---

## Error Handling

The script handles partial failures:
- Feature fails → its stories and tasks are skipped
- Story fails → its tasks are skipped
- Task fails → logged, execution continues

The script exits with code 1 if any items failed. On failure, it prints re-run hints for each failed item.

To re-run only failed items, create a new manifest with just the failed items and call:

```bash
python3 scripts/ado_bulk_create.py --input /tmp/ado_retry.json
```

---

## Examples

### Document mode (after prd-workflow)

```
/azuredevops:import-workitems user-authentication-oauth2 \
  --assigned-to dev@company.com \
  --area-path "MyProject\TeamA" \
  --iteration "MyProject\Sprint 5" \
  --bundle "Q1-Release"
```

### Ad-hoc mode

```
/azuredevops:import-workitems --adhoc \
  --assigned-to dev@company.com \
  --area-path "MyProject\TeamA" \
  --iteration "MyProject\Sprint 5" \
  --bundle "Q1-Release"
```

Then describe your features and stories when prompted.

### With explicit file paths

```
/azuredevops:import-workitems \
  --prd docs/prd-auth.md \
  --tdd docs/tdd-auth-v2.md \
  --assigned-to lead@company.com \
  --area-path "MyProject\Platform" \
  --iteration "MyProject\Sprint 6" \
  --bundle "Q2-Release" \
  --project MyOtherProject
```
