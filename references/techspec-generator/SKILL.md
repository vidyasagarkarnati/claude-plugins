---
name: techspec-generator
description: >
  Generate a complete Technical Specification Word document (.docx) from a PRD and/or Action Plan.
  Use this skill whenever the user provides a PRD (Product Requirements Document) or action plan
  and wants to produce a Tech Spec, Technical Design Document, or engineering spec. Triggers include:
  "generate tech spec", "create technical specification", "write tech spec from PRD", "turn this PRD
  into a tech spec", "produce engineering spec", or any request where someone uploads a PRD or action
  plan file and wants technical documentation output. Always use this skill when the user provides
  input documents (PRD, action plan, feature brief) and the desired output is a technical specification.
  Also use this skill when the user asks to update, regenerate, or improve an existing tech spec document.
---

# Tech Spec Generator — CoreStack Style

Generates a polished Tech Spec Word document (.docx) in CoreStack's exact house style, from a PRD
and/or Action Plan. Skips the User Stories section entirely. Uses `[TBD]` for anything not covered
by the input documents.

Reference samples are in `assets/` — study their patterns before generating:
- `assets/sample_k8.docx` — K8s Onboarding: deep API hierarchy, complex Data Model, agent-based design
- `assets/sample_azure_mca.docx` — Azure MCA: hierarchy sync, extended background job, permissions table
- `assets/sample_ai_agent.docx` — AI Agent Metering: concurrency section, Observability, Use Cases, full Checklist + Deployment
- `assets/sample_metrics.docx` — Metrics Utilization: background job with storage analysis, flowchart reference, class-based data model
- `assets/sample_batch_api.docx` — Batch API Refactoring: API optimisation with full request/response models, "No new Audit Log Added" pattern

---

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| PRD document (.docx) | Recommended | Feature goals, use cases, UX reference |
| Action Plan document (.docx) | Recommended | APIs, DB changes, jobs, deployment notes |

At least one input must be provided. If neither is supplied, ask the user before proceeding.

---

## Step 1 — Extract content from inputs

```bash
pandoc input.docx -o extracted.md
```

**From PRD extract:**
- Feature name, short description, ADO/Jira feature link
- Status (DRAFT / REVIEW / APPROVED / HOLD) — use DRAFT if not stated
- Author name and date
- Overview / objective paragraph
- Use cases or scenario list
- UX / Figma links
- Benefits (used in Overview narrative)
- Any concurrency, locking, or special design considerations

**From Action Plan extract:**
- Design considerations and approach narrative
- High-level design component list
- Background jobs (name, trigger, purpose, frequency, storage analysis if present)
- API endpoints (full request/response JSON, auth, headers, status codes)
- API data model classes (typed Java/pseudocode style with inline comments)
- MongoDB collections introduced or impacted
- Index definitions
- Sample records (new and with modifications highlighted)
- Audit log entries
- Error messages
- Checklist items (External API, Angular version, team impact)
- Deployment items (config, DevOps, firewall)
- Technical Specification items (Figma, UI html, third-party libs)
- Observability details (metrics, logs, traces, visualization)

---

## Step 2 — Content mapping decisions

For each section decide:
- Content available → fill it in fully
- Partially available → fill what exists, mark gaps `[TBD]`
- Not mentioned → use `[TBD]` throughout
- Explicitly not applicable → write "N/A" or "No" (never leave cell blank)
- Special explicit statement (e.g. "No new Audit Log Added") → write that exact statement as a paragraph before the table

**Never skip a section.** Every section must appear even if all cells say "No".

---

## Step 3 — Generate the Tech Spec .docx

Read `/mnt/skills/public/docx/SKILL.md` before writing any code.

### Document structure (exact order)

```
[Header block]
Tech Spec                                  <- H1
  Overview                                 <- H2
  Version-Based / Concurrency section      <- H2  (only if locking/concurrency described)
  Concurrency Example                      <- H2  (only if concurrency table present)
  Use Cases                                <- H2
  Background Job                           <- H2
  API                                      <- H2
    API Summary                            <- H3
    API Details                            <- H3  (one table per endpoint)
    API Data Model                         <- H3
  Observability                            <- H2
  Data Model                               <- H2
  Audit Log                                <- H2
  Error Message                            <- H2
  Checklist                                <- H2
  Deployment                               <- H2
  Technical Specification                  <- H2
```

> **Never include:** PRD section, Feature Summary, User Stories, Planning the launch,
> Customer Adoption, Product Marketing Plan, Product Tour, FAQ, Testing section.
> Those are excluded by design.

> **Checklist and Deployment ARE included** — they appear in most real samples. Always generate them.

---

### Header block

Match this exact layout (from all real samples):

```
[Feature Name]               <- bold title paragraph
Short Description            <- plain text, or actual short desc from PRD
Feature Link: [hyperlink]    <- linked ADO/Jira URL, or [TBD]
Status [DRAFT|REVIEW|APPROVED|HOLD]
Prepared by:
[Author name]
[Date DD/MM/YYYY or DD-Mon,YYYY]

This document consists of
TechSpec
```

---

### Section: Overview

2–4 paragraphs. Cover:
1. What the feature does (engineering lens, not user-story language)
2. Objective / goal
3. Key sub-systems, entities, or architectural choices relevant to the design

After prose, add diagram placeholders using italic/plain text:
```
System Design Diagram
[TBD — add architecture diagram]

[Any other referenced diagrams: sequence, flow, HLD image]
[TBD — add diagram]
```

If diagrams are referenced in the PRD (even by name or figma link), include a placeholder line for each.

---

### Section: Version-Based / Concurrency (optional)

**Only include if** the inputs describe optimistic locking, race conditions, or version-based
concurrency controls (like the AI Agent Metering sample).

Write as bullet points listing the approach's benefits. Then add the Concurrency Example as a
separate H2 section with a multi-column table showing time/actor/state columns.

---

### Section: Use Cases

Numbered list. Extract from PRD use cases / scenarios.

For refactoring or optimisation features (like Batch API sample), Use Cases are often architectural
goals rather than user stories, e.g.:
1. Remove hierarchy build logic from UI
2. Child count will be passed in API response list
3. API will support pagination for large Service Account lists

If none found: one `[TBD]` entry.

---

### Section: Background Job

**Pattern A — Named new job:**
State the job class name as a H3 or bold heading, then describe it.
Follow with bullet list of behaviours (schedule, data window, granularity, document limits, etc.)
Add storage analysis paragraph if present (like Metrics sample — "Each document stores 1,440 data points...").

**Pattern B — Existing job extended:**
"No new background job will be introduced. The existing **[JobName]** background job will be extended..."
List external APIs used with hyperlinks if available.
Add permissions table if needed (Hierarchy Level | Purpose | Role | Description).

**Pattern C — Not applicable:**
"N/A." (exactly as in multiple samples — just the abbreviation and period)

---

### Section: API

#### API Summary table

Three columns: Item | Yes/No/NA | Impact Details if yes

Standard rows: Module, Internal API, External API.

Note: some samples use different row labels (e.g. "Identity" instead of "Module" in AI Agent sample).
Use whatever row labels appear in the input; default to Module / Internal API / External API.

For Internal API impact cell: list old APIs impacted AND new APIs introduced as numbered sub-lists.
If no impact on existing APIs and no new APIs: write "No Impact".

#### API Details — one table per endpoint

**Each endpoint = its own two-column table (Item | Description).**
Add an H3 or bold heading with the API name before each table.

Full row set (from AI Agent / Batch API samples — most complete):
- API Name (include method + path below if not a separate row)
- Purpose
- Is New Api
- Endpoint
- Method
- Authentication
- Authorization
- Headers
- Query Strings
- Request (full JSON)
- Response (full JSON)
- Status Codes

For endpoints with **no request body** (GET): write "NONE" in the Request row.

**JSON payloads must be complete** — never summarise or truncate. Each JSON line = separate Paragraph
in Courier New 9pt inside the cell.

**Class name reference at bottom of Request/Response cells:** some samples append the model class
name below the JSON block (e.g. `MasterAccountBalanceUpdateRequest`). Match this if present.

#### API Data Model

Use typed Java/pseudocode class style. Include inline comments after `//` for every field.
Group with `//` or plain-text section headers (e.g. `Request Models`, `Filters`, `Pagination`,
`Response Models`, `Service Account Data`).

Match the exact comment style from samples:
```java
public class ClassName {
  private Type fieldName; // Description of what this field does
}
```

---

### Section: Observability

This section is **mandatory** in all specs. If the input has detailed observability content
(like the Batch API sample), render it with sub-headings or bullet groups:
- **Metrics:** list of key metrics (latency, request count, error rate, cache hit/miss, etc.)
- **Logs:** fields logged per request (tenant_id, filters, slow request threshold, etc.)
- **Traces:** trace flow description (API → Cache → DB → Aggregation)
- **Key Data:** what is captured per transaction/request
- **Visualization:** dashboard panels described, alert thresholds

If the input has a prose observability section (like AI Agent sample), render it as bullet list
under the section heading without sub-headings.

If nothing in the input: write:
"Observability will be implemented via structured logging and metrics. Key data captured will include
request latency, error rates, and relevant domain events. Dashboards will be configured in
`[TBD — monitoring tool]`. Specific metrics and trace IDs are `[TBD]`."

---

### Section: Data Model

Three-column table: Item | Yes/No/NA | Impact details if yes

Rows (exact order, all 14):
1. Database Introduced
2. Collection(s) Introduced
3. Collections Impacted
4. Document Introduced
5. Field modification or any new possible value
6. Sample new Record
7. Sample Record with modifications highlighted
8. Index Creation
9. Index Details
10. Is there any backward compatibility?
11. Is Migration Required?
12. RBAC Changes
13. Will there be any changes to new setup installation scripts?
14. Expected Load / Any Infra changes required?

**For sample records:**
- Put full MongoDB JSON document in the Impact column
- Include ISODate(), ObjectId() wrappers exactly as they appear in source
- For "modifications highlighted" row: **bold** the changed block (match K8s/Azure MCA style)
- If N/A (like AI Agent sample): write "N/A" in Yes/No column, leave Impact blank

**For Index Details:** render the pymongo index definitions exactly as in the source.

**For Is Migration Required?:** can be "May be" with an explanation (like AI Agent sample — accept
nuanced answers, not just Yes/No).

---

### Section: Audit Log

Two-column table: Action | Message added to Audit Log

**Three patterns from samples:**

A) **Real entries** (AI Agent sample style):
```
ADD_BALANCE_MANUAL    | admin_user_42 performed ADD_BALANCE_MANUAL on master account MA-1001. Transaction ID: TX-1a2b3c
DEDUCT_BALANCE_AGENT  | SYSTEM performed DEDUCT_BALANCE_AGENT on master account MA-1001...
```

B) **Existing logs cover it** (Batch API sample):
Write "No new Audit Log Added" as the only content in the first cell, second cell blank.
(Still render the table — one row with this statement.)

C) **No logs added** (Azure MCA sample):
Write a paragraph before the table: "No new audit log added, existing logs will cover this"
Then include the table with 3 blank rows.

---

### Section: Error Message

Two-column table: Message | Description

**Two patterns:**

A) **Real entries:** list error codes and descriptions.

B) **Captured in API responses** (AI Agent / Batch API sample):
Write "Captured in the above API responses" in the Message column, leave Description blank.
Then two more blank rows.

---

### Section: Checklist

Two-column table: Item | Description

**Rows (from AI Agent / Batch API samples):**
- Is External API available → Yes/No + justification
- Angular 14 or Angular.js → specify which + justification if mixed (Angular.js for older screens, Angular 14 for new pages)
- Impact on the Other Teams? → team names or "None"

If the input has no checklist data, use `[TBD]` for Description cells.

---

### Section: Deployment

Two-column table: Item | Description

**Rows:**
- Config Change → No / or list new configs
- Dependency with DevOps → No / or ADO ticket reference
- Firewall Changes → No / or ADO ticket reference

---

### Section: Technical Specification

Two-column table: Item | Descriptions

**Rows:**
- Figma → URL (hyperlinked) or "Yet to be received" or "-" or `[TBD]`
- UI html → same options
- Third Party Library → "No" / "Yes. [list libs]" / blank template text

Match exactly what appears in the source. Do not default to `[TBD]` if the sample uses "-" or
"Yet to be received" — use the phrasing from the input.

---

## Step 4 — Styling rules

Read `/mnt/skills/public/docx/SKILL.md` for full docx-js API.

**Fonts & colours:**
- Default: Arial, 12pt (24 half-points)
- H1: Arial, 18pt, bold, dark navy `1F3864`
- H2: Arial, 14pt, bold, CoreStack blue `2E75B6`
- H3: Arial, 12pt, bold, CoreStack blue `2E75B6`
- Body: Arial, 12pt, black `000000`

**Tables:**
- Border: light grey single `CCCCCC`
- Header cells: shaded `D5E8F0`, bold, `ShadingType.CLEAR`
- Cell padding: `{ top: 80, bottom: 80, left: 120, right: 120 }`
- Always set both `columnWidths` array AND cell `width` in DXA
- US Letter content width = 9360 DXA

Standard column widths (DXA):
- Two-column detail/deployment tables: col1=2800, col2=6560
- Three-column summary tables: col1=3000, col2=2000, col3=4360
- Data model table: col1=3000, col2=1500, col3=4860
- Audit log / error / checklist: col1=3500, col2=5860
- Concurrency example (4 col): col1=1200, col2=2500, col3=2500, col4=3160

**JSON in cells:** Each JSON line = separate `Paragraph` with
`TextRun({ text: line, font: "Courier New", size: 18 })`. Never use `\n`.

**CRITICAL — tcell must always receive an array:** The `tcell(content, width)` helper must
always be passed an array of Paragraph elements as the first argument. Passing a bare `Paragraph`
object (not wrapped in `[]`) causes the cell to silently render empty — this is the root cause
of blank Item columns in API Detail tables. Always write:
  - ✅ `tcell([new Paragraph(...)], width)`
  - ❌ `tcell(new Paragraph(...), width)`  ← renders empty

**Never add a duplicate header row** as a data entry in `detailTable` — the `Item | Description`
header is always auto-generated as the first row. Do not include `["Item", "Description"]` in
the rows array.

**Bold text in cells (modified fields):** Use `TextRun({ text: "...", bold: true })` inline.

**Lists:** `LevelFormat.BULLET` / `LevelFormat.DECIMAL` with numbering config. Never unicode bullets.

**Page:** US Letter 12240 × 15840 DXA, 1-inch margins all sides.

**Output filename:** `TechSpec-<FeatureName>.docx`

---

## Step 5 — Validate and deliver

```bash
python scripts/office/validate.py TechSpec-FeatureName.docx
```

If validation fails: unpack → fix XML → repack.

Copy to `/mnt/user-data/outputs/TechSpec-<FeatureName>.docx` and call `present_files`.

---

## Rules & guardrails (all non-negotiable)

- **Never generate User Stories or Testing sections** — excluded by design.
- **Always include Checklist and Deployment** — they appear in most real samples.
- **Never skip any section** — every section must appear even if "No" or "N/A".
- **Never summarise JSON payloads** — reproduce them in full.
- **Class definitions must be typed** — always include field type + `// comment`.
- **Bold modified fields** in Data Model sample records.
- **Background job N/A = "N/A."** — just the abbreviation and period (not a full sentence).
- **Audit log "no new entries" = exact phrase** from the source (not generic `[TBD]`).
- **Error message "captured in API" = exact phrase** from the source.
- **Use `[TBD]`** only when information is genuinely missing from inputs.
- **Never use `\n` inside paragraphs** — use separate `Paragraph` elements.
- **Never use unicode bullet characters** — use `LevelFormat.BULLET` with numbering config.
- **Status from input doc** — if source says REVIEW, output says REVIEW; not always DRAFT.
- **Date from input** — use date from source document, not today's date, unless genuinely absent.
