---
description: "Deployment pipeline: Cloud Architect validates infra, FinOps checks cost impact, QA verifies post-deploy"
argument-hint: "<service> [--env staging|production] [--cloud aws|azure|gcp|oci]"
---

# Deploy Flow

End-to-end deployment workflow. Cloud Architect validates infrastructure readiness, FinOps Expert checks cost impact, QA Engineer runs post-deployment smoke tests.

## Chain

```
use_agent: aws-cloud-architect
```
*(or azure-cloud-architect / gcp-cloud-architect / oci-cloud-architect based on `--cloud` flag)*

**Input**: `$ARGUMENTS` — service name, target environment, cloud
**Task**: Infrastructure readiness validation:
- Verify target environment infrastructure is healthy
- Check that IaC changes (if any) have been applied and are converged
- Validate: security groups, IAM permissions, secrets configured, certificates valid
- Review scaling configuration for expected load
- Confirm rollback mechanism is ready (previous image tag, IaC state backup)
- Output GO / NO-GO with reasoning
**Handoff artifact**: Infrastructure readiness report + any blocking issues

---

```
use_agent: finops-expert
```
**Input**: Deployment details + infrastructure report
**Task**: Cost impact assessment:
- Estimate monthly cost delta from this deployment
- Check if new resources are correctly tagged for cost allocation
- Verify budget alerts are configured for the environment
- Flag any unexpectedly expensive resources added
- Rate cost risk: LOW (< 5% increase) / MEDIUM / HIGH (> 20% increase)
**Handoff artifact**: Cost impact summary + tagging compliance check + risk rating

---

```
use_agent: qa-engineer
```
**Input**: Infrastructure GO + Cost approval
**Task**: Execute deployment and verify:
- Run `/deploy $ARGUMENTS` to execute the deployment
- Monitor deployment rollout progress
- Run smoke tests against deployed environment
- Verify health endpoints, key user journeys, and critical API endpoints
- Monitor error rates and latency for 10 minutes post-deploy
- Report PASS / FAIL with specific failing scenarios if any
**Output**: Deployment result + smoke test report + monitoring summary

## Output
```
## Deployment Report: [service] → [env]

### Infrastructure Check (Cloud Architect)
Status: ✅ GO
[any notes]

### Cost Impact (FinOps)
Delta: +$X/mo (LOW risk)
Tagging: ✅ Compliant

### Deployment + Verification (QA)
Deploy: ✅ Successful
Smoke Tests: 12/12 PASS
Error Rate: 0.02% (normal)
p99 Latency: 145ms (baseline: 138ms) ✅

### Final Status: DEPLOYED SUCCESSFULLY ✅
```

## Usage
```
/orchestrators:deploy-flow order-service --env production --cloud aws
```
