---
description: "Documentation workflow: PM writes user-facing docs, Technical Writer formats, Prompt Engineer optimizes clarity"
argument-hint: "<what-to-document> [--type api|howto|readme|runbook]"
---

# Doc Flow

End-to-end documentation workflow. Product Manager captures the user-facing narrative, Technical Writer structures and formats it, Prompt Engineer optimizes for clarity and discoverability.

## Chain

```
use_agent: product-manager
```
**Input**: `$ARGUMENTS` — what to document and type
**Task**: User-facing narrative and context:
- What is the audience for this documentation? (developers, end users, ops)
- What does the user need to accomplish?
- What are the key concepts the reader must understand?
- Write a first draft of the core content (feature explanation, use cases, goals)
- Flag any gaps where technical details are needed
**Handoff artifact**: Draft content + audience profile + list of technical gaps

---

```
use_agent: technical-writer
```
**Input**: PM draft + audience profile
**Task**: Structure, accuracy, and completeness:
- Run `/document --type $TYPE --path <relevant-code>` to gather technical details
- Fill in the technical gaps identified by PM
- Structure the doc according to the type template (API / HOWTO / README / runbook)
- Add code examples, command snippets, and diagrams where needed
- Ensure every example is runnable and accurate
- Add cross-references to related docs
**Handoff artifact**: Structured, complete draft document

---

```
use_agent: prompt-engineer
```
**Input**: Complete draft from Technical Writer
**Task**: Clarity, tone, and discoverability optimization:
- Apply plain language principles (no jargon without definition, active voice)
- Optimize headings and structure for scannability
- Add a TL;DR / Quick Start section at the top for busy readers
- Ensure consistent terminology with the rest of the docs
- Review code examples for correctness and readability
- Final polish: formatting, consistent casing, no spelling errors
**Output**: Finalized document saved to appropriate path

## Output
By end of this workflow:
1. Complete, polished documentation at `docs/<type>/<name>.md`
2. All examples verified as accurate
3. Consistent with existing docs style

## Usage
```
/orchestrators:doc-flow "user authentication flow" --type howto
/orchestrators:doc-flow "orders API" --type api
```
