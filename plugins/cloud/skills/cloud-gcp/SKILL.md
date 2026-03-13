---
name: cloud-gcp
description: GCP resource hierarchy, key services (GKE, Cloud Run, Cloud SQL, BigQuery, Pub/Sub), Terraform for GCP, IAM, VPC Service Controls, and cost optimization
---

# GCP Cloud

Mastery of this skill enables you to design and deploy GCP infrastructure following Google's best practices, with strong IAM, networking, and cost governance patterns.

## When to Use This Skill
- Designing GCP infrastructure for a new service
- Writing Terraform for GCP resources
- Configuring GCP IAM and service accounts
- Using BigQuery for analytics workloads
- Setting up VPC Service Controls for data security

## Core Concepts

### 1. GCP Resource Hierarchy
```
Organization
└── Folders (environments, business units)
    └── Projects
        └── Resources
```
IAM policies inherit downward — set at the highest applicable level.

### 2. Key Service Decisions
| Need | Service | Notes |
|------|---------|-------|
| Container orchestration | GKE | Managed Kubernetes |
| Serverless containers | Cloud Run | Scale-to-zero, simpler |
| Serverless functions | Cloud Functions | Event-driven |
| Relational DB | Cloud SQL | PostgreSQL/MySQL/SQL Server |
| Data warehouse | BigQuery | Serverless, petabyte-scale |
| Message queue | Pub/Sub | At-least-once delivery |
| CDN | Cloud CDN + Load Balancer | Global anycast |
| Object storage | Cloud Storage | S3 equivalent |

## Quick Reference
```bash
# gcloud CLI
gcloud config set project my-project-id
gcloud auth application-default login

# GKE
gcloud container clusters get-credentials cluster-name --region us-central1
kubectl get nodes

# BigQuery
bq query --use_legacy_sql=false 'SELECT COUNT(*) FROM `project.dataset.table`'

# Cost
gcloud billing accounts list
gcloud beta billing budgets list --billing-account=BILLING_ACCOUNT_ID
```

## Key Patterns

### Pattern 1: GKE Cluster (Terraform)
```hcl
resource "google_container_cluster" "prod" {
  name     = "prod-cluster"
  location = "us-central1"
  project  = var.project_id

  remove_default_node_pool = true
  initial_node_count       = 1

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }
}

resource "google_container_node_pool" "general" {
  name       = "general"
  cluster    = google_container_cluster.prod.name
  location   = "us-central1"
  node_count = 3

  node_config {
    machine_type = "e2-standard-4"
    disk_size_gb = 50
    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    workload_metadata_config { mode = "GKE_METADATA" }
  }

  autoscaling {
    min_node_count = 2
    max_node_count = 10
  }
}
```

### Pattern 2: Workload Identity (App → GCP Services)
```bash
# Create GCP service account
gcloud iam service-accounts create app-backend \
  --display-name="Backend App Service Account"

# Grant it Cloud SQL access
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:app-backend@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

# Bind Kubernetes service account to GCP SA
gcloud iam service-accounts add-iam-policy-binding app-backend@PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="serviceAccount:PROJECT_ID.svc.id.goog[default/backend-ksa]"
```

### Pattern 3: BigQuery Cost-Efficient Patterns
```sql
-- Use column pruning — only select needed columns
SELECT user_id, event_type, created_at  -- NOT SELECT *
FROM `project.analytics.events`
WHERE DATE(created_at) = CURRENT_DATE()

-- Partition pruning — filter on partition column
WHERE DATE(created_at) BETWEEN '2026-01-01' AND '2026-03-31'

-- Clustering for frequent filter patterns
CREATE TABLE analytics.events
PARTITION BY DATE(created_at)
CLUSTER BY user_id, event_type
AS SELECT ...
```

## Best Practices
1. Use Workload Identity instead of service account key files
2. Apply organization-level policies (org constraints) for baseline security
3. Enable VPC Service Controls for sensitive projects (data, production)
4. Use Cloud Armor for WAF protection on external load balancers
5. Enable Cloud Audit Logs (Admin Activity, Data Access) from day 1
6. Set BigQuery slot reservations for predictable cost; use on-demand for dev
7. Use committed use discounts for steady-state GKE and Cloud SQL

## Common Issues
- **GKE pod can't access GCP APIs**: check Workload Identity binding; verify K8s SA annotation
- **BigQuery cost spike**: check for full-table scans; add partition/cluster filters; use `INFORMATION_SCHEMA.JOBS` to find expensive queries
- **Cloud SQL connection errors**: ensure Cloud SQL Auth Proxy is running or use Cloud SQL connector
