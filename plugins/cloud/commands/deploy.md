---
description: "Execute or plan a deployment to a target environment"
argument-hint: "<service> [--env staging|production] [--strategy blue-green|canary|rolling]"
---

# Deploy

Execute or plan a deployment. Performs pre-deployment checks, coordinates rollout strategy, validates health post-deploy, and documents rollback plan.

## Pre-flight Checks
1. Parse `$ARGUMENTS` for service name, `--env` (default: staging), `--strategy` (default: rolling)
2. Read `.claude/memory/project-state.md` for cloud and deployment config
3. Confirm no active incidents on the target environment
4. Check CI is green for the commit being deployed

## Phase 1: Pre-Deployment Checklist
- [ ] All tests passing in CI
- [ ] Security scan clear (no new HIGH/CRITICAL findings)
- [ ] Database migrations reviewed and tested on staging
- [ ] Feature flags configured correctly for target environment
- [ ] Runbook updated if deployment changes operational behavior
- [ ] Rollback procedure documented and tested
- [ ] Stakeholders notified (production only)
- [ ] Monitoring/alerting in place for new code paths

## Phase 2: Deployment Strategy

### Rolling Update (default)
```bash
# Kubernetes rolling update
kubectl set image deployment/<service> <container>=<image>:<tag>
kubectl rollout status deployment/<service>
# Rollback if needed:
kubectl rollout undo deployment/<service>
```

### Blue-Green
```bash
# Point traffic to green environment
# Verify green is healthy
# Switch load balancer from blue to green
# Keep blue running for 30 min for fast rollback
```

### Canary
```bash
# Route 5% of traffic to new version
# Monitor error rates and latency for 15 min
# If clean, gradually increase: 5% → 25% → 50% → 100%
# Abort if p99 latency increases >20% or error rate >0.1%
```

## Phase 3: Health Checks
After deployment, verify:
- All pods/instances healthy: `kubectl get pods` or equivalent
- Health endpoint returning 200: `curl https://<service>/health`
- Key metrics normal (within 2 std dev of baseline):
  - Error rate < 0.1%
  - p99 latency within 20% of pre-deploy baseline
  - No increase in 5xx responses
- Smoke test critical user paths

## Phase 4: Rollback Plan
Document before deploying:
```markdown
## Rollback Procedure
**Trigger**: error rate > X% or p99 latency > Yms for > 5 min
**Command**: kubectl rollout undo deployment/<service>
**ETA**: ~3 minutes
**Data rollback**: [required/not required — detail if required]
**Notification**: post to #incidents Slack channel
```

## Phase 5: Post-Deployment
- [ ] Confirm all health checks green for 15+ minutes
- [ ] Check error logs for new patterns
- [ ] Update deployment record in run log
- [ ] Notify stakeholders of successful deployment
- [ ] Schedule post-deploy review if this was a major release

## Error Handling
- CI not green: block deployment, show failing checks
- Health check fails after deploy: auto-trigger rollback, post incident notification
- Database migration fails: stop deployment, run rollback migration
