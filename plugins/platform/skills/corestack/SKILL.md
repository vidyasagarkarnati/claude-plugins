---
name: corestack
description: Corestack governance model, policy types (budget/compliance/security), blueprint configuration, approval workflows, and reporting
---

# Corestack

Mastery of this skill enables you to configure and use Corestack (now CoreStack, a cloud governance and management platform) for multi-cloud cost management, compliance enforcement, and operational governance.

## When to Use This Skill
- Configuring governance policies for cloud accounts
- Setting up budget alerts and cost guardrails
- Building compliance policy packs
- Configuring approval workflows for cloud provisioning
- Generating governance reports for auditors

## Core Concepts

### 1. Corestack Architecture
- **Tenant**: top-level organization unit
- **Account Groups**: groupings of cloud accounts (by BU, env, or region)
- **Cloud Accounts**: individual AWS/Azure/GCP/OCI accounts onboarded to Corestack
- **Blueprints**: reusable governance policy bundles
- **Policies**: individual rules (budget, compliance, security, operational)

### 2. Policy Types
| Type | Purpose | Example |
|------|---------|---------|
| **Budget** | Spending guardrails | Alert at 80% of monthly budget |
| **Compliance** | Regulatory controls | Ensure all S3 buckets have encryption |
| **Security** | Threat detection | Alert on root account login |
| **Operational** | Resource hygiene | Flag stopped instances > 7 days |

### 3. Approval Workflows
Corestack can gate cloud resource provisioning:
- **Self-service**: auto-approve within guardrails
- **Approval required**: routes to manager or FinOps team
- **Blocked**: prevents provisioning of non-compliant resource types

## Quick Reference
```
Corestack key concepts:
- Policy Pack = bundle of policies to apply to account groups
- Blueprint = policy pack + guardrails + default settings
- CSPM = Cloud Security Posture Management (compliance scanning)
- CWPP = Cloud Workload Protection Platform (runtime security)
- FinOps Dashboard = cost visibility, rightsizing, RI recommendations
```

## Key Patterns

### Pattern 1: Budget Policy Configuration
```json
{
  "policy_type": "budget",
  "name": "Monthly Budget Alert",
  "scope": "account_group",
  "target": "production-accounts",
  "rules": [
    {
      "threshold_percent": 80,
      "action": "notify",
      "recipients": ["finops@company.com", "team-lead@company.com"]
    },
    {
      "threshold_percent": 95,
      "action": "notify_and_restrict",
      "recipients": ["cto@company.com"],
      "restrict": ["new_ec2_instances", "new_rds_instances"]
    },
    {
      "threshold_percent": 100,
      "action": "notify_and_block",
      "recipients": ["cto@company.com", "finops@company.com"]
    }
  ]
}
```

### Pattern 2: Compliance Policy Pack (CIS AWS Benchmark)
```
Corestack Policy Pack: CIS AWS Foundations Benchmark v1.4

Key controls to enable:
- CIS 1.4: No root access key active
- CIS 1.10: MFA enabled for all IAM users with console access
- CIS 2.1.1: S3 buckets have server-side encryption enabled
- CIS 2.2.1: EBS volumes are encrypted
- CIS 3.1: CloudTrail is enabled in all regions
- CIS 4.1: No security groups allow unrestricted SSH (0.0.0.0:22)
- CIS 4.2: No security groups allow unrestricted RDP (0.0.0.0:3389)

Remediation: auto-remediate LOW findings; notify for MEDIUM; alert for HIGH
```

### Pattern 3: Governance Report Structure
```markdown
## Monthly Cloud Governance Report

### Executive Summary
- Cloud accounts monitored: 12 (3 AWS, 5 Azure, 4 GCP)
- Total spend MTD: $124,500
- Budget utilization: 78% (on track)
- Compliance score: 94% (↑ from 89% last month)

### Compliance Status
| Framework | Score | Critical Findings | Trend |
|-----------|-------|-------------------|-------|
| CIS AWS | 96% | 0 | ↑ |
| Azure Security Benchmark | 91% | 2 | → |
| SOC 2 | 94% | 0 | ↑ |

### Critical Findings (require immediate action)
1. [Azure] Storage account without encryption: storage-dev-001
   - Risk: CRITICAL | Remediation: Enable SSE | Owner: Platform Team

### Budget Alerts Triggered
| Account | Budget | Actual | % | Status |
|---------|--------|--------|---|--------|
| prod-aws-us | $50,000 | $43,000 | 86% | ⚠ Warning |

### Operational Issues
- Stopped EC2 instances > 7 days: 3 (costing $45/day in EBS)
- Unused load balancers: 2 ($36/day)
```

## Best Practices
1. Start with notification-only policies before enforcing blocks — avoids disrupting teams
2. Group accounts by environment and apply different policy strictness (prod stricter than dev)
3. Review compliance reports weekly, not monthly — critical findings accumulate fast
4. Integrate approval workflows with Jira/ServiceNow for audit trail
5. Export governance reports to S3 for long-term audit retention
6. Use Corestack blueprints for new account provisioning — ensures consistent baseline

## Common Issues
- **Too many alerts fatigue**: tune thresholds carefully; start at 80% budget, not 50%
- **Compliance score drops after new accounts added**: onboard with a baseline policy pack from day one
- **Approval workflow delays provisioning**: set SLA for approvals (e.g., 4-hour business hours SLA)
