---
description: "Create a STRIDE threat model for a system or feature"
argument-hint: "<system-or-feature-description>"
---

# Threat Model

Create a structured STRIDE threat model for a system or feature. Uses a Security Architect persona to systematically identify threats, rate risks, and recommend mitigations.

## Pre-flight Checks
1. Parse `$ARGUMENTS` for system/feature description
2. Read `.claude/memory/project-state.md` for architecture context
3. Check for existing threat models in `docs/security/`

## Phase 1: System Boundary Definition
- Identify what's in scope: services, components, data stores, external integrations
- Draw a simple data flow diagram (text-based):
  ```
  User → [HTTPS] → API Gateway → [Internal] → Service → [TCP] → Database
  ```
- List all trust boundaries (where authentication/authorization decisions are made)
- Identify all data assets and their sensitivity classification (PUBLIC/INTERNAL/CONFIDENTIAL/SECRET)

## Phase 2: Asset Identification
List the assets that need protection:
| Asset | Sensitivity | Location | Owner |
|-------|-------------|----------|-------|
| User PII | CONFIDENTIAL | MongoDB users collection | Platform |
| Auth tokens | SECRET | Redis sessions | Auth service |

## Phase 3: STRIDE Analysis

For each trust boundary and component, apply STRIDE:

| Threat | Description | Example |
|--------|-------------|---------|
| **S**poofing | Impersonating a user or system | JWT forgery, SSRF |
| **T**ampering | Modifying data or code | SQL injection, CSRF |
| **R**epudiation | Denying an action occurred | No audit log |
| **I**nformation Disclosure | Exposing sensitive data | Verbose errors, IDOR |
| **D**enial of Service | Making system unavailable | No rate limiting |
| **E**levation of Privilege | Gaining unauthorized access | Privilege escalation, BOLA |

For each identified threat:
```
Threat: [STRIDE category]
Component: [where it applies]
Description: [what could happen]
Likelihood: HIGH/MEDIUM/LOW
Impact: HIGH/MEDIUM/LOW
Risk Score: [Likelihood × Impact]
Mitigation: [specific control]
Status: Open/Mitigated/Accepted
```

## Phase 4: Risk Rating
Rate each threat:
- **CRITICAL** (High × High): immediate mitigation required
- **HIGH** (High × Medium or Medium × High): fix before production
- **MEDIUM**: fix in current or next sprint
- **LOW**: track, fix when convenient

## Phase 5: Mitigations
For each HIGH/CRITICAL threat, provide concrete mitigation steps with code examples where relevant.

## Output Format
Save as `docs/security/threat-model-$ARGUMENTS.md`:
1. Executive Summary (3 bullets: scope, top risks, key mitigations)
2. System Boundary Diagram
3. Asset Register
4. STRIDE Threat Table
5. Risk Register (sorted by severity)
6. Recommended Mitigations
7. Accepted Risks (with justification)

## Error Handling
- Vague system description: ask for data flow clarification before proceeding
- No architecture context: infer from project-state.md and flag assumptions
