---
mode: agent
description: "Generate documentation for code, APIs, or systems"
# argument-hint: [--type api|howto|readme|runbook] [--path <file-or-dir>]
---


# Document

Generate high-quality documentation for code, APIs, or operational procedures. Uses Technical Writer + Prompt Engineer persona.

## Pre-flight Checks
1. Parse `${input:arguments}` for `--type` and `--path`
2. If `--path` provided, read the target file/directory
3. Default type: auto-detect from path (`.ts`/`.py` → api, `ops/` → runbook)

## Phase 1: Code Analysis
- Read the target code files thoroughly
- Identify: exported functions/classes, their inputs/outputs, side effects
- Note: complex logic, non-obvious behavior, error cases
- Find existing JSDoc/docstrings to understand the current documentation state

## Phase 2: Content Generation by Type

### API Documentation (OpenAPI/Swagger)
Generate for each endpoint:
```yaml
/orders/{id}:
  get:
    summary: Get order by ID
    parameters:
      - name: id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Order found
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Order'
      404:
        description: Order not found
```

### HOWTO Guide
Structure:
1. **Title**: "How to [accomplish specific task]"
2. **Prerequisites**: what the reader needs before starting
3. **Steps**: numbered, each with a command or action + expected result
4. **Verification**: how to confirm it worked
5. **Troubleshooting**: common errors and fixes

### README
Structure:
1. Project name + one-line description
2. Quick start (get running in < 5 commands)
3. Configuration (env vars table)
4. Available commands / scripts
5. Architecture overview (link to TDD)
6. Contributing guide
7. License

### Runbook (Operational)
Structure:
1. **Service overview**: what it does, who owns it
2. **Alerts and their meaning**: each alert name → description → severity → action
3. **Incident response steps**: numbered checklist
4. **Common issues**: symptom → diagnosis → fix
5. **Escalation path**: who to page and when
6. **Useful commands**: copy-paste ready

## Phase 3: Quality Check
- All code examples are runnable and correct
- No placeholder text left in output
- Terminology is consistent with the codebase
- Links are valid (no dead references)

## Output Format
- Print documentation to console
- Optionally save: API → `docs/api/<service>.yaml`, HOWTO → `docs/howto/<name>.md`, README → `README.md`, Runbook → `docs/runbooks/<service>.md`

## Error Handling
- File not found: report and ask for correct path
- Empty file: report "No code to document"
- Ambiguous type: ask before generating
