# Orchestrator Workflow Guide

Orchestrators chain multiple agents to complete an end-to-end workflow with a single command. Each orchestrator coordinates specialist agents in sequence, passing context between them.

All orchestrators use the `/orchestrators:<name>` prefix.

---

## How Orchestrators Work

When you invoke an orchestrator:
1. The first agent in the chain receives your input and produces output
2. That output is passed as context to the next agent
3. Each agent builds on the previous one's work
4. The final output is a complete, multi-perspective deliverable

You can monitor the chain via hook logs in `.claude/logs/`.

---

## `/orchestrators:prd-workflow`
**Chain:** Product Manager → Technical Architect → Scrum Master

**What it produces:**
- `docs/prd-<feature>.md` — full PRD from PM
- `docs/tdd-<feature>.md` — technical design from Technical Architect
- Updated `.claude/memory/sprint-context.md` — stories broken down by Scrum Master

**When to use:** Starting a new feature from scratch. You have a feature idea and want everything needed to hand off to engineers — requirements, design, and sprint-ready stories.

**Usage:**
```bash
/orchestrators:prd-workflow "real-time notifications with WebSockets"
/orchestrators:prd-workflow "bulk CSV import for enterprise accounts"
/orchestrators:prd-workflow "self-serve billing portal with Stripe"
```

**After this workflow — create ADO work items in bulk:**

Once the PRD and TDD are generated, run `/azuredevops:import-workitems` to bulk-create all Features, User Stories, and Tasks from both documents in one pass (no per-item confirmation):

```bash
/azuredevops:import-workitems bulk-csv-import \
  --assigned-to dev@company.com \
  --area-path "MyProject\TeamA" \
  --iteration "MyProject\Sprint 5" \
  --bundle "Q1-Release"
```

This reads `docs/prd-bulk-csv-import.md` and `docs/tdd-bulk-csv-import.md`, extracts all work items, shows you a one-time preview, then creates everything via the Python SDK.

**Real-world scenarios:**

*Scenario 1 — Customer-requested feature:*
Sales team has 5 customers asking for a CSV import. You have 20 minutes before standup.
```
/orchestrators:prd-workflow "bulk CSV import: upload user data, async processing, validation report, email when done"
```
Result: PM writes the PRD covering personas (IT admin, ops manager), acceptance criteria, success metrics. Technical Architect designs the async job queue, S3 staging, MongoDB job tracking, and API contract. Scrum Master breaks it into 8 sprint-ready stories with point estimates.

Then immediately create all ADO work items:
```
/azuredevops:import-workitems bulk-csv-import \
  --assigned-to dev@company.com --area-path "MyProject\TeamA" \
  --iteration "MyProject\Sprint 5" --bundle "Q1-Release"
```

*Scenario 2 — New product capability:*
```
/orchestrators:prd-workflow "AI-powered search using semantic embeddings across all customer content"
```

*Scenario 3 — Platform feature:*
```
/orchestrators:prd-workflow "webhook delivery system with signing, retry backoff, and delivery dashboard"
```

---

## `/orchestrators:brainstorm`
**Chain:** CTO → Product Manager → AI/ML Architect

**What it produces:**
- Strategic brief (CTO perspective — technology direction, risks, build vs buy)
- Product angle (PM perspective — user value, prioritization, go-to-market)
- Technical feasibility (AI/ML Architect — implementation approach, model selection, MLOps)
- Final recommendation synthesizing all three perspectives

**When to use:** Exploring a new strategic direction, emerging technology adoption, or AI feature before committing resources.

**Usage:**
```bash
/orchestrators:brainstorm "how should we approach AI-powered search?"
/orchestrators:brainstorm "should we build a mobile app or invest in PWA?"
/orchestrators:brainstorm "evaluating moving from MongoDB to PostgreSQL for our core data"
```

**Real-world scenarios:**

*Scenario 1 — AI feature exploration:*
Board wants to know your AI strategy before funding round.
```
/orchestrators:brainstorm "how should we approach AI-powered customer support — build, buy, or partner?"
```
Result: CTO evaluates vendor landscape (Intercom Fin, Zendesk AI, building on Claude/OpenAI), build vs buy cost matrix, strategic moat analysis. PM identifies user segments most impacted, pricing angle, adoption path. AI/ML Architect designs RAG pipeline, latency requirements, model selection rationale.

*Scenario 2 — Platform direction:*
```
/orchestrators:brainstorm "should we expose our core functionality as a public API — risks, market opportunity, and implementation approach"
```

*Scenario 3 — Technology migration:*
```
/orchestrators:brainstorm "migrating our frontend from React to Next.js — when, why, and how"
```

---

## `/orchestrators:full-sdlc`
**Chain:** Full-Stack Developer → QA Engineer → MongoDB DBA (if DB changes detected)

**What it produces:**
- Implemented feature (code changes across frontend/backend)
- Test suite (unit + integration + E2E)
- Database review (schema/index optimization if DB was touched)

**When to use:** Implementing a specific ticket or feature from start to finish, including tests and data layer review.

**Usage:**
```bash
/orchestrators:full-sdlc "PROJ-234: add bulk user import via CSV"
/orchestrators:full-sdlc "PROJ-234" --tdd docs/tdd-bulk-import.md
/orchestrators:full-sdlc "add rate limiting to the public API using Redis sliding window"
```

**Real-world scenarios:**

*Scenario 1 — Ticket from backlog:*
PROJ-234 has been in backlog 3 sprints. You have a TDD ready.
```
/orchestrators:full-sdlc "PROJ-234: bulk CSV import" --tdd docs/tdd-bulk-import.md
```
Result: Full-Stack Dev implements the React upload component, FastAPI async endpoint, S3 staging, MongoDB job collection. QA writes Playwright E2E for the upload flow and Jest unit tests for the parser. MongoDB DBA reviews the new `import_jobs` collection schema, suggests TTL index for cleanup, and adds compound index for job status queries.

*Scenario 2 — API feature:*
```
/orchestrators:full-sdlc "PROJ-189: add webhook delivery with HMAC signing and 3-retry exponential backoff"
```

*Scenario 3 — Performance improvement:*
```
/orchestrators:full-sdlc "optimize the /api/reports endpoint — currently P95 at 8 seconds, target under 500ms"
```

---

## `/orchestrators:code-review-flow`
**Chain:** Technical Architect → Security Architect → Full-Stack Developer (resolves findings)

**What it produces:**
- Architecture review (Technical Architect — design patterns, scalability, maintainability)
- Security scan (Security Architect — OWASP, auth, data handling)
- Resolved PR (Full-Stack Developer — fixes all Critical and Suggestion findings)

**When to use:** Before merging a significant PR that touches architecture, security-sensitive code, or a new service. More thorough than a single `/engineering:code-review`.

**Usage:**
```bash
/orchestrators:code-review-flow --pr 156
/orchestrators:code-review-flow --files "src/payments/**"
/orchestrators:code-review-flow --files "src/auth/" --context "new OAuth 2.0 integration"
```

**Real-world scenarios:**

*Scenario 1 — Payment feature review:*
New Stripe integration PR. Must pass security review before deploying to production.
```
/orchestrators:code-review-flow --pr 198
```
Result: Technical Architect flags two design issues (webhook handler not idempotent, missing retry logic), security audit finds PAN data logged in debug, JWT validation missing on one endpoint. Full-Stack Dev fixes all findings, adds idempotency key, removes the log statement, adds the validation. PR ready for merge.

*Scenario 2 — Auth system rewrite:*
```
/orchestrators:code-review-flow --files "src/auth/**" --context "replacing legacy session auth with JWT + refresh tokens"
```

*Scenario 3 — New microservice:*
```
/orchestrators:code-review-flow --pr 234 --context "new notification service, first standalone microservice in our stack"
```

---

## `/orchestrators:bug-fix-flow`
**Chain:** Full-Stack Developer → QA Engineer → Test Coverage Agent

**What it produces:**
- Root cause analysis and fix (Full-Stack Developer)
- Regression test (QA Engineer — targeted test for the exact bug)
- Coverage check (Test Coverage Agent — ensures the fix area meets coverage threshold)

**When to use:** Fixing a production bug where you want confidence the fix is solid, tested, and won't regress.

**Usage:**
```bash
/orchestrators:bug-fix-flow "users getting logged out randomly after 10 min"
/orchestrators:bug-fix-flow "PROJ-456: duplicate orders being created under high load"
/orchestrators:bug-fix-flow "TypeError at payments.service.ts:134 — see Sentry #89234"
```

**Real-world scenarios:**

*Scenario 1 — Critical production bug:*
Support tickets flooding in. Users can't complete checkout.
```
/orchestrators:bug-fix-flow "checkout fails with 500 error for users with promo codes — started after yesterday's deploy"
```
Result: Full-Stack Dev traces to a null pointer when `promoCode` is an empty string vs null (regression from refactor), applies minimal fix with null coalescing. QA writes regression test covering empty string, null, expired code, and valid code scenarios. Test Coverage Agent confirms checkout service is back to 84% (was 71% before).

*Scenario 2 — Race condition:*
```
/orchestrators:bug-fix-flow "race condition causing duplicate email sends — roughly 1-2% of confirmation emails are duplicated"
```

*Scenario 3 — Data corruption bug:*
```
/orchestrators:bug-fix-flow "PROJ-789: user profile images overwriting each other when two users upload simultaneously"
```

---

## `/orchestrators:deploy-flow`
**Chain:** Cloud Architect → FinOps Expert → QA Engineer

**What it produces:**
- Infrastructure validation (Cloud Architect — config check, capacity, dependencies)
- Cost impact analysis (FinOps — projected cost change from this deploy)
- Deployment execution + smoke tests (QA Engineer — deploys and validates)

**When to use:** Production deployments, especially for infrastructure changes, new services, or high-traffic periods.

**Usage:**
```bash
/orchestrators:deploy-flow api-service --env production --cloud aws
/orchestrators:deploy-flow payments-service --env production --strategy blue-green
/orchestrators:deploy-flow "new kafka cluster" --env production --cloud aws
```

**Real-world scenarios:**

*Scenario 1 — New service launch:*
Deploying a new recommendation service for the first time to production.
```
/orchestrators:deploy-flow recommendation-service --env production --cloud aws --strategy canary
```
Result: Cloud Architect validates EKS node capacity (need 3 more m5.xlarge nodes), checks IAM permissions, verifies RDS security group rules. FinOps estimates +$340/mo for the new workload, flags that Savings Plans could reduce this to $240/mo. QA deploys with 10% canary, runs smoke tests, monitors error rate for 10 minutes, then promotes to 100%.

*Scenario 2 — Infrastructure change:*
```
/orchestrators:deploy-flow "Aurora PostgreSQL cluster upgrade from 14 to 16" --env production --cloud aws
```

*Scenario 3 — High-traffic event deployment:*
```
/orchestrators:deploy-flow checkout-service --env production --context "Black Friday — peak traffic expected 10x normal" --strategy blue-green
```

---

## `/orchestrators:doc-flow`
**Chain:** Product Manager → Technical Writer → Prompt Engineer

**What it produces:**
- Content structure and narrative (PM — audience, key messages, structure)
- Written documentation (Technical Writer — full draft)
- Optimized for clarity and AI-readability (Prompt Engineer — refines for developer consumption and LLM accuracy)

**When to use:** Creating polished documentation — developer guides, product docs, API guides, or onboarding materials.

**Usage:**
```bash
/orchestrators:doc-flow "getting started guide" --type howto
/orchestrators:doc-flow "orders API" --type api
/orchestrators:doc-flow "webhook integration guide" --type howto
/orchestrators:doc-flow "system architecture overview" --type overview
```

**Real-world scenarios:**

*Scenario 1 — Developer onboarding docs:*
New developer joining next week, current README hasn't been updated in a year.
```
/orchestrators:doc-flow "developer onboarding guide for the monorepo" --type howto
```
Result: PM structures the guide around developer journey (day 1, day 3, day 7). Technical Writer writes prerequisites, setup steps, first PR walkthrough, local services guide, troubleshooting section. Prompt Engineer optimizes section headers, adds code blocks, ensures consistency, and structures it for Claude/Copilot to reference accurately.

*Scenario 2 — Public API documentation:*
```
/orchestrators:doc-flow "REST API reference for external developers" --type api
```

*Scenario 3 — Architecture overview for new team members:*
```
/orchestrators:doc-flow "how the notification system works" --type overview --audience "new backend engineers"
```

---

## `/orchestrators:sprint-workflow`
**Chain:** Scrum Master → Engineering Manager → Product Manager

**What it produces:**
- Sprint ceremony plan (Scrum Master — planning structure, retro format, health metrics)
- Capacity and resource plan (Engineering Manager — team capacity, allocations, risk)
- Committed sprint backlog (Product Manager — prioritized stories with acceptance criteria)
- Updated `.claude/memory/sprint-context.md`

**When to use:** Sprint kickoff. Run this at the start of each sprint to get a complete, committed plan that all three stakeholder perspectives agree on.

**Usage:**
```bash
/orchestrators:sprint-workflow --sprint "Sprint 15" --capacity 45
/orchestrators:sprint-workflow --sprint "Sprint 15" --capacity 45 --goal "launch payments v2"
/orchestrators:sprint-workflow --sprint "Sprint 15" --capacity 32 --carry-over "PROJ-234, PROJ-235"
```

**Real-world scenarios:**

*Scenario 1 — Standard sprint kickoff:*
Monday morning. 5 engineers, 2-week sprint, goal is to ship the billing portal.
```
/orchestrators:sprint-workflow --sprint "Sprint 22" --capacity 45 --goal "self-serve billing portal MVP"
```
Result: Scrum Master designs the planning agenda (2hr session), defines sprint health metrics to track, sets retro format for end of sprint. Engineering Manager calculates capacity (42 effective points after meetings/review overhead), notes one engineer is ramping on the billing domain (20% discount), identifies cross-team dependency on the payments API team. PM prioritizes backlog: 7 billing stories committed (38pts), 3 stretch stories (12pts), acceptance criteria confirmed with stakeholders, success metric defined.

*Scenario 2 — Sprint with carry-over:*
```
/orchestrators:sprint-workflow --sprint "Sprint 23" --capacity 40 --carry-over "PROJ-289, PROJ-290" --focus "complete billing portal and start analytics"
```

*Scenario 3 — Reduced team sprint:*
```
/orchestrators:sprint-workflow --sprint "Sprint 24" --capacity 28 --context "2 engineers on PTO, 1 new hire onboarding"
```

---

## Orchestrator Quick Reference

| Workflow | Command | When to Use | Time |
|----------|---------|-------------|------|
| New feature planning | `/orchestrators:prd-workflow` | Have a feature idea, need PRD + TDD + stories | ~10 min |
| Strategic exploration | `/orchestrators:brainstorm` | Big decision, new technology, need multi-perspective analysis | ~8 min |
| Feature implementation | `/orchestrators:full-sdlc` | Have a ticket/TDD, need it built + tested | ~15 min |
| Thorough code review | `/orchestrators:code-review-flow` | Significant PR, needs arch + security + fixes | ~10 min |
| Production bug | `/orchestrators:bug-fix-flow` | Confirmed bug, need fix + test + coverage check | ~8 min |
| Production deployment | `/orchestrators:deploy-flow` | Deploying to prod, want infra + cost + smoke test | ~10 min |
| Polished documentation | `/orchestrators:doc-flow` | Need complete, audience-appropriate docs | ~8 min |
| Sprint start | `/orchestrators:sprint-workflow` | Monday of new sprint, need committed plan | ~10 min |
| ADO bulk import (from docs) | `/azuredevops:import-workitems` | After prd-workflow, create all ADO work items at once | ~2 min |
| ADO bulk import (ad-hoc) | `/azuredevops:import-workitems --adhoc` | Describe features/stories/tasks conversationally | ~2 min |

---

## Chaining Orchestrators

Orchestrators compose well. Common sequences:

**Full feature lifecycle (with ADO work items):**
```
/orchestrators:brainstorm "AI-powered search"           # → strategic decision
/orchestrators:prd-workflow "semantic search MVP"       # → PRD + TDD + stories
/azuredevops:import-workitems semantic-search-mvp \     # → all Features/Stories/Tasks in ADO
  --assigned-to dev@company.com \
  --area-path "MyProject\Search" \
  --iteration "MyProject\Sprint 8" \
  --bundle "Q2-Release"
/orchestrators:full-sdlc "PROJ-301: search indexer"    # → implementation + tests
/orchestrators:code-review-flow --pr 301                # → review + security + fixes
/orchestrators:deploy-flow search-service --env prod    # → deploy + cost + smoke tests
```

**Bug to resolution:**
```
/orchestrators:bug-fix-flow "duplicate orders bug"   # → fix + regression test
/orchestrators:code-review-flow --files "src/orders" # → verify fix quality
/orchestrators:deploy-flow orders-service --env prod  # → safe deploy
```

**Sprint kickoff with ADO sync:**
```
/orchestrators:sprint-workflow --sprint "Sprint 15" --capacity 45   # → committed sprint plan
/azuredevops:import-workitems --adhoc \                              # → create any missing items
  --assigned-to dev@company.com \
  --area-path "MyProject\TeamA" \
  --iteration "MyProject\Sprint 15" \
  --bundle "Q2-Release"
/azuredevops:sprint-status --sprint "MyProject\Sprint 15"           # → verify items landed correctly
```
