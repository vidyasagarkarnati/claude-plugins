# Command Reference

Detailed usage guide for all 12 slash commands. Each command is namespaced by plugin — use `/plugin:command` syntax in Claude Code.

---

## Leadership Plugin Commands

### `/leadership:create-prd`
**Plugin:** leadership | **Argument:** `<feature-name-or-description>`

Creates a full Product Requirements Document saved to `docs/prd-<name>.md`. Covers problem statement, personas, user stories (INVEST format), acceptance criteria (BDD), success metrics, and phased timeline.

**Usage:**
```bash
/leadership:create-prd "user notifications with email and push"
/leadership:create-prd "bulk CSV import for enterprise accounts"
/leadership:create-prd "real-time dashboard with WebSocket updates"
```

**Real-world scenarios:**

*Scenario 1 — New feature from sales request:*
Your sales team keeps losing deals because enterprise customers can't bulk-import users. You have rough notes from 3 customer calls.
```
/leadership:create-prd "bulk user import via CSV for enterprise accounts — max 5000 rows, async processing, email notification, validation report download"
```
Output: `docs/prd-bulk-user-import.md` with problem statement, personas (IT admin, ops manager), user stories, acceptance criteria including error handling, success metric (enterprise activation rate +15%).

*Scenario 2 — Product-led growth feature:*
```
/leadership:create-prd "free tier to paid upgrade flow with in-app prompts and self-serve checkout"
```

*Scenario 3 — Technical feature for developers:*
```
/leadership:create-prd "webhook delivery system with retry, signing, and delivery dashboard"
```

**Output sections:**
1. Problem Statement
2. Target Personas
3. Solution Overview (with alternatives considered)
4. User Stories (grouped by epic)
5. Acceptance Criteria (Given/When/Then)
6. Non-functional Requirements
7. Success Metrics (3-5 KPIs with baselines)
8. Dependencies & Risks
9. Phased Timeline

---

### `/leadership:sprint-planning`
**Plugin:** leadership | **Argument:** `--sprint "<name>" --capacity <points>`

Runs a full sprint planning session: pulls stories from backlog context, estimates, checks capacity, assigns to engineers, and writes the committed plan to `.claude/memory/sprint-context.md`.

**Usage:**
```bash
/leadership:sprint-planning --sprint "Sprint 15" --capacity 40
/leadership:sprint-planning --sprint "Sprint 15" --capacity 40 --focus "payments migration"
/leadership:sprint-planning --sprint "Sprint 15" --capacity 32 --team 4
```

**Real-world scenarios:**

*Scenario 1 — Standard sprint:*
Monday planning meeting, 5 engineers, 2-week sprint, 40 story points capacity.
```
/leadership:sprint-planning --sprint "Sprint 15" --capacity 40
```
Output: Committed sprint plan with stories prioritized by value, estimated, assigned, with capacity buffer noted. Saved to sprint-context.md.

*Scenario 2 — Reduced capacity sprint:*
Two engineers on PTO, critical deadline for payments launch.
```
/leadership:sprint-planning --sprint "Sprint 16" --capacity 24 --focus "payments v2 launch"
```

*Scenario 3 — Sprint with carry-over:*
Previous sprint had 12 points of carry-over from the auth refactor.
```
/leadership:sprint-planning --sprint "Sprint 17" --capacity 40 --carry-over "AUTH-45, AUTH-46"
```

**Output:** Committed sprint plan with: goal statement, story list (with points and assignees), capacity analysis, risks, definition of done.

---

## Architecture Plugin Commands

### `/architecture:create-tdd`
**Plugin:** architecture | **Argument:** `<feature-or-system-name> [--prd <path>]`

Creates a Technical Design Document saved to `docs/tdd-<name>.md`. Covers system design, component breakdown, data models, API contracts, non-functional requirements, and implementation phases.

**Usage:**
```bash
/architecture:create-tdd "real-time notification system"
/architecture:create-tdd "CSV import feature" --prd docs/prd-csv-import.md
/architecture:create-tdd "payment processing service" --prd docs/prd-payments.md
```

**Real-world scenarios:**

*Scenario 1 — New service design:*
```
/architecture:create-tdd "event-driven order processing service" --prd docs/prd-order-processing.md
```
Output: TDD with system context diagram, component design (order service, event bus, inventory service, notification service), MongoDB schemas, event contracts, API endpoints, scalability plan (sharding strategy at 10M orders), and 4-week implementation phases.

*Scenario 2 — Infrastructure feature:*
```
/architecture:create-tdd "multi-region active-active deployment on AWS"
```

*Scenario 3 — Platform capability:*
```
/architecture:create-tdd "internal feature flag service with per-tenant targeting"
```

**Output sections:** System Context, Architecture Decision, Component Design, Data Models, API Contracts, NFRs (latency/throughput/availability), Security Considerations, Implementation Phases, Open Questions.

---

### `/architecture:threat-model`
**Plugin:** architecture | **Argument:** `<system-or-feature-description>`

Produces a STRIDE threat model with identified threats, risk scores (DREAD), mitigations, and a security checklist.

**Usage:**
```bash
/architecture:threat-model "user authentication and session management"
/architecture:threat-model "payment checkout flow including Stripe integration"
/architecture:threat-model "file upload system storing user documents in S3"
```

**Real-world scenarios:**

*Scenario 1 — Pre-launch security review:*
Launching a new payments feature next week. Security review required.
```
/architecture:threat-model "checkout flow: React form → Node.js API → Stripe → order DB → email confirmation"
```
Output: Data flow diagram, 12 identified threats across STRIDE categories (e.g., Spoofing: JWT token theft; Tampering: price manipulation; Repudiation: missing audit log), DREAD scores, mitigations (CSRF tokens, idempotency keys, signed webhooks), and pre-launch checklist.

*Scenario 2 — New data integration:*
```
/architecture:threat-model "third-party CRM integration with bidirectional user data sync"
```

*Scenario 3 — Infrastructure change:*
```
/architecture:threat-model "public API with API key authentication and rate limiting"
```

---

### `/architecture:update-architecture-docs`
**Plugin:** architecture | **Argument:** `[--create-adrs] [--output-report] [--path <dir>]`

Scans your codebase against existing architecture docs, detects drift, generates missing ADRs, and produces an update report.

**Usage:**
```bash
/architecture:update-architecture-docs
/architecture:update-architecture-docs --create-adrs
/architecture:update-architecture-docs --create-adrs --output-report
/architecture:update-architecture-docs --path docs/architecture/
```

**Real-world scenarios:**

*Scenario 1 — Post-migration cleanup:*
You migrated from REST to GraphQL 2 months ago but docs still say REST everywhere.
```
/architecture:update-architecture-docs --create-adrs --output-report
```
Output: Report listing stale docs (5 files with REST references), auto-generated ADR-015 "Migration from REST to GraphQL", ADR-016 "Adoption of Apollo Client for state management", and a diff of proposed doc updates.

*Scenario 2 — Quarterly doc audit:*
```
/architecture:update-architecture-docs --output-report --path docs/
```

*Scenario 3 — New team member onboarding prep:*
```
/architecture:update-architecture-docs --create-adrs
```

---

## Cloud Plugin Commands

### `/cloud:cost-estimate`
**Plugin:** cloud | **Argument:** `<infrastructure-description> [--cloud aws|azure|gcp]`

Produces a detailed cloud cost estimate with service breakdown, monthly projection, cost optimization options, and RI/Savings Plan recommendations.

**Usage:**
```bash
/cloud:cost-estimate "3-tier web app with RDS and EKS" --cloud aws
/cloud:cost-estimate "microservices platform: 10 services on EKS, Aurora PostgreSQL, ElastiCache" --cloud aws
/cloud:cost-estimate "data pipeline: Cloud Run jobs, BigQuery, Cloud Storage" --cloud gcp
```

**Real-world scenarios:**

*Scenario 1 — Pre-launch budgeting:*
CTO needs a cloud budget for next fiscal year. New product launching in Q2.
```
/cloud:cost-estimate "SaaS platform: EKS (10 nodes m5.xlarge), Aurora PostgreSQL Multi-AZ, ElastiCache r6g.large, ALB, CloudFront, S3 — supporting 10k active users" --cloud aws
```
Output: Line-item monthly estimate (~$4,200/mo), breakdown by service, 1-year vs 3-year RI savings ($1,100/mo savings), Savings Plans recommendation, spot instance opportunities for non-prod.

*Scenario 2 — Cost comparison for cloud choice:*
```
/cloud:cost-estimate "Kubernetes cluster: 6 nodes, managed PostgreSQL, Redis, CDN — compare AWS vs GCP vs Azure"
```

*Scenario 3 — Scaling projection:*
```
/cloud:cost-estimate "current stack at 10x scale: what does our AWS bill look like at 100k users vs current 10k?"
```

---

### `/cloud:deploy`
**Plugin:** cloud | **Argument:** `<service-name> --env <environment> [--strategy rolling|blue-green|canary]`

Executes a deployment: pre-flight checks, health validation, deploy with chosen strategy, smoke tests, rollback plan on failure.

**Usage:**
```bash
/cloud:deploy order-service --env staging --strategy rolling
/cloud:deploy payments-api --env production --strategy blue-green
/cloud:deploy frontend --env production --strategy canary --canary-weight 10
```

**Real-world scenarios:**

*Scenario 1 — Standard staging deploy:*
```
/cloud:deploy api-service --env staging --strategy rolling
```
Output: Pre-flight checklist (Docker image exists, DB migrations validated, config secrets present), rolling deploy to EKS, health check results, smoke test suite run, deployment summary.

*Scenario 2 — Zero-downtime production release:*
Database schema change + app deploy must be coordinated.
```
/cloud:deploy payments-service --env production --strategy blue-green --pre-deploy "run migration script"
```

*Scenario 3 — Canary release for risky change:*
```
/cloud:deploy recommendation-engine --env production --strategy canary --canary-weight 5 --success-metric "error_rate < 0.1%"
```

**Safety checks:** Image digest verification, replica readiness, connection drain, automatic rollback on health check failure.

---

## Engineering Plugin Commands

### `/engineering:code-review`
**Plugin:** engineering | **Argument:** `[--pr <number>] [--files <glob>] [--focus security|performance|style]`

Multi-layer code review: correctness, security (OWASP lens), performance, test coverage, and style. Produces structured findings with severity levels.

**Usage:**
```bash
/engineering:code-review --pr 142
/engineering:code-review --files "src/auth/**"
/engineering:code-review --files "src/payments/**" --focus security
/engineering:code-review  # reviews staged git changes
```

**Real-world scenarios:**

*Scenario 1 — PR review before merge:*
```
/engineering:code-review --pr 156
```
Output: Scope summary (8 files changed, auth refactor + new endpoint), Critical findings (JWT not validated on one path), Suggestions (N+1 query in user fetch, missing index), Nits (inconsistent error handling style), Security findings (token logged in debug statement), Coverage gaps (new endpoint has 0 tests).

*Scenario 2 — Security-focused review of payments code:*
```
/engineering:code-review --files "src/payments/**" --focus security
```
Output: Deep OWASP analysis — injection risks, input validation gaps, PCI-DSS relevant findings, auth bypass vectors.

*Scenario 3 — Pre-commit review of staged changes:*
```
/engineering:code-review
```

**Finding severities:** Critical (block merge), Suggestion (should fix), Nit (optional improvement).

---

### `/engineering:bug-fix`
**Plugin:** engineering | **Argument:** `<bug-description-or-error-message>`

End-to-end bug resolution: reproduce → root cause analysis → minimal fix → regression test → documentation.

**Usage:**
```bash
/engineering:bug-fix "TypeError: Cannot read property 'id' of undefined at orders.js:47"
/engineering:bug-fix "users are getting logged out randomly after about 10 minutes"
/engineering:bug-fix "PROJ-234: payment confirmation emails not sending in production"
```

**Real-world scenarios:**

*Scenario 1 — Production error from Sentry:*
```
/engineering:bug-fix "TypeError: Cannot read properties of undefined (reading 'stripeCustomerId') at checkout.service.ts:134 — happens for users who registered before 2024-01-15"
```
Output: Root cause (users before Jan 15 have `stripeCustomerId` as `null` not `undefined`, defensive check missing), fix (null check + migration script for existing nulls), regression test, PR description.

*Scenario 2 — Intermittent issue:*
```
/engineering:bug-fix "race condition in order processing — duplicate orders appear roughly 1 in 200 times under high load"
```
Output: Root cause (missing idempotency key on the retry path), fix (MongoDB upsert with idempotency key), load test to verify, regression test.

*Scenario 3 — Bug from user report:*
```
/engineering:bug-fix "PROJ-456: CSV export shows wrong date format for EU users — should be DD/MM/YYYY but showing MM/DD/YYYY"
```

---

### `/engineering:release-notes`
**Plugin:** engineering | **Argument:** `[--from <tag>] [--to <ref>] [--format slack|github|markdown]`

Generates release notes from git log. Groups by feature/fix/chore, writes for target audience, formats for the target platform.

**Usage:**
```bash
/engineering:release-notes --from v1.3.0 --to HEAD --format github
/engineering:release-notes --from v1.3.0 --to HEAD --format slack
/engineering:release-notes --from v2.0.0 --to v2.1.0 --format markdown --audience customers
```

**Real-world scenarios:**

*Scenario 1 — GitHub release:*
```
/engineering:release-notes --from v2.2.0 --to HEAD --format github
```
Output: GitHub-formatted release with `## What's New`, `## Bug Fixes`, `## Performance`, `## Breaking Changes` sections, each with linked commits and PR numbers.

*Scenario 2 — Slack announcement to engineering team:*
```
/engineering:release-notes --from v2.2.0 --to HEAD --format slack
```
Output: Slack-formatted message with emoji, bullet points, @mentions for key contributors.

*Scenario 3 — Customer-facing changelog:*
```
/engineering:release-notes --from v2.2.0 --to HEAD --audience customers --format markdown
```
Output: Non-technical language, benefits-focused, no internal implementation details.

---

### `/engineering:document`
**Plugin:** engineering | **Argument:** `--type api|howto|readme|runbook --path <file-or-dir>`

Generates documentation for the specified path. API docs use OpenAPI format. HOWTOs and runbooks follow structured templates.

**Usage:**
```bash
/engineering:document --type api --path src/routes/orders.ts
/engineering:document --type howto --path src/auth/
/engineering:document --type readme --path services/payment-service/
/engineering:document --type runbook --path ops/incident-response/
```

**Real-world scenarios:**

*Scenario 1 — API documentation:*
New REST API endpoint added last sprint, no docs.
```
/engineering:document --type api --path src/routes/orders.ts
```
Output: OpenAPI 3.0 YAML for all endpoints in the file — `GET /orders`, `POST /orders`, `GET /orders/{id}`, `PATCH /orders/{id}/cancel` — with request/response schemas, auth requirements, error codes, and curl examples.

*Scenario 2 — Developer HOWTO:*
```
/engineering:document --type howto --path src/auth/
```
Output: Structured HOWTO — "How to authenticate API requests" — covering: getting an API key, making authenticated requests, token refresh, error handling, code examples in 3 languages.

*Scenario 3 — Ops runbook:*
```
/engineering:document --type runbook --path src/workers/email-processor/
```
Output: On-call runbook — purpose, normal behavior, alert conditions, diagnostic steps, remediation procedures, escalation path.

---

### `/engineering:coverage-audit`
**Plugin:** engineering | **Argument:** `[--threshold <pct>] [--path <dir>] [--framework jest|pytest|go]`

Runs coverage tools, identifies gaps below threshold, prioritizes by risk/complexity, generates tests for uncovered paths.

**Usage:**
```bash
/engineering:coverage-audit --threshold 80 --path src/
/engineering:coverage-audit --threshold 75 --path src/payments/ --framework jest
/engineering:coverage-audit --threshold 80 --path . --framework pytest
```

**Real-world scenarios:**

*Scenario 1 — Pre-release audit:*
Preparing for v2.0 release. Team agreed on 80% coverage requirement.
```
/engineering:coverage-audit --threshold 80 --path src/
```
Output: Coverage report showing 12 files below 80%, ranked by: business criticality (payments files flagged highest), coverage delta (files that regressed since last sprint), complexity score. Generates tests for the top 5 highest-priority gaps. CI configuration update to enforce threshold.

*Scenario 2 — New feature coverage check:*
```
/engineering:coverage-audit --threshold 90 --path src/checkout/ --framework jest
```
Output: Checkout module at 67%, generates 8 Jest tests covering: validation edge cases, error paths, async failure scenarios.

*Scenario 3 — Python backend audit:*
```
/engineering:coverage-audit --threshold 80 --path app/ --framework pytest
```

**Output:** Coverage summary table, files-below-threshold list with priority scores, generated test files, CI config snippet.

---

## Quick Reference

| Command | Plugin | What it produces |
|---------|--------|-----------------|
| `/leadership:create-prd` | leadership | `docs/prd-*.md` with 9 sections |
| `/leadership:sprint-planning` | leadership | Updated `sprint-context.md` |
| `/architecture:create-tdd` | architecture | `docs/tdd-*.md` with system design |
| `/architecture:threat-model` | architecture | STRIDE report with DREAD scores |
| `/architecture:update-architecture-docs` | architecture | Stale doc report + ADRs |
| `/cloud:cost-estimate` | cloud | Line-item cost breakdown + RI recommendations |
| `/cloud:deploy` | cloud | Deploy execution + health report |
| `/engineering:code-review` | engineering | Structured findings (Critical/Suggestion/Nit) |
| `/engineering:bug-fix` | engineering | Root cause + fix + regression test |
| `/engineering:release-notes` | engineering | Formatted release notes |
| `/engineering:document` | engineering | API docs / HOWTO / README / runbook |
| `/engineering:coverage-audit` | engineering | Coverage report + generated tests |
