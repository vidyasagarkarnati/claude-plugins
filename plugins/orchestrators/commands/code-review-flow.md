---
description: "Multi-layer code review: Technical Architect reviews design, Security Architect scans vulnerabilities, Full-Stack Developer resolves findings"
argument-hint: "[--pr <number>] [--files <glob>]"
---

# Code Review Flow

Three-layer code review. Technical Architect reviews architecture and design quality, Security Architect scans for vulnerabilities, Full-Stack Developer resolves all findings.

## Chain

```
use_agent: technical-architect
```
**Input**: `$ARGUMENTS` — PR number or file glob
**Task**: Architecture and design review:
- Run `/code-review $ARGUMENTS --focus architecture`
- Check: API design consistency, data model integrity, component boundaries
- Verify the change doesn't violate existing ADRs
- Assess scalability and maintainability impact
- Rate overall design: APPROVE / REQUEST_CHANGES / NEEDS_DISCUSSION
**Handoff artifact**: Architecture review findings (critical/suggested/nit)

---

```
use_agent: security-architect
```
**Input**: PR/files scope from previous step
**Task**: Security-focused review:
- Run `/code-review $ARGUMENTS --focus security`
- Apply OWASP Top 10 lens to every changed file
- Check: input validation, auth/authz, secrets, injection, dependency vulnerabilities
- Rate each finding: CRITICAL / HIGH / MEDIUM / LOW
- For CRITICAL findings: block merge and provide remediation steps
**Handoff artifact**: Security findings list with severity ratings + remediation steps

---

```
use_agent: full-stack-developer
```
**Input**: Architecture findings + Security findings from previous steps
**Task**: Resolve all findings:
- Fix all CRITICAL and HIGH findings (required before merge)
- Address MEDIUM and suggested architecture findings
- Add comments on nits explaining why changes were or weren't made
- Re-run tests after fixes
- Update PR description with summary of changes made in response to review
**Output**: Updated PR / file changes + list of resolved findings + any accepted-as-is rationale

## Output
Structured review summary:
```
## Code Review: [PR/scope]

### Architecture Review (Technical Architect)
- CRITICAL: [0]
- REQUEST CHANGES: [N items]

### Security Review (Security Architect)
- CRITICAL: [0]
- HIGH: [N items]

### Resolution (Full-Stack Developer)
- Fixed: [list]
- Accepted as-is: [list with rationale]

### Final Status: APPROVED / NEEDS FURTHER REVIEW
```

## Usage
```
/orchestrators:code-review-flow --pr 142
```
