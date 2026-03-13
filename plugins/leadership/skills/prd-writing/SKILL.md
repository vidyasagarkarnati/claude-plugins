---
name: prd-writing
description: PRD structure, problem statements, user story format, acceptance criteria, RICE prioritization, and success metrics
---

# PRD Writing

Mastery of this skill enables you to produce clear, actionable Product Requirements Documents that align engineering, design, and stakeholders around a shared understanding of what to build and why.

## When to Use This Skill
- Starting a new feature or product initiative
- Translating stakeholder requests into engineering-ready requirements
- Prioritizing a backlog using a scoring framework
- Defining success metrics before development begins
- Reviewing an existing PRD for completeness

## Core Concepts

### 1. PRD Structure
1. **Executive Summary** — one paragraph, the whole story
2. **Problem Statement** — what's broken, for whom, how bad
3. **Solution Overview** — what we're building (not how)
4. **User Personas** — who uses it and what they need
5. **User Stories + AC** — specific behaviors with testable criteria
6. **Success Metrics** — how we know it's working
7. **Timeline** — MVP → Beta → GA phases
8. **Risks & Dependencies** — what could go wrong
9. **Open Questions** — unresolved decisions

### 2. User Story Format
```
As a [specific persona],
I want to [specific action or goal],
So that [measurable outcome or value].
```

### 3. RICE Scoring
| Factor | Formula | Notes |
|--------|---------|-------|
| Reach | users/quarter | How many users affected |
| Impact | 0.25/0.5/1/2/3 | How much it moves the needle |
| Confidence | 50%/80%/100% | How sure are we |
| Effort | person-weeks | Cost to build |
| **Score** | R × I × C / E | Higher = higher priority |

## Quick Reference
```
Problem statement formula:
"[Persona] struggles with [problem] because [root cause].
This results in [business impact]. Currently, they [workaround]."

Metric framework: North Star + 2–3 supporting metrics + guardrail metrics
North Star: measures the core value delivered
Guardrail: metrics that must not degrade (e.g., error rate, churn)
```

## Key Patterns

### Pattern 1: Strong Problem Statement
```markdown
## Problem Statement

**Who**: Enterprise customers with > 100 users on our platform
**What**: Cannot bulk-export user activity data for compliance audits
**Magnitude**: 23 enterprise accounts have requested this feature in the last 6 months; 3 are at churn risk without it
**Current workaround**: Customers manually export page-by-page, which takes 4-8 hours per audit

**Out of scope**: Real-time streaming exports, custom report builder, data transformation
```

### Pattern 2: User Story + Acceptance Criteria
```markdown
### Story: Export user activity report

**As** a Compliance Officer at an enterprise company,
**I want** to export a CSV of all user activity in a date range,
**So that** I can submit it to our auditor within the required 24-hour window.

**Acceptance Criteria:**

Given I am logged in as a user with "Compliance" role
When I navigate to Settings > Exports > Activity Report
Then I see a date range picker and "Export CSV" button

Given I select a 90-day date range and click "Export CSV"
When the export is complete (within 5 minutes for up to 100k rows)
Then I receive an email with a download link that expires in 24 hours

Given the export contains > 1M rows
When I request the export
Then I am warned it will take up to 30 minutes and notified by email when ready
```

### Pattern 3: Success Metrics
```markdown
## Success Metrics

| Metric | Baseline | Target | Timeframe | Source |
|--------|----------|--------|-----------|--------|
| Compliance export adoption | 0% | 60% of enterprise accounts | 90 days post-launch | Product analytics |
| Churn risk tickets resolved | 3 open | 0 | 30 days | Salesforce |
| Time to complete audit export | 4-8 hours (manual) | < 10 minutes | Measured via survey | User interviews |
| Export error rate | N/A | < 1% | Ongoing | Application logs |

**Guardrail metrics** (must not worsen):
- Overall page load time: p99 < 2s
- API error rate: < 0.1%
```

## Best Practices
1. Problem before solution — never start with "we should build X"
2. Quantify the problem — attach data to the pain (support tickets, survey results, revenue at risk)
3. Write AC before development starts — not after
4. Every metric needs a measurement method — "user satisfaction" is not a metric
5. List what's out of scope explicitly — prevents scope creep
6. Use RICE to defend prioritization decisions with data
7. Open Questions section prevents PRD from blocking engineering — keep questions visible

## Common Issues
- **PRD is too vague**: add concrete acceptance criteria with Given/When/Then format
- **Success metrics not measurable**: ensure each has a data source and baseline
- **Scope creep in implementation**: refer back to explicit out-of-scope list
- **Stakeholders misaligned on what's being built**: hold a PRD review meeting before development
