---
name: finops
description: FinOps phases (Inform/Optimize/Operate), cost allocation tags, rightsizing methodology, reserved instance analysis, and showback/chargeback models
---

# FinOps

Mastery of this skill enables you to analyze cloud spend, identify optimization opportunities, implement cost governance, and build accountability frameworks for engineering teams.

## When to Use This Skill
- Analyzing cloud costs and identifying waste
- Recommending reserved instances or savings plans
- Setting up cost allocation and tagging strategies
- Building showback or chargeback models
- Responding to unexpected cost spikes

## Core Concepts

### 1. FinOps Phases
**Inform**: Visibility — who is spending what, on what.
**Optimize**: Reduce waste — rightsizing, reserved capacity, architectural changes.
**Operate**: Ongoing discipline — budgets, alerts, culture of ownership.

### 2. Cost Optimization Levers (priority order)
1. **Eliminate waste** — unused resources (stopped EC2s, unattached EBS, orphaned load balancers)
2. **Rightsize** — oversized instances (use CloudWatch/Datadog metrics to find underutilized)
3. **Reserved capacity** — 1-year reserved = 30-40% savings; 3-year = 50-60%
4. **Spot/Preemptible** — 60-90% savings for non-critical, interruptible workloads
5. **Architecture optimization** — Lambda vs EC2, managed services, data transfer reduction

### 3. Tagging Strategy (Required Tags)
| Tag | Purpose | Example |
|-----|---------|---------|
| `Environment` | Cost by env | `prod`, `staging`, `dev` |
| `Team` | Showback | `platform`, `payments` |
| `Service` | Service cost | `order-service` |
| `CostCenter` | Chargeback | `eng-123` |
| `Project` | Project tracking | `migration-2026` |

## Quick Reference
```bash
# AWS: find unused resources
aws ec2 describe-instances --filters "Name=instance-state-name,Values=stopped"
aws ec2 describe-volumes --filters "Name=status,Values=available"  # unattached EBS

# Find top cost services this month
aws ce get-cost-and-usage \
  --time-period Start=2026-03-01,End=2026-03-31 \
  --granularity MONTHLY \
  --metrics "UnblendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE

# Rightsizing recommendations
aws ce get-rightsizing-recommendation --service EC2
```

## Key Patterns

### Pattern 1: Monthly Cost Review Checklist
```markdown
## Monthly FinOps Review

### 1. Anomaly Detection
- [ ] Review Cost Anomaly Detection alerts
- [ ] Compare MTD vs last month same period
- [ ] Flag any service > 20% increase

### 2. Waste Audit
- [ ] Stopped EC2 instances still billed (EBS volumes)
- [ ] Unattached EBS volumes
- [ ] Idle NAT Gateways (< 5% utilization)
- [ ] Unused Elastic IPs
- [ ] Old AMI snapshots (> 90 days, no instance)

### 3. Rightsizing
- [ ] Review CloudWatch CPU < 10% for 14+ days → downsize
- [ ] Memory utilization from CloudWatch agent
- [ ] RDS connections < 20% of max → smaller instance class

### 4. Reserved Coverage
- [ ] On-demand spend on steady-state workloads > $500/mo → buy 1yr RI
- [ ] RI utilization > 90%? (else: modify or sell)
- [ ] Savings Plans coverage

### 5. Tagging Compliance
- [ ] Resources without required tags
- [ ] New resources added this month — properly tagged?
```

### Pattern 2: Rightsizing Analysis
```
Downsize recommendation criteria:
- CPU utilization: p99 < 40% for 14 days
- Memory: p99 < 50% for 14 days (requires CloudWatch agent)
- Network: not a network-bound workload

Downsize path:
t3.xlarge (4 vCPU, 16GB, $0.166/hr) → t3.large (2 vCPU, 8GB, $0.083/hr)
Savings: $0.083/hr × 730 hr = $61/mo per instance

Action: schedule maintenance window, change instance type, verify performance
```

### Pattern 3: Reserved Instance Breakeven
```
On-demand: $0.192/hr (t3.large)
1-year RI (no upfront): $0.121/hr → 37% savings
3-year RI (all upfront): $1,465 total → $0.056/hr → 71% savings

Breakeven for 1-yr RI vs on-demand: always (from month 1 if steady-state)
Breakeven for 3-yr all-upfront: ~8 months vs 1-yr no-upfront

Recommendation: 1-year RI for prod workloads; spot for dev/batch
```

## Best Practices
1. Tag everything before optimizing — you can't optimize what you can't measure
2. Eliminate waste first — it has 100% ROI with no risk
3. Reserved instances: match to baseline, not peak (use on-demand for peaks)
4. Set budget alerts at 80% and 100% of monthly budget — don't wait for the bill
5. Give teams visibility into their own spend — engineers optimize what they see
6. Spot instances: use Spot Fleet with multiple AZs to reduce interruption risk
7. Data egress is often the hidden cost driver — check CDN coverage

## Common Issues
- **Tagging compliance < 80%**: enforce at provisioning via IaC + SCP/policy; don't rely on manual tagging
- **RI utilization < 70%**: modify instance type/family or sell on RI marketplace
- **Surprise cost spike**: check Cost Anomaly Detection; common causes are unprotected Lambda recursion, S3 data transfer, or auto-scaling event
