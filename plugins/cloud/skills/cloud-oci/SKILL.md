---
name: cloud-oci
description: OCI tenancy structure, compartments, OKE, Autonomous Database, Object Storage, IAM policies, Terraform for OCI, and cost management
---

# OCI Cloud

Mastery of this skill enables you to design and deploy Oracle Cloud Infrastructure following OCI best practices, with compartment-based governance, managed Kubernetes, and Autonomous Database.

## When to Use This Skill
- Designing OCI infrastructure for a new workload
- Writing Terraform for OCI resources
- Configuring OCI IAM policies and compartments
- Using Autonomous Database for data workloads
- Setting up OKE (Oracle Kubernetes Engine)

## Core Concepts

### 1. OCI Tenancy Structure
```
Tenancy (root compartment)
└── Compartments (recursive hierarchy)
    ├── Production compartment
    │   ├── Networking compartment
    │   ├── Compute compartment
    │   └── Database compartment
    └── Non-Production compartment
```

Compartments are the primary unit of isolation and access control. Use them to separate environments, teams, and cost centers.

### 2. Key OCI Services
| Need | OCI Service | Equivalent |
|------|-------------|-----------|
| Container orchestration | OKE | GKE/EKS/AKS |
| Serverless functions | OCI Functions | Lambda |
| Managed DB | Autonomous Database | Aurora Serverless |
| Object storage | Object Storage | S3 |
| Block storage | Block Volume | EBS |
| CDN | OCI CDN | CloudFront |
| Load balancing | Load Balancer | ALB |
| Message queue | OCI Queue / Streaming | SQS / Kinesis |
| DNS | OCI DNS | Route 53 |

### 3. IAM Model
OCI uses **policies** written in plain English:
```
Allow group Developers to manage all-resources in compartment Production
Allow service OKE to manage all-resources in compartment Production
```

## Quick Reference
```bash
# OCI CLI
oci iam compartment list --all
oci compute instance list --compartment-id <ocid>
oci ce cluster list --compartment-id <ocid>

# Terraform provider
terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 5.0"
    }
  }
}

provider "oci" {
  region = var.region
  # Uses OCI_CLI_PROFILE or instance principal in cloud
}
```

## Key Patterns

### Pattern 1: OKE Cluster (Terraform)
```hcl
resource "oci_containerengine_cluster" "prod" {
  compartment_id     = var.compartment_id
  kubernetes_version = "v1.29.1"
  name               = "prod-cluster"
  vcn_id             = oci_core_vcn.prod.id

  endpoint_config {
    is_public_ip_enabled = false
    subnet_id            = oci_core_subnet.api_endpoint.id
  }

  options {
    service_lb_subnet_ids = [oci_core_subnet.lb.id]
    add_ons {
      is_kubernetes_dashboard_enabled = false
      is_tiller_enabled               = false
    }
  }
}

resource "oci_containerengine_node_pool" "general" {
  cluster_id         = oci_containerengine_cluster.prod.id
  compartment_id     = var.compartment_id
  kubernetes_version = "v1.29.1"
  name               = "general"

  node_shape = "VM.Standard.E4.Flex"
  node_shape_config {
    ocpus         = 4
    memory_in_gbs = 16
  }

  node_config_details {
    size = 3
    placement_configs {
      availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
      subnet_id           = oci_core_subnet.workers.id
    }
  }
}
```

### Pattern 2: IAM Policy Examples
```
# Allow a group to manage compute in a compartment
Allow group ComputeAdmins to manage instance-family in compartment Production

# Allow OKE to use networking resources
Allow service OKE to manage all-resources in tenancy

# Dynamic group for instances to access Object Storage
Allow dynamic-group BackendInstances to read objects in compartment Production
where target.bucket.name = 'app-assets'

# Tag-based access control
Allow group Developers to manage all-resources in compartment Dev
where target.resource.tag.Environment = 'dev'
```

### Pattern 3: Autonomous Database Connection
```python
import oracledb

# Using wallet (mTLS)
conn = oracledb.connect(
    user="app_user",
    password=os.environ["DB_PASSWORD"],
    dsn="prod_high",  # from tnsnames.ora in wallet
    config_dir="/path/to/wallet",
    wallet_location="/path/to/wallet",
    wallet_password=os.environ["WALLET_PASSWORD"]
)

# Or using connection string directly (TLS without wallet)
conn = oracledb.connect(
    user="app_user",
    password=os.environ["DB_PASSWORD"],
    dsn="(description=(retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.region.oraclecloud.com))(connect_data=(service_name=xxx_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))"
)
```

## Best Practices
1. Use compartment hierarchy to mirror org structure (BU → env → service)
2. Tag all resources with `Environment`, `Team`, `Service` for cost tracking
3. Use instance principals for compute-to-OCI-service auth (no credentials)
4. Enable OCI Audit service on the tenancy — free and valuable for compliance
5. Use Autonomous Database for most relational workloads — reduced ops burden
6. OKE: use node pool autoscaling + OCI cluster autoscaler
7. Set budget alerts at 80% of monthly allocation per compartment

## Common Issues
- **OKE worker nodes not joining**: check Security List rules allow port 6443 from workers to API endpoint subnet
- **Autonomous DB connection timeout**: verify wallet is valid; check Autonomous DB MTLS setting vs TLS-only
- **IAM policy not taking effect**: OCI IAM has eventual consistency (~30s); wait and retry
- **Cost spike from data transfer**: OCI charges for egress; use Object Storage for large data movement between services
