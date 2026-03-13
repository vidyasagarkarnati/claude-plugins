---
description: "Create a Technical Design Document (Tech Spec) for a feature"
argument-hint: "<feature-name> [--prd <path/to/prd.md>]"
---

# Create TDD

Generate a complete Technical Design Document (Tech Spec) for a feature. Uses a Technical Architect persona to design the implementation approach, API contracts, data models, and non-functional requirements.

## Pre-flight Checks
1. Confirm feature name is provided in `$ARGUMENTS`
2. If `--prd` flag provided, read the referenced PRD file
3. Read `.claude/memory/project-state.md` for tech stack and existing architecture
4. Check `.claude/memory/decisions.md` for relevant prior ADRs

## Phase 1: Problem Analysis
- Summarize the feature's requirements and constraints from the PRD or argument
- Identify components affected: services, databases, APIs, third-party integrations
- List non-functional requirements: latency targets, throughput, availability, data retention

## Phase 2: Architecture Design
- Draw the system context (which services/components are involved)
- Choose the appropriate architectural pattern (REST/event-driven/batch) and justify it
- Identify new services or significant changes to existing services
- Note dependencies and integration points

## Phase 3: API Contracts
For each new or modified endpoint, document:
```
METHOD /resource/{id}
Request body: { ... }
Response: { ... }
Error codes: 400, 401, 404, 500
Auth: Bearer JWT required
Rate limit: 100/min per user
```

## Phase 4: Data Models
- Schema definition (MongoDB collection or SQL table)
- Index strategy (which fields are indexed and why)
- Data migration plan if modifying existing schemas (expand-contract pattern)
- Data retention and archival policy

## Phase 5: Non-Functional Requirements
- **Performance**: p50/p95/p99 latency targets
- **Scalability**: expected load and horizontal scaling approach
- **Security**: auth model, data sensitivity classification, encryption requirements
- **Observability**: key metrics, logs, and alerts needed
- **Resilience**: failure modes and recovery strategies

## Phase 6: Architecture Decision Record
Write an ADR for any significant decision in this design:
```markdown
## ADR-NNN: [Decision Title]
**Date**: YYYY-MM-DD
**Status**: Proposed
**Context**: [Why this decision is needed]
**Decision**: [What was decided]
**Consequences**: [Trade-offs]
```

## Phase 7: Implementation Plan
- Break work into ordered tasks with estimated complexity (S/M/L)
- Identify parallel vs sequential work
- List risks and open questions for the engineering team
- Define definition of done for this feature

## Output Format
Save as `docs/tdd-$ARGUMENTS.md` with sections:
1. Overview & Goals
2. Architecture Design
3. API Contracts
4. Data Models
5. Non-Functional Requirements
6. Security Considerations
7. Observability Plan
8. Implementation Plan
9. ADRs
10. Open Questions

## Error Handling
- Missing PRD: infer requirements from feature name; flag all assumptions
- Conflicting architectural approaches: present trade-offs in a comparison table
