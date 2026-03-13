# Setup & Usage Instructions

Complete guide to installing, configuring, and using the AI Agent Team.

---

## Prerequisites

- **Claude Code** `>= 2.x` or **GitHub Copilot** (VS Code extension)
- **Node.js** `>= 18` (for MCP tools via `npx`)
- **jq** (for hook scripts): `brew install jq`
- API keys for MCP tools you want to use (see [MCP Setup](#mcp-setup))

---

## Installation

### Step 1: Clone the repository
```bash
git clone <your-repo-url>
cd my-ai-agent-team
```

### Step 2: Run the setup script
```bash
bash scripts/setup-symlinks.sh
```

This creates:
- `AGENTS.md` → symlink to `CLAUDE.MD` (Cursor compatibility)
- `.github/copilot-instructions.md` → symlink to `.claude/CLAUDE.md`

### Step 3: Generate Copilot prompts
```bash
bash scripts/sync-commands.sh
```

This translates `plugins/*/commands/*.md` → `.github/prompts/*.prompt.md` with Copilot-compatible syntax. Runs automatically in CI on every push that changes plugin commands.

---

## MCP Setup

MCP tools give agents access to web search, browser automation, and external APIs. All are configured in `.mcp.json`.

### Required environment variables

Add these to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
# Perplexity — web search for CTO, PM, Prompt Engineer
export PERPLEXITY_API_KEY="pplx-..."

# Firecrawl — web scraping for PM, FinOps
export FIRECRAWL_API_KEY="fc-..."

# Hunter — email lookup for Marketing
export HUNTER_API_KEY="..."

# GitHub MCP — PR/issue management
export GITHUB_PERSONAL_ACCESS_TOKEN="ghp_..."

# Playwright — no key needed (browser automation)
```

Reload your shell: `source ~/.zshrc`

### Verify MCP is working
In Claude Code, type:
```
/mcp
```
You should see the 5 configured servers listed.

---

## Project Context Setup

Agents read `.claude/memory/` files at session start to understand your project. Fill these in before your first session.

### `.claude/memory/project-state.md`
```markdown
## Project Overview
- **Project:** My App
- **Description:** SaaS platform for team collaboration

## Tech Stack
- **Backend:** FastAPI + Python 3.12
- **Frontend:** React 18 + TypeScript + Tailwind
- **Database:** MongoDB Atlas + Redis
- **Cloud:** AWS (us-east-1)
- **CI/CD:** GitHub Actions
```

### `.claude/memory/sprint-context.md`
Update this at the start of each sprint with your tickets, sprint goal, and team capacity.

### `.claude/memory/decisions.md`
Architecture decisions are auto-appended here by the `/architecture:update-architecture-docs` command and by the Architecture Docs Agent.

---

## Further Reading

| Doc | Contents |
|-----|----------|
| [docs/agents.md](docs/agents.md) | All 25 agents with real-world use cases and invocation examples |
| [docs/commands.md](docs/commands.md) | All 12 slash commands with scenarios and output descriptions |
| [docs/orchestrators.md](docs/orchestrators.md) | All 8 orchestrator workflows with end-to-end examples |

---

## Using Individual Agents

Agents activate automatically based on your prompt in Claude Code. You can also invoke them explicitly.

### Auto-activation examples
```
"Design the authentication system"          → Technical Architect
"Review this code for security issues"      → Security Architect
"Write a PRD for the export feature"        → Product Manager
"Fix the 500 error on /api/checkout"        → Full-Stack Developer
"Estimate AWS costs for this architecture"  → AWS Cloud Architect + FinOps Expert
"Generate tests for src/auth/"              → Test Coverage Agent
"Update the README for the orders service"  → Technical Writer
```

### Explicit invocation (Claude Code)
```
Use the technical-architect agent to review this system design.
Use the security-architect agent to threat model the payment flow.
Use the mongodb-dba agent to optimize this aggregation pipeline.
```

---

## Using Slash Commands

### In Claude Code
Commands are namespaced by plugin. Type `/plugin:command`:
```bash
# Leadership plugin
/leadership:create-prd "user notifications with email and push"
/leadership:sprint-planning --sprint "Sprint 15" --capacity 40

# Architecture plugin
/architecture:create-tdd "CSV export feature" --prd docs/prd-csv-export.md
/architecture:threat-model "user authentication and session management"
/architecture:update-architecture-docs --create-adrs --output-report

# Cloud plugin
/cloud:cost-estimate "3-tier web app on AWS with RDS and EKS" --cloud aws
/cloud:deploy order-service --env staging --strategy rolling

# Engineering plugin
/engineering:code-review --pr 142
/engineering:code-review --files "src/auth/**" --focus security
/engineering:bug-fix "TypeError: Cannot read property 'id' of undefined at orders.js:47"
/engineering:release-notes --from v1.3.0 --to HEAD --format slack
/engineering:document --type api --path src/routes/orders.ts
/engineering:coverage-audit --threshold 80 --path src/
```

### In GitHub Copilot
The same commands are available as prompts in `.github/prompts/`. Access them via the Copilot Chat prompt picker (e.g., `@workspace /leadership-create-prd`).

---

## Using Orchestrator Workflows

Orchestrators chain multiple agents to complete a full workflow.

### Plan Mode — `/orchestrators:prd-workflow`
Chains: Product Manager → Technical Architect → Scrum Master

```
/orchestrators:prd-workflow "real-time notifications with WebSockets"
```

Produces:
1. `docs/prd-real-time-notifications.md`
2. `docs/tdd-real-time-notifications.md`
3. Updated sprint stories in `.claude/memory/sprint-context.md`

---

### Development Mode — `/orchestrators:full-sdlc`
Chains: Full-Stack Developer → QA Engineer → MongoDB DBA (if DB changes)

```
/orchestrators:full-sdlc "PROJ-234: add bulk user import via CSV"
/orchestrators:full-sdlc "PROJ-234" --tdd docs/tdd-bulk-import.md
```

Produces: implemented feature + tests + data layer review

---

### Code Review — `/orchestrators:code-review-flow`
Chains: Technical Architect → Security Architect → Full-Stack Developer (resolves findings)

```
/orchestrators:code-review-flow --pr 156
/orchestrators:code-review-flow --files "src/payments/**"
```

Produces: architecture review + security scan + resolved PR

---

### Bug Fix Mode — `/orchestrators:bug-fix-flow`
Chains: Full-Stack Developer → QA Engineer → Test Coverage Agent

```
/orchestrators:bug-fix-flow "users getting logged out randomly after 10 min"
```

Produces: root cause analysis + fix + regression test

---

### Deployment — `/orchestrators:deploy-flow`
Chains: Cloud Architect → FinOps Expert → QA Engineer

```
/orchestrators:deploy-flow api-service --env production --cloud aws
```

Produces: infra validation + cost impact check + deployment + smoke tests

---

### Documentation — `/orchestrators:doc-flow`
Chains: Product Manager → Technical Writer → Prompt Engineer

```
/orchestrators:doc-flow "getting started guide" --type howto
/orchestrators:doc-flow "orders API" --type api
```

Produces: complete, polished documentation

---

### Sprint Planning — `/orchestrators:sprint-workflow`
Chains: Scrum Master → Engineering Manager → Product Manager

```
/orchestrators:sprint-workflow --sprint "Sprint 15" --capacity 45
```

Produces: committed sprint plan in `.claude/memory/sprint-context.md`

---

### Brainstorming — `/orchestrators:brainstorm`
Chains: CTO → Product Manager → AI/ML Architect

```
/orchestrators:brainstorm "how should we approach AI-powered search?"
```

Produces: strategic brief + product angle + technical feasibility + recommendation

---

## Hook System

Hooks run automatically on specific events — no configuration needed after setup.

| Hook | Event | What It Does |
|------|-------|-------------|
| `inject-context.sh` | Session start | Loads project state + sprint context |
| `prompt-enhance.sh` | Every prompt | Logs prompt patterns and quality signals |
| `security-check.sh` | Before any Bash command | Blocks dangerous shell patterns |
| `audit-log.sh` | After every tool use | Logs all tool invocations |
| `validate-output.sh` | Before agent stops | Checks for incomplete output signals |
| `log-handoff.sh` | When subagent completes | Logs agent-to-agent handoffs |
| `notify-next-agent.sh` | When subagent completes | Signals next agent in an orchestrator chain |
| `teammate-sync.sh` | Agent idle / task complete | Syncs agent team state |

Logs are written to `.claude/logs/` (gitignored).

---

## Customization

### Add a new agent
1. Create `plugins/<plugin>/agents/<name>.md` using this template:
```yaml
---
name: agent-name
description: One-sentence trigger description. Use PROACTIVELY when [specific conditions].
model: opus|sonnet|haiku
color: blue|cyan|magenta|yellow|green|red|orange
---

You are a [role] specializing in [domain].

## Core Mission
[2-3 sentences]

## Capabilities
[Domain-specific knowledge sections]

## Behavioral Traits
[How this agent approaches problems]

## Response Approach
[Step-by-step methodology]
```
2. Register it in `.claude-plugin/marketplace.json`

### Add a new slash command
1. Create `plugins/<plugin>/commands/<command-name>.md`
2. Run `bash scripts/sync-commands.sh` to generate the Copilot prompt
3. Invoke it as `/<plugin>:<command-name>` in Claude Code

### Add a new skill
1. Create `plugins/<plugin>/skills/<skill-name>/SKILL.md`
2. Follow the skill template: frontmatter → When to Use → Core Concepts → Quick Reference → Key Patterns → Best Practices → Common Issues
3. Reference it in `plugins/<plugin>/.claude-plugin/plugin.json` under `"skills"`

### Add a new MCP server
Add to `.mcp.json`:
```json
"my-tool": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "my-mcp-package"],
  "env": {
    "MY_API_KEY": "${MY_API_KEY}"
  }
}
```

---

## Updating for Your Project

Before your first session, update these three things:

1. **Tech stack**: `.claude/memory/project-state.md` — what you're actually building
2. **Current sprint**: `.claude/memory/sprint-context.md` — active tickets and goals
3. **Team context in CLAUDE.md**: if your team uses different tools or standards, update `.claude/CLAUDE.md`

The agents will automatically adapt to whatever stack and context you describe.

---

## Troubleshooting

**Agents not activating?**
Ensure you're in a Claude Code session within this repository directory, or that `.github/copilot-instructions.md` is symlinked (run `setup-symlinks.sh`).

**MCP tools not working?**
Run `/mcp` in Claude Code to see server status. Check that environment variables are exported in your shell profile and that you've reloaded it (`source ~/.zshrc`).

**Hook scripts not running?**
Verify scripts are executable: `ls -la .claude/hooks/`. If not: `chmod +x .claude/hooks/*.sh`.

**Copilot prompts out of sync?**
Run `bash scripts/sync-commands.sh` manually, or push a change to `plugins/*/commands/` to trigger the CI workflow.

**Coverage audit failing to detect framework?**
Use the explicit flag: `/engineering:coverage-audit --framework jest` or `pytest` or `go`.
