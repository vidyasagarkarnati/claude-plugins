# AI Agent Team

A team of **25 specialized AI agents** covering the full software engineering lifecycle — from strategy and architecture to development, testing, deployment, and marketing. Works on both **Claude Code** (primary) and **GitHub Copilot** (secondary) without maintaining duplicate configurations.

---

## The Team

### Leadership (6 agents)
| Agent | Model | Role |
|-------|-------|------|
| CTO | Opus | Technology strategy, build vs buy, architectural governance |
| VP of Engineering | Opus | Engineering excellence, DORA metrics, delivery velocity |
| Director of Engineering | Sonnet | Cross-team coordination, roadmap execution |
| Engineering Manager | Haiku | Sprint management, capacity planning, blocker removal |
| Product Manager | Sonnet | PRDs, user stories, prioritization (RICE), roadmap |
| Scrum Master | Haiku | Agile ceremonies, retrospectives, sprint health |

### Architecture (5 agents)
| Agent | Model | Role |
|-------|-------|------|
| Technical Architect | Opus | System design, TDDs, tech stack decisions, ADRs |
| Security Architect | Opus | Threat modeling (STRIDE), OWASP, compliance |
| Data Architect | Sonnet | Data modeling, ETL/ELT, data governance |
| AI/ML Architect | Sonnet | ML system design, MLOps, RAG, LLM integration |
| Architecture Docs Agent | Sonnet | Doc auditing, drift detection, ADR generation |

### Cloud (4 agents)
| Agent | Model | Role |
|-------|-------|------|
| AWS Cloud Architect | Sonnet | AWS Well-Architected, CDK/Terraform, multi-account |
| Azure Cloud Architect | Sonnet | Azure landing zones, Bicep/Terraform, Entra ID |
| GCP Cloud Architect | Sonnet | GKE, BigQuery, Workload Identity, VPC Service Controls |
| OCI Cloud Architect | Sonnet | Compartments, OKE, Autonomous Database |

### Engineering (8 agents)
| Agent | Model | Role |
|-------|-------|------|
| Full-Stack Developer | Sonnet | React/TypeScript, Node.js/Python, APIs, Docker |
| QA Engineer | Haiku | Test strategy, Playwright, Jest, automation |
| MongoDB DBA | Haiku | Schema design, indexing, aggregation pipelines |
| Prompt Engineer | Sonnet | Prompt optimization, RAG design, context engineering |
| Release Manager | Sonnet | Versioning, changelogs, deployment coordination |
| Technical Writer | Haiku | API docs, HOWTOs, runbooks, READMEs |
| Test Coverage Agent | Sonnet | Coverage audits, gap analysis, test generation |

### Platform (2 agents)
| Agent | Model | Role |
|-------|-------|------|
| Corestack Expert | Haiku | Cloud governance, compliance policies, cost guardrails |
| FinOps Expert | Haiku | Cost analysis, rightsizing, reserved instances |

### Marketing (1 agent)
| Agent | Model | Role |
|-------|-------|------|
| Marketing/Content | Haiku | Blog posts, release announcements, marketing copy |

---

## Orchestrator Modes

Activate multi-agent workflows with a single command:

| Mode | Command | Agent Chain |
|------|---------|-------------|
| Plan Mode | `/orchestrators:prd-workflow` | PM → Technical Architect → Scrum Master |
| Brainstorming | `/orchestrators:brainstorm` | CTO → PM → AI/ML Architect |
| Development | `/orchestrators:full-sdlc` | Full-Stack Dev → QA → MongoDB DBA |
| Code Review | `/orchestrators:code-review-flow` | Technical Architect → Security Architect → Full-Stack Dev |
| Bug Fix | `/orchestrators:bug-fix-flow` | Full-Stack Dev → QA → Test Coverage Agent |
| Deployment | `/orchestrators:deploy-flow` | Cloud Architect → FinOps → QA |
| Documentation | `/orchestrators:doc-flow` | PM → Technical Writer → Prompt Engineer |
| Sprint Planning | `/orchestrators:sprint-workflow` | Scrum Master → Eng Manager → PM |

---

## Slash Commands

Commands are namespaced by plugin. Use `/plugin:command` syntax in Claude Code.

| Command | Plugin | Description |
|---------|--------|-------------|
| `/leadership:create-prd` | leadership | Create a Product Requirements Document |
| `/leadership:sprint-planning` | leadership | Run sprint planning with estimation and capacity check |
| `/architecture:create-tdd` | architecture | Create a Technical Design Document |
| `/architecture:threat-model` | architecture | Create a STRIDE threat model |
| `/architecture:update-architecture-docs` | architecture | Scan and update stale architecture documentation |
| `/cloud:cost-estimate` | cloud | Estimate cloud infrastructure costs |
| `/cloud:deploy` | cloud | Execute a deployment with health checks and rollback plan |
| `/engineering:code-review` | engineering | Multi-layer code review (quality + security + performance) |
| `/engineering:bug-fix` | engineering | Diagnose and fix a bug end-to-end |
| `/engineering:release-notes` | engineering | Generate release notes from git log |
| `/engineering:document` | engineering | Generate API docs, HOWTOs, READMEs, or runbooks |
| `/engineering:coverage-audit` | engineering | Audit test coverage and generate missing tests |

---

## Repository Structure

```
.
├── .claude/
│   ├── CLAUDE.md                  # Agent memory foundation (all agents read this)
│   ├── settings.json              # Hook events + permissions config
│   ├── hooks/                     # 8 automation scripts
│   └── memory/                    # Shared project state
│       ├── project-state.md       # Tech stack, services, key decisions
│       ├── sprint-context.md      # Active sprint, tickets, capacity
│       └── decisions.md           # Architecture Decision Records (ADRs)
├── plugins/                       # Self-contained installable plugins
│   ├── leadership/                # /leadership:* commands
│   │   ├── .claude-plugin/plugin.json
│   │   ├── agents/                # 6 agents (CTO, VP Eng, Director, EM, PM, Scrum Master)
│   │   ├── skills/                # prd-writing, agile, project-context
│   │   └── commands/              # create-prd, sprint-planning
│   ├── architecture/              # /architecture:* commands
│   │   ├── .claude-plugin/plugin.json
│   │   ├── agents/                # 5 agents (Technical, Security, Data, AI/ML, Arch Docs)
│   │   ├── skills/                # architecture, security, tdd-writing, architecture-docs
│   │   └── commands/              # create-tdd, threat-model, update-architecture-docs
│   ├── cloud/                     # /cloud:* commands
│   │   ├── .claude-plugin/plugin.json
│   │   ├── agents/                # 4 agents (AWS, Azure, GCP, OCI)
│   │   ├── skills/                # cloud-aws, cloud-azure, cloud-gcp, cloud-oci
│   │   └── commands/              # cost-estimate, deploy
│   ├── engineering/               # /engineering:* commands
│   │   ├── .claude-plugin/plugin.json
│   │   ├── agents/                # 7 agents (Full-Stack, QA, MongoDB DBA, Prompt, Release, Writer, Test Coverage)
│   │   ├── skills/                # mongodb, prompt-engineering, test-coverage
│   │   └── commands/              # code-review, bug-fix, release-notes, document, coverage-audit
│   ├── platform/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── agents/                # 2 agents (Corestack, FinOps)
│   │   └── skills/                # finops, corestack
│   ├── marketing/
│   │   ├── .claude-plugin/plugin.json
│   │   └── agents/                # 1 agent (Marketing/Content)
│   └── orchestrators/             # /orchestrators:* commands
│       ├── .claude-plugin/plugin.json
│       └── commands/              # 8 multi-agent workflow orchestrators
├── .github/
│   ├── prompts/                   # Auto-generated Copilot prompts (from sync script)
│   ├── workflows/                 # CI: validation + prompt sync
│   └── instructions/              # Scoped Copilot instructions (arch/security/testing)
├── .mcp.json                      # MCP server config (Firecrawl, Perplexity, Playwright, Hunter, GitHub)
├── .claude-plugin/
│   └── marketplace.json           # Plugin registry (references all 7 plugin.json manifests)
├── scripts/
│   ├── setup-symlinks.sh          # One-time setup after clone
│   └── sync-commands.sh           # Sync plugin commands → Copilot prompts
├── docs/                          # Usage guides with real-world examples
│   ├── agents.md                  # All 25 agents with use cases
│   ├── commands.md                # All 12 commands with scenarios
│   └── orchestrators.md           # All 8 orchestrators with end-to-end examples
└── references/
    └── wshobson_agents/           # Reference: wshobson/agents (72 plugins, 496 agents)
```

---

## Quick Start

### 1. Clone and set up
```bash
git clone <this-repo>
cd my-ai-agent-team
bash scripts/setup-symlinks.sh
```

### 2. Configure MCP tools
Add to your shell profile (`.zshrc` / `.bashrc`):
```bash
export PERPLEXITY_API_KEY="your-key"
export FIRECRAWL_API_KEY="your-key"
export HUNTER_API_KEY="your-key"
export GITHUB_PERSONAL_ACCESS_TOKEN="your-token"
```

### 3. Fill in project context
Edit `.claude/memory/project-state.md` with your project's tech stack and context. Agents read this at session start.

### 4. Start using agents
```bash
# In Claude Code — just describe what you need:
"Design the authentication system for our API"        # → Technical Architect activates
"Write tests for src/orders/service.ts"               # → QA Engineer + Test Coverage Agent
"We have a 500 error on /api/checkout — fix it"       # → Full-Stack Dev + bug-fix-flow

# Or use plugin-namespaced commands directly:
/leadership:create-prd "user dashboard with analytics"
/orchestrators:code-review-flow --pr 142
/engineering:coverage-audit --threshold 80
```

---

## Compatibility

| Tool | Support | Method |
|------|---------|--------|
| Claude Code | ✅ Native | `.claude/` directory |
| GitHub Copilot | ✅ Via symlinks + sync | `.github/` directory |
| Cursor | ✅ Via AGENTS.md symlink | Root `AGENTS.md` |

The `scripts/setup-symlinks.sh` script wires everything up after clone. The `scripts/sync-commands.sh` script (also runs in CI on push) translates Claude commands to Copilot prompt format automatically.

---

## MCP Integrations

| Tool | Agents | Purpose |
|------|--------|---------|
| Perplexity | CTO, PM, Prompt Engineer | Web research and knowledge lookup |
| Firecrawl | PM, FinOps Expert | Web scraping and data extraction |
| Playwright | QA Engineer | Browser automation and E2E testing |
| Hunter | Marketing/Content | Email finding for outreach |
| GitHub MCP | Release Manager, Eng Manager | PR/issue/repo management |

---

## Documentation

| Doc | Contents |
|-----|----------|
| [docs/agents.md](docs/agents.md) | Usage guide for all 25 agents with real-world examples |
| [docs/commands.md](docs/commands.md) | Reference for all 12 slash commands with scenarios |
| [docs/orchestrators.md](docs/orchestrators.md) | Multi-agent workflow guide with end-to-end examples |
| [INSTRUCTIONS.MD](INSTRUCTIONS.MD) | Installation, setup, and configuration guide |

---

## Inspired By
- [wshobson/agents](https://github.com/wshobson/agents) — 72 plugin reference library (included as `references/wshobson_agents/`)
