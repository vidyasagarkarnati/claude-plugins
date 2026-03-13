---
description: "Generate a CoreStack-style Tech Spec Word document (.docx) from a PRD and/or Action Plan"
argument-hint: "<feature-name> [--prd <path/to/prd.docx>] [--action-plan <path/to/plan.docx>]"
---

# Create Tech Spec (.docx)

Invoke the `techspec-generator` skill to produce `TechSpec-<FeatureName>.docx` in CoreStack house style.

## Pre-flight Checks
1. Confirm at least one input document is provided (`--prd` or `--action-plan`)
2. If neither provided, ask the user before proceeding
3. Read `.claude/memory/project-state.md` for project context

## Execution

Delegate fully to the `techspec-generator` skill. Follow its 5-step process:

1. Extract content from input docs via `pandoc`
2. Map content to CoreStack sections (Overview → Use Cases → Background Job → API → Observability → Data Model → Audit Log → Error Message → Checklist → Deployment → Technical Specification)
3. Generate `.docx` with CoreStack styling (Arial fonts, navy/blue headings, grey-bordered tables)
4. Validate output
5. Deliver `TechSpec-<FeatureName>.docx`

## Output

`TechSpec-$ARGUMENTS.docx` — validated CoreStack-format Word document
