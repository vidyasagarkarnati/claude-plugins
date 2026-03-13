---
name: cloud-azure
description: Azure Well-Architected Framework, key services (AKS, Azure SQL, App Service, Functions), Bicep/Terraform, Entra ID, landing zones, and cost management
---

# Azure Cloud

Mastery of this skill enables you to design, deploy, and govern Azure infrastructure following the Well-Architected Framework, with production-ready IaC and Azure-native security patterns.

## When to Use This Skill
- Designing Azure infrastructure for a new service
- Writing Bicep or Terraform for Azure resources
- Configuring Entra ID (Azure AD) and RBAC
- Setting up Azure landing zones
- Optimizing Azure costs

## Core Concepts

### 1. Azure Resource Hierarchy
```
Tenant (Entra ID)
└── Management Groups
    └── Subscriptions
        └── Resource Groups
            └── Resources
```

### 2. Key Service Decision Matrix
| Need | Service | Notes |
|------|---------|-------|
| Container orchestration | AKS | Managed Kubernetes |
| Serverless containers | Container Apps | Simpler than AKS |
| Serverless functions | Azure Functions | Event-driven |
| Relational DB | Azure SQL / PostgreSQL Flexible | Managed SQL |
| Caching | Azure Cache for Redis | Redis-compatible |
| Message queue | Service Bus | Enterprise messaging |
| Event streaming | Event Hubs | Kafka-compatible |
| CDN + WAF | Azure Front Door | Global load balancing |

## Quick Reference
```bash
# Azure CLI
az account show                    # current subscription
az group list --output table       # list resource groups
az aks get-credentials --resource-group rg-prod --name aks-prod

# Cost
az consumption usage list --start-date 2026-03-01 --end-date 2026-03-31

# Entra ID
az ad user list --filter "displayName eq 'John Smith'"
az role assignment list --assignee user@company.com
```

## Key Patterns

### Pattern 1: Bicep Resource Group + AKS
```bicep
// main.bicep
targetScope = 'subscription'

param location string = 'eastus'
param environment string = 'prod'

resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: 'rg-platform-${environment}'
  location: location
  tags: {
    Environment: environment
    Team: 'platform'
    ManagedBy: 'bicep'
  }
}

module aks 'modules/aks.bicep' = {
  name: 'aks-deployment'
  scope: rg
  params: {
    clusterName: 'aks-${environment}'
    location: location
    nodeCount: 3
    vmSize: 'Standard_D4s_v3'
  }
}
```

### Pattern 2: Terraform for Azure
```hcl
resource "azurerm_kubernetes_cluster" "prod" {
  name                = "aks-prod"
  location            = azurerm_resource_group.prod.location
  resource_group_name = azurerm_resource_group.prod.name
  dns_prefix          = "aks-prod"

  default_node_pool {
    name            = "system"
    node_count      = 3
    vm_size         = "Standard_D4s_v3"
    os_disk_size_gb = 50
    vnet_subnet_id  = azurerm_subnet.aks.id
  }

  identity { type = "SystemAssigned" }

  network_profile {
    network_plugin = "azure"
    network_policy = "calico"
  }

  tags = { Environment = "prod" }
}
```

### Pattern 3: Entra ID RBAC Pattern
```bash
# Create custom role with least privilege
az role definition create --role-definition '{
  "Name": "App Secrets Reader",
  "Description": "Read secrets from Key Vault",
  "Actions": [],
  "NotActions": [],
  "DataActions": ["Microsoft.KeyVault/vaults/secrets/getSecret/action"],
  "AssignableScopes": ["/subscriptions/{subId}/resourceGroups/rg-prod"]
}'

# Assign managed identity to role
az role assignment create \
  --assignee <managed-identity-object-id> \
  --role "App Secrets Reader" \
  --scope /subscriptions/{subId}/resourceGroups/rg-prod/providers/Microsoft.KeyVault/vaults/kv-prod
```

## Best Practices
1. Use Management Groups + Azure Policy for tenant-wide guardrails
2. Enable Microsoft Defender for Cloud on all subscriptions
3. Use Managed Identities for app-to-service auth (no credentials)
4. Enable Azure Monitor + Log Analytics workspace from day 1
5. Use Azure Private Endpoints for PaaS services (no public exposure)
6. Enable Diagnostic Settings on all resources to send logs to Log Analytics
7. Tag everything: Environment, Team, Service, CostCenter

## Common Issues
- **AKS node not joining cluster**: check NSG rules allow required ports; check kubelet identity permissions
- **Key Vault access denied**: verify Managed Identity has the Key Vault role + RBAC mode enabled (not access policies)
- **Cost anomaly**: check for orphaned public IPs, unused App Service Plans, and over-provisioned Premium storage
