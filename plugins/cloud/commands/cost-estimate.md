---
description: "Estimate cloud infrastructure costs for an architecture"
argument-hint: "<architecture-description> [--cloud aws|azure|gcp|oci]"
---

# Cost Estimate

Estimate monthly cloud infrastructure costs for a described architecture. Uses a FinOps Expert + Cloud Architect persona. Includes optimization recommendations.

## Pre-flight Checks
1. Parse `$ARGUMENTS` for architecture description and `--cloud` target (default: AWS)
2. Read `.claude/memory/project-state.md` for current infrastructure context
3. Note: all estimates are approximate — use cloud pricing calculators for final numbers

## Phase 1: Resource Identification
Extract all infrastructure components from the description:
- Compute: VMs, containers, serverless functions, auto-scaling groups
- Storage: block storage, object storage, databases
- Networking: load balancers, NAT gateways, data transfer, CDN
- Managed services: queues, caches, search, monitoring
- Supporting: DNS, certificates, secrets management

## Phase 2: Usage Estimation
For each resource, estimate:
- Instance type / size
- Hours per month (730 for always-on, less for scheduled)
- Storage GB
- Requests per month (for serverless/managed services)
- Data transfer GB (egress is usually billed, ingress is free)

## Phase 3: Cost Breakdown

### AWS Example Format
| Service | Type | Qty | Unit Price | Monthly |
|---------|------|-----|------------|---------|
| EC2 | t3.medium | 2 | $0.0416/hr | $61 |
| RDS | db.t3.medium Multi-AZ | 1 | $0.136/hr | $99 |
| EKS | Cluster | 1 | $0.10/hr | $73 |
| S3 | Standard 500GB | 1 | $0.023/GB | $12 |
| ALB | 1 LCU avg | 1 | $0.008/LCU-hr | $6 |
| Data Transfer | 100GB egress | - | $0.09/GB | $9 |
| **TOTAL** | | | | **$260/mo** |

## Phase 4: Optimization Recommendations
- Reserved Instances / Savings Plans: 1-year commitment typically saves 30–40%
- Spot instances for non-critical workloads: up to 70% savings
- Right-sizing opportunities: any oversized instances
- Storage tier recommendations: S3 Intelligent-Tiering, lifecycle policies
- Data transfer optimization: CDN for static assets, VPC endpoints

## Phase 5: Cost at Scale
Project costs at 10×, 100× current load — identify the most expensive scaling dimensions.

## Output Format
```markdown
## Cost Estimate: [Architecture Name]
**Cloud**: AWS | **Region**: us-east-1
**Confidence**: LOW/MEDIUM/HIGH

### Monthly Estimate
Base cost: $X/mo
With 1-yr reserved: $Y/mo (Z% savings)

### Cost Breakdown Table
[table]

### Top Cost Drivers
1. [service] — $X/mo (N%)

### Optimization Opportunities
- [recommendation]: saves ~$X/mo

### Scaling Projections
| Load | Est. Monthly |
|------|-------------|
| 1× (current) | $X |
| 10× | $Y |
| 100× | $Z |
```

## Error Handling
- Vague architecture: ask for clarification on instance types and scale
- Unknown service: use comparable service pricing and note the assumption
