---
name: cloud-aws
description: AWS Well-Architected Framework, key services (EC2, ECS, EKS, RDS, S3, Lambda), IAM patterns, CDK/Terraform, multi-account strategy, and cost optimization
---

# AWS Cloud

Mastery of this skill enables you to design, deploy, and optimize AWS infrastructure following the Well-Architected Framework, with production-ready IaC and security best practices.

## When to Use This Skill
- Designing AWS infrastructure for a new service
- Writing Terraform or CDK for AWS resources
- Reviewing IAM policies or security configurations
- Optimizing AWS costs
- Planning multi-account landing zone architecture

## Core Concepts

### 1. Well-Architected Framework (6 Pillars)
1. **Operational Excellence**: IaC, runbooks, observability
2. **Security**: least privilege IAM, encryption everywhere, audit logging
3. **Reliability**: multi-AZ, auto-scaling, backups, chaos testing
4. **Performance Efficiency**: right instance types, caching, CDN
5. **Cost Optimization**: reserved capacity, rightsizing, waste elimination
6. **Sustainability**: efficient resource usage, reduce carbon footprint

### 2. Key Service Decision Matrix
| Need | Service | Alternative |
|------|---------|-------------|
| Container orchestration | EKS | ECS (simpler) |
| Serverless containers | Fargate | Lambda (stateless only) |
| Relational DB | RDS Aurora | RDS PostgreSQL/MySQL |
| Document DB | DocumentDB | MongoDB Atlas |
| Caching | ElastiCache Redis | DAX (DynamoDB only) |
| Message queue | SQS | EventBridge (routing) |
| Event streaming | MSK (Kafka) | Kinesis |
| Static hosting | S3 + CloudFront | Amplify |

## Quick Reference
```bash
# AWS CLI essentials
aws sts get-caller-identity  # confirm current account/role
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name,InstanceType]' --output table
aws s3 ls s3://bucket-name/ --recursive --human-readable

# EKS
aws eks update-kubeconfig --name cluster-name --region us-east-1
kubectl get nodes

# Cost
aws ce get-cost-and-usage --time-period Start=2026-03-01,End=2026-03-31 --granularity MONTHLY --metrics UnblendedCost
```

## Key Patterns

### Pattern 1: IAM Least Privilege (Terraform)
```hcl
# Service role for Lambda — only what it needs
resource "aws_iam_role" "lambda_exec" {
  name = "order-processor-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  role = aws_iam_role.lambda_exec.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
        Resource = aws_sqs_queue.orders.arn
      },
      {
        Effect = "Allow"
        Action = ["dynamodb:GetItem", "dynamodb:PutItem"]
        Resource = aws_dynamodb_table.orders.arn
      }
    ]
  })
}
```

### Pattern 2: VPC Design
```
/16 VPC (e.g., 10.0.0.0/16)
├── Public subnets (one per AZ): 10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24
│   └── ALB, NAT Gateway, Bastion
├── Private subnets (one per AZ): 10.0.11.0/24, 10.0.12.0/24, 10.0.13.0/24
│   └── EKS nodes, EC2, Lambda in VPC
└── Database subnets (one per AZ): 10.0.21.0/24, 10.0.22.0/24, 10.0.23.0/24
    └── RDS, ElastiCache (no internet access)
```

### Pattern 3: EKS Cluster (CDK)
```typescript
import * as eks from 'aws-cdk-lib/aws-eks';

const cluster = new eks.Cluster(this, 'ProdCluster', {
  version: eks.KubernetesVersion.V1_29,
  defaultCapacity: 0,  // manage node groups separately
  endpointAccess: eks.EndpointAccess.PRIVATE,  // no public endpoint
});

cluster.addNodegroupCapacity('general', {
  instanceTypes: [ec2.InstanceType.of(ec2.InstanceClass.M5, ec2.InstanceSize.XLARGE)],
  minSize: 2,
  maxSize: 10,
  desiredSize: 3,
  amiType: eks.NodegroupAmiType.AL2_X86_64,
});
```

## Best Practices
1. All infrastructure in IaC (Terraform or CDK) — no manual console changes
2. Use AWS Organizations + SCPs for account-level guardrails
3. Enable CloudTrail, Config, and GuardDuty in all regions from day 1
4. Never use root account credentials; use IAM Identity Center for human access
5. VPC endpoints for S3 and DynamoDB to avoid NAT Gateway costs
6. Enable S3 server-side encryption and versioning on all buckets
7. Use Secrets Manager (not SSM Parameter Store) for secrets

## Common Issues
- **NAT Gateway cost spike**: check if private subnet resources are downloading large packages; add VPC endpoints
- **EKS node out of capacity**: check both node count AND CPU/memory; add Cluster Autoscaler
- **IAM permission denied**: use CloudTrail event history to find exact action that was denied
