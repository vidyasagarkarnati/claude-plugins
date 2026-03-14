# Agent Usage Guide

Real-world use cases for all 25 agents. Agents activate automatically based on your prompt, or invoke them explicitly with `Use the <agent-name> agent to...`.

---

## Leadership Plugin

### CTO
**Model:** Opus | **Plugin:** `leadership`

The CTO is your senior technology executive. Best for strategic, org-level, or forward-looking technology decisions. Not for implementation — for direction.

**When to use:**
- Making a build vs. buy decision
- Evaluating whether to adopt a new technology (AI, edge compute, new cloud service)
- Defining engineering values and career ladders
- Setting architectural governance policies
- Preparing board-level technology updates

**Real-world examples:**
```
"Should we build our own auth system or use Auth0? We have 3 engineers and need SOC2."

"We're evaluating migrating from REST to GraphQL. Give me a build vs keep analysis with risks and a recommendation."

"Write a 3-year technology roadmap for a B2B SaaS company moving from monolith to microservices."

"Our team ships slowly. Do a DORA metrics diagnosis and recommend interventions."

"Draft a tech due diligence checklist for acquiring a 20-person startup with a Python/React stack."
```

---

### VP of Engineering
**Model:** Opus | **Plugin:** `leadership`

Engineering excellence, team health, and delivery velocity. Use for organizational engineering concerns and cross-team quality standards.

**When to use:**
- Engineering process improvements (CI/CD maturity, deployment frequency)
- Team structure and topology decisions
- Engineering hiring and leveling
- DORA metrics analysis and improvement
- Engineering culture initiatives

**Real-world examples:**
```
"Our deployment frequency is once per week. What practices can get us to daily?"

"Design an engineering leveling matrix from L1 to L7 for a 40-person eng team."

"We have a 70% test coverage requirement but teams are gaming it. How do we fix this?"

"Create an onboarding plan for a new senior backend engineer joining next week."

"Our mean time to restore after incidents is 4 hours. What does a good incident response process look like?"
```

---

### Director of Engineering
**Model:** Sonnet | **Plugin:** `leadership`

Cross-team coordination, roadmap execution, and escalation handling. Use when work involves multiple teams or requires alignment across domains.

**When to use:**
- Coordinating a feature that spans frontend, backend, and infra teams
- Managing dependencies between parallel workstreams
- Escalating blockers that cross team boundaries
- Creating quarterly engineering roadmaps
- Stakeholder status reporting

**Real-world examples:**
```
"We have 3 teams working on a shared payments feature. Create a dependency matrix and coordination plan."

"Draft a Q3 engineering roadmap covering platform stability, feature delivery, and tech debt reduction."

"The mobile team is blocked on the API team for 2 weeks. Write an escalation memo with proposed resolution."

"Create a program plan for migrating from MongoDB 4.4 to 7.0 across 6 services with zero downtime."
```

---

### Engineering Manager
**Model:** Haiku | **Plugin:** `leadership`

Day-to-day team management: sprint health, capacity planning, and blocker removal. Fast and practical.

**When to use:**
- Sprint planning and estimation
- Capacity planning for a team
- Identifying and removing blockers
- 1:1 prep and performance feedback
- Standups and retrospective facilitation

**Real-world examples:**
```
"Our sprint has 42 story points but we've historically delivered 30. Help me re-scope."

"Two engineers are out next sprint. Recalculate our capacity and adjust the sprint backlog."

"Write a performance improvement plan for an engineer who misses deadlines regularly."

"Generate retro questions for a sprint where we missed the goal due to scope creep."

"We have a dependency on the platform team. Draft a blocker report for the weekly stakeholder meeting."
```

---

### Product Manager
**Model:** Sonnet | **Plugin:** `leadership`

PRDs, user stories, prioritization, and product strategy. Use when you need product artifacts or stakeholder alignment on requirements.

**When to use:**
- Writing a PRD for a new feature
- Creating user stories from requirements
- Prioritizing a feature backlog
- Defining success metrics for a launch
- Writing acceptance criteria

**Real-world examples:**
```
"Write a PRD for a CSV bulk import feature for enterprise users. Max 1000 rows, async processing, email notification."

"We have 12 feature requests from customers. Score them using RICE and produce a prioritized list."

"Turn these 5 Slack messages from the sales team into properly formatted user stories with acceptance criteria."

"Define success metrics for our new onboarding flow. Current activation rate is 34%."

"A customer wants custom report exports. Write the acceptance criteria in BDD Given/When/Then format."
```

---

### Scrum Master
**Model:** Haiku | **Plugin:** `leadership`

Agile ceremonies, process health, and team rituals. Quick output for sprint ceremonies.

**When to use:**
- Running retrospectives
- Facilitating sprint planning
- Tracking sprint health metrics
- Writing team working agreements
- Identifying and addressing agile anti-patterns

**Real-world examples:**
```
"Run a 4Ls retrospective (Liked, Learned, Lacked, Longed For) for our sprint where we delivered 85% of points."

"Create a sprint planning agenda for a 2-week sprint with a team of 6 engineers."

"Write a team working agreement covering: core hours, PR review SLAs, definition of done, meeting norms."

"We keep having 'zombie' stories that carry over every sprint. Diagnose the root cause and suggest fixes."

"Generate 5 sprint health metrics we should track and how to visualize them in Jira."
```

---

## Architecture Plugin

### Technical Architect
**Model:** Opus | **Plugin:** `architecture`

System design authority. Use for any architectural decision, new system design, or technical specification that will have long-term impact.

**When to use:**
- Designing a new service or system
- Choosing between architectural patterns (monolith vs microservices, event-driven vs sync)
- Creating Technical Design Documents (TDDs)
- API design and versioning strategy
- Database selection and schema design
- Reviewing architecture for scalability

**Real-world examples:**
```
"Design a real-time notification system supporting 100k concurrent users. Include WebSocket, event bus, and fallback to polling."

"We're splitting our monolith. Design the strangler fig migration strategy for the orders domain."

"Create a C4 architecture diagram for our SaaS platform (React frontend, FastAPI backend, MongoDB, Redis, deployed on AWS EKS)."

"Choose between Kafka, SQS, and RabbitMQ for our event pipeline processing 50k events/sec."

"Design a multi-tenant data isolation strategy for a B2B SaaS where tenants require strict data separation."

"Review this API design for our payments service and flag any versioning, idempotency, or security gaps."
```

---

### Security Architect
**Model:** Opus | **Plugin:** `architecture`

Threat modeling, security architecture, and compliance. Use for anything touching auth, data security, external APIs, or regulatory requirements.

**When to use:**
- Threat modeling a new feature or system
- Designing authentication and authorization systems
- Reviewing code for security vulnerabilities
- Meeting compliance requirements (SOC2, GDPR, HIPAA, PCI-DSS)
- Designing secrets management
- Zero-trust architecture

**Real-world examples:**
```
"Run a STRIDE threat model on our payment checkout flow: React frontend → Node.js API → Stripe → MongoDB."

"Design an OAuth 2.0 + OIDC authentication system with refresh token rotation for our mobile app."

"We're storing PII (name, email, DOB). What encryption, access controls, and audit logging do we need for GDPR compliance?"

"Review this JWT implementation for security issues: [paste code]"

"Design a secrets management strategy using AWS Secrets Manager for 12 microservices with secret rotation."

"We're preparing for SOC 2 Type II. Give me a 90-day readiness checklist."
```

---

### Data Architect
**Model:** Sonnet | **Plugin:** `architecture`

Data modeling, pipelines, and governance. Use when designing how data flows, is stored, or is processed at scale.

**When to use:**
- Designing data models for new domains
- Building ETL/ELT pipelines
- Data governance and lineage
- Analytical vs operational data strategy
- Data warehouse or data lake design

**Real-world examples:**
```
"Design a MongoDB schema for an e-commerce platform with products, variants, inventory, and orders. Optimize for reads."

"We need to sync our MongoDB operational data to BigQuery for analytics. Design the CDC pipeline."

"Our data team needs a data catalog. Design the metadata model and governance process."

"Design a data lake architecture on S3 for storing 10TB/day of clickstream events with Athena querying."

"We have 5 microservices each with their own DB. How do we build cross-service reporting without a god schema?"
```

---

### AI/ML Architect
**Model:** Sonnet | **Plugin:** `architecture`

ML system design, LLM integration, RAG pipelines, and MLOps. Use when building AI-powered features or production ML systems.

**When to use:**
- Designing RAG (Retrieval Augmented Generation) pipelines
- Selecting models and embedding strategies
- MLOps pipeline design (training, evaluation, deployment)
- LLM prompt engineering architecture
- Feature stores and ML infrastructure

**Real-world examples:**
```
"Design a RAG pipeline for a customer support chatbot. We have 50k support articles in Markdown. Use Claude as the LLM."

"Compare fine-tuning vs RAG vs prompt engineering for our use case: classifying customer feedback into 20 categories."

"Design an MLOps pipeline for a fraud detection model: training on Spark, serving on SageMaker, monitoring drift."

"We want to add AI search to our SaaS product. Design the embedding strategy, vector DB choice, and reranking layer."

"Create a model evaluation framework for our LLM-powered features with automatic regression testing on prompt changes."
```

---

### Architecture Docs Agent
**Model:** Sonnet | **Plugin:** `architecture`

Audits architecture documentation for staleness and drift. Use to keep your docs honest and generate ADRs.

**When to use:**
- Detecting drift between docs and actual code
- Generating ADRs for undocumented decisions
- Auditing README and architecture docs after a major change
- Creating a documentation health report

**Real-world examples:**
```
"Scan our /docs folder and flag any architecture docs that describe patterns we no longer use."

"We migrated from REST to GraphQL 3 months ago but the docs still say REST. Find and list all stale references."

"Generate ADRs for the 5 most significant architectural decisions in our codebase based on git history."

"Create a documentation health report: what's current, what's stale, what's missing entirely."
```

---

## Cloud Plugin

### AWS Cloud Architect
**Model:** Sonnet | **Plugin:** `cloud`

AWS infrastructure design, IaC, cost optimization. Use for any AWS-specific infrastructure work.

**When to use:**
- Designing AWS architecture for a new service
- Writing CloudFormation or CDK
- EKS cluster design
- Multi-account AWS Organizations strategy
- Cost optimization and right-sizing
- Well-Architected Framework reviews

**Real-world examples:**
```
"Design a multi-account AWS architecture for a startup: prod, staging, dev, shared services accounts with Control Tower."

"Write CDK TypeScript for an EKS cluster with IRSA, Karpenter autoscaling, and private endpoint."

"Our AWS bill is $45k/month. Run a cost optimization analysis and give me the top 5 savings opportunities."

"Design VPC architecture for 3 environments (prod/staging/dev) with Transit Gateway for cross-VPC traffic."

"We need to pass SOC 2 on AWS. Configure Config rules, GuardDuty, Security Hub, and CloudTrail for compliance."

"Our Lambda cold starts are 3 seconds. Diagnose and fix the performance issue."
```

---

### Azure Cloud Architect
**Model:** Sonnet | **Plugin:** `cloud`

Azure infrastructure, AKS, Bicep/Terraform, Entra ID. Use for Azure-specific work.

**When to use:**
- Azure landing zone design
- AKS cluster setup and governance
- Bicep or Terraform for Azure resources
- Entra ID (Azure AD) and RBAC design
- Azure cost management
- Azure DevOps integration

**Real-world examples:**
```
"Design an Azure landing zone with Management Groups for prod/non-prod, Hub-Spoke networking, and Azure Policy guardrails."

"Write Bicep for an AKS cluster with Workload Identity, Azure CNI, and Calico network policies."

"We're using Azure SQL Managed Instance. Design the high availability and disaster recovery configuration."

"Our Entra ID has 200 apps. Design a Conditional Access policy framework for Zero Trust."

"Our Azure spend jumped 40% last month. Identify the top cost drivers using Cost Management and suggest fixes."
```

---

### GCP Cloud Architect
**Model:** Sonnet | **Plugin:** `cloud`

GCP infrastructure, GKE, BigQuery, Workload Identity. Use for GCP-specific work.

**When to use:**
- GCP project and folder hierarchy design
- GKE cluster architecture
- BigQuery optimization and governance
- Workload Identity configuration
- VPC Service Controls for data security
- GCP cost optimization

**Real-world examples:**
```
"Design a GCP organization hierarchy with folders for business units and environments, with Org Policy constraints."

"Write Terraform for a private GKE cluster with Workload Identity, Binary Authorization, and GKE Autopilot."

"Our BigQuery costs are $8k/month. Audit our queries for full-table scans and design a partition/cluster strategy."

"Configure VPC Service Controls to prevent data exfiltration from our BigQuery and Cloud Storage in the prod project."

"Set up Cloud Armor WAF policies to block OWASP Top 10 attacks on our external Application Load Balancer."
```

---

### OCI Cloud Architect
**Model:** Sonnet | **Plugin:** `cloud`

Oracle Cloud Infrastructure, OKE, Autonomous Database, compartments. Use for OCI-specific work.

**When to use:**
- OCI compartment hierarchy design
- OKE (Oracle Kubernetes Engine) setup
- Autonomous Database configuration
- OCI IAM policies
- Cost management with budgets

**Real-world examples:**
```
"Design an OCI compartment hierarchy for a financial services company: prod, non-prod, networking, and security compartments."

"Write Terraform for an OKE cluster in OCI with VM.Standard.E4.Flex nodes, private API endpoint, and node pool autoscaling."

"We're migrating from AWS RDS PostgreSQL to OCI Autonomous Database. What's the migration path and compatibility gaps?"

"Configure OCI IAM policies for: developers (manage compute in dev), DBAs (manage database in prod), and read-only auditors."
```

---

## Engineering Plugin

### Full-Stack Developer
**Model:** Sonnet | **Plugin:** `engineering`

End-to-end implementation: React frontends, Node.js/FastAPI backends, Docker, CI/CD. Use for building features.

**When to use:**
- Building a new feature end-to-end
- Writing React components or pages
- Building REST or GraphQL APIs
- Docker and CI/CD configuration
- Performance optimization
- Code review

**Real-world examples:**
```
"Build a CSV bulk import feature: React drag-and-drop upload, FastAPI async processing endpoint, MongoDB job tracking, email notification on completion."

"Create a React dashboard with real-time WebSocket updates showing order status. Use React Query for state management."

"Write a FastAPI middleware that logs all requests with user ID, endpoint, latency, and response status to structured JSON."

"Our React app bundle is 4.2MB. Analyze and implement code splitting, lazy loading, and tree shaking to get it under 1.5MB."

"Write a GitHub Actions CI pipeline: lint → test → build → Docker push → deploy to EKS on merge to main."

"Add rate limiting (100 req/min per API key) to our Express.js API using Redis sliding window."
```

---

### QA Engineer
**Model:** Haiku | **Plugin:** `engineering`

Test strategy, Playwright E2E, Jest unit tests, automation. Use for test writing and QA process.

**When to use:**
- Writing E2E tests with Playwright
- Setting up Jest test suites
- Designing test strategies for a feature
- API testing with Supertest or similar
- Performance and load testing setup

**Real-world examples:**
```
"Write Playwright E2E tests for our checkout flow: add to cart → enter shipping → payment → order confirmation."

"Create a Jest test suite for our UserService including unit tests for all public methods and edge cases."

"Design a test strategy for our CSV import feature: what unit, integration, and E2E tests do we need?"

"Write Supertest integration tests for our REST API auth endpoints: register, login, refresh token, logout."

"Set up k6 load tests simulating 500 concurrent users on our /api/search endpoint. Target: p95 < 500ms."
```

---

### MongoDB DBA
**Model:** Haiku | **Plugin:** `engineering`

MongoDB schema design, indexing, aggregation pipelines, performance. Use for MongoDB-specific work.

**When to use:**
- Schema design for a new collection
- Writing aggregation pipelines
- Index optimization
- Query performance analysis
- MongoDB Atlas configuration

**Real-world examples:**
```
"Design a MongoDB schema for a multi-tenant SaaS where each tenant has users, projects, and tasks. Optimize for tenant-scoped queries."

"Write an aggregation pipeline to calculate monthly revenue per plan tier from our subscriptions collection."

"Our query `db.orders.find({userId, status, createdAt: {$gte}})` takes 800ms. Diagnose and create the right compound index."

"We're storing user sessions in MongoDB. Design the TTL index strategy and cleanup pipeline."

"Our MongoDB Atlas M10 cluster is hitting CPU spikes. Run a slow query analysis and recommend schema/index changes."
```

---

### Prompt Engineer
**Model:** Sonnet | **Plugin:** `engineering`

Prompt optimization, context engineering, RAG design, AI output quality. Use when building or tuning LLM features.

**When to use:**
- Writing system prompts for AI features
- Optimizing prompts for quality or cost
- Designing context injection strategies
- Building evaluation frameworks for LLM output
- Few-shot example selection

**Real-world examples:**
```
"Write a system prompt for a customer support chatbot that: stays on topic, uses our brand voice, escalates billing issues to humans, and cites knowledge base articles."

"Our classification prompt has 72% accuracy. Analyze it and rewrite it to improve precision on edge cases."

"Design a context injection strategy for a code assistant: what to include from the codebase, how to prioritize, and how to fit within 8k tokens."

"Write 10 few-shot examples for our sentiment analysis prompt covering positive, negative, neutral, and mixed signals."

"Build a prompt evaluation harness that tests our summarization prompt against 50 gold-standard examples and scores quality."
```

---

### Release Manager
**Model:** Sonnet | **Plugin:** `engineering`

Versioning, changelogs, deployment coordination. Use for release process work.

**When to use:**
- Generating release notes from git log
- Planning a major release
- Managing hotfixes
- Coordinating multi-service deployments
- Setting up semantic versioning and changelog automation

**Real-world examples:**
```
"Generate release notes for v2.3.0 from git log between v2.2.0 and HEAD. Audience: technical users. Format: GitHub release."

"We have a critical auth bug in production. Create a hotfix runbook: branch strategy, testing, deploy sequence, rollback plan."

"Design a release process for coordinating 4 microservices that must deploy together. Include health checks and rollback triggers."

"Set up conventional commits + semantic-release to auto-generate CHANGELOG.md and bump versions on merge to main."

"Create a go/no-go checklist for our v3.0.0 major release with feature flags, DB migration steps, and comms plan."
```

---

### Technical Writer
**Model:** Haiku | **Plugin:** `engineering`

API docs, HOWTOs, READMEs, runbooks. Use to produce documentation output quickly.

**When to use:**
- Writing API reference docs
- Creating developer HOWTOs
- Writing runbooks for ops teams
- Updating README files
- Creating onboarding guides

**Real-world examples:**
```
"Write API reference docs for our Orders API: list, get, create, update, cancel endpoints. Include request/response examples."

"Write a HOWTO for developers on setting up the local dev environment for our monorepo (Node.js + Python + Docker)."

"Create a runbook for on-call engineers responding to a database connection pool exhaustion incident."

"Update the README for our auth-service to reflect the new OIDC integration. Current README is 6 months stale."

"Write a developer onboarding guide covering: repo setup, local services, running tests, making your first PR."
```

---

### Test Coverage Agent
**Model:** Sonnet | **Plugin:** `engineering`

Coverage audits, gap analysis, automated test generation. Use when coverage is below threshold or tests are missing.

**When to use:**
- Auditing test coverage across a codebase
- Identifying and filling coverage gaps
- Generating tests for uncovered code paths
- Enforcing coverage thresholds in CI
- Prioritizing what to test first

**Real-world examples:**
```
"Run a coverage audit on src/. Report files below 80%, prioritized by business criticality."

"src/payments/processor.ts has 12% coverage. Generate Jest unit tests for all uncovered branches."

"Add a coverage gate to our GitHub Actions CI that fails the build if overall coverage drops below 75%."

"We added 3 new API endpoints last week. Check if they have test coverage and generate integration tests for any that don't."

"Generate a coverage heatmap report showing: files with 0% coverage, files that changed in the last 30 days with coverage < 50%."
```

---

## Platform Plugin

### Corestack Expert
**Model:** Haiku | **Plugin:** `platform`

Cloud governance, compliance policies, cost guardrails via Corestack. Use for multi-cloud governance work.

**When to use:**
- Setting up Corestack governance policies
- Compliance policy enforcement across accounts
- Cost guardrail configuration
- Cloud resource tagging policies
- Governance audit reporting

**Real-world examples:**
```
"Write a Corestack policy that enforces required tags (Environment, Team, CostCenter) on all EC2 and RDS resources."

"Configure a Corestack budget guardrail that alerts at 80% and auto-stops non-production EC2s at 100%."

"Create a governance report template for monthly cloud compliance status covering our 5 AWS accounts."

"Set up Corestack to detect and alert on public S3 buckets, unencrypted EBS volumes, and security groups with 0.0.0.0/0."
```

---

### FinOps Expert
**Model:** Haiku | **Plugin:** `platform`

Cloud cost analysis, rightsizing, reserved instances, savings plans. Use to reduce cloud spend.

**When to use:**
- Cloud cost analysis and anomaly detection
- Reserved instance or Savings Plan recommendations
- Rightsizing EC2, RDS, or container workloads
- FinOps process and reporting setup
- Chargeback and showback models

**Real-world examples:**
```
"Our AWS bill increased 35% this month. Identify the top cost drivers from our Cost Explorer data and suggest remediation."

"We have 50 EC2 instances running 24/7. Analyze CPU/memory utilization and recommend rightsizing — target 30% savings."

"Calculate the ROI of moving from on-demand to Reserved Instances for our 8 RDS instances running steadily for 2+ years."

"Design a cloud cost chargeback model for 4 product teams sharing one AWS account. Include Kubernetes namespace cost attribution."

"Set up AWS Cost Anomaly Detection with alerts for >20% week-over-week increases per service."
```

---

## Marketing Plugin

### Marketing/Content
**Model:** Haiku | **Plugin:** `marketing`

Blog posts, product announcements, marketing copy. Use to produce content quickly.

**When to use:**
- Writing release announcement blog posts
- Product launch copy
- Developer-facing marketing content
- Social media posts about new features
- Changelog entries in marketing style

**Real-world examples:**
```
"Write a developer blog post announcing our new GraphQL API. Tone: conversational, technical, excited. Include code examples."

"Write a product launch email for our CSV import feature targeting operations managers at mid-market companies."

"Turn our v2.3.0 technical changelog into a customer-facing release announcement for our newsletter."

"Write 5 LinkedIn post variations announcing our Series A funding round."

"Create a feature spotlight for our new real-time dashboard: headline, 3 bullet benefits, CTA, under 150 words."
```

---

## Azure DevOps Plugin

### ADO Project Manager
**Model:** Sonnet | **Plugin:** `azuredevops`

Work item lifecycle management, sprint tracking, and capacity planning. Auto-activates on ADO/Azure DevOps keywords. For bulk operations, pairs with `/azuredevops:import-workitems`.

**When to use:**
- Creating Features, User Stories, and Tasks (single items or bulk from PRD/TDD)
- Checking sprint status and burndown
- Generating weekly status reports
- Capacity planning by assignee
- Any Azure DevOps query or update

**Real-world examples:**
```
"Create an ADO Feature for User Authentication with 3 stories: Login, Signup, Password Reset
  --assigned-to dev@company.com --area-path MyProject\Auth --bundle Q1-Release --iteration MyProject\Sprint 5"

"Show me the current sprint status for MyProject\Sprint 5"

"Generate a weekly status report for this week's sprint as a Teams message"

"Who is over-allocated in Sprint 5? Show capacity vs remaining work by engineer."

"Create all work items from docs/prd-notifications.md and docs/tdd-notifications.md
  --assigned-to dev@company.com --area-path MyProject\TeamA --iteration MyProject\Sprint 6 --bundle Q2-Release"
```

---

## Orchestrators Plugin

See [orchestrators.md](orchestrators.md) for multi-agent workflow details.

---

## Quick Reference

| Need | Agent | Model |
|------|-------|-------|
| Strategic technology decision | CTO | Opus |
| Engineering org process | VP of Engineering | Opus |
| Cross-team coordination | Director of Engineering | Sonnet |
| Sprint / team management | Engineering Manager | Haiku |
| PRD / user stories | Product Manager | Sonnet |
| Agile ceremonies | Scrum Master | Haiku |
| System design / TDD | Technical Architect | Opus |
| Security / threat model | Security Architect | Opus |
| Data modeling / pipelines | Data Architect | Sonnet |
| AI/ML system design | AI/ML Architect | Sonnet |
| Architecture doc drift | Architecture Docs Agent | Sonnet |
| AWS infrastructure | AWS Cloud Architect | Sonnet |
| Azure infrastructure | Azure Cloud Architect | Sonnet |
| GCP infrastructure | GCP Cloud Architect | Sonnet |
| OCI infrastructure | OCI Cloud Architect | Sonnet |
| Feature implementation | Full-Stack Developer | Sonnet |
| Test writing / QA | QA Engineer | Haiku |
| MongoDB schema / queries | MongoDB DBA | Haiku |
| Prompt design / LLM | Prompt Engineer | Sonnet |
| Release / versioning | Release Manager | Sonnet |
| Docs / runbooks | Technical Writer | Haiku |
| Coverage gaps | Test Coverage Agent | Sonnet |
| Cloud governance | Corestack Expert | Haiku |
| Cloud cost reduction | FinOps Expert | Haiku |
| Blog / announcements | Marketing/Content | Haiku |
| ADO work items / sprint tracking | ADO Project Manager | Sonnet |
