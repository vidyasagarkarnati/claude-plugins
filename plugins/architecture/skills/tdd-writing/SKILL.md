---
name: tdd-writing
description: Technical Design Document structure, C4 diagrams, API contract design, data model documentation, non-functional requirements, and ADR format
---

# TDD Writing

Mastery of this skill enables you to produce comprehensive Technical Design Documents that give engineers a complete blueprint for implementation, with clear API contracts, data models, and architectural decisions.

## When to Use This Skill
- Designing implementation for a non-trivial feature
- Creating API contracts between teams
- Documenting data model changes and migrations
- Writing Architecture Decision Records (ADRs)
- Reviewing a TDD for completeness and correctness

## Core Concepts

### 1. TDD Structure
1. **Overview & Goals** — what problem, what constraints, what success looks like
2. **Architecture Design** — which components, which patterns, why
3. **API Contracts** — exact request/response shapes
4. **Data Models** — schema + indexes + migrations
5. **Non-Functional Requirements** — performance, scalability, security
6. **Observability Plan** — metrics, logs, alerts
7. **Implementation Plan** — ordered tasks with estimates
8. **ADRs** — significant decisions made during design
9. **Open Questions** — unresolved items for the team

### 2. Non-Functional Requirements Template
| NFR | Target | Measurement |
|-----|--------|-------------|
| Latency | p99 < 200ms | APM (Datadog/New Relic) |
| Throughput | 1000 RPS | Load test with k6 |
| Availability | 99.9% | Uptime monitoring |
| Data retention | 7 years | Storage policy |
| RTO | < 4 hours | DR runbook |
| RPO | < 1 hour | Backup frequency |

## Quick Reference
```
Expand-contract migration pattern:
1. Add new column/field (backward compatible)
2. Deploy code that reads from both old + new
3. Backfill data to new column
4. Deploy code that reads from new only
5. Remove old column (separate deploy)

API versioning rules:
- PATCH version: bug fixes, no behavior change
- MINOR version: additive changes (new endpoints, new optional fields)
- MAJOR version: breaking changes (removed/renamed fields, changed behavior)
```

## Key Patterns

### Pattern 1: API Contract Documentation
```markdown
## POST /api/v1/orders

**Auth**: Bearer JWT (scope: orders:write)
**Rate limit**: 100 req/min per user

### Request
```json
{
  "items": [
    {
      "productId": "prod_abc123",    // required, string
      "quantity": 2,                  // required, int, min: 1, max: 100
      "customizations": {}            // optional, object
    }
  ],
  "shippingAddressId": "addr_xyz",   // required, string
  "couponCode": "SAVE20"             // optional, string
}
```

### Response — 201 Created
```json
{
  "id": "order_def456",
  "status": "pending",
  "items": [...],
  "total": 59.98,
  "estimatedDelivery": "2026-01-20",
  "createdAt": "2026-01-15T10:30:00Z"
}
```

### Error Responses
| Code | Error | Condition |
|------|-------|-----------|
| 400 | `invalid_quantity` | quantity < 1 or > 100 |
| 404 | `product_not_found` | productId doesn't exist |
| 409 | `insufficient_stock` | Requested qty exceeds available stock |
| 422 | `invalid_coupon` | Coupon expired or not applicable |
```

### Pattern 2: Data Model Documentation
```markdown
## Collection: orders

### Schema
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| _id | ObjectId | Yes | Auto-generated |
| userId | ObjectId | Yes | Reference to users collection |
| status | String | Yes | Enum: pending, confirmed, shipped, delivered, cancelled |
| items | Array | Yes | Embedded order items (max 50) |
| items[].productId | ObjectId | Yes | Reference to products |
| items[].quantity | Int | Yes | 1-100 |
| items[].price | Decimal | Yes | Price at time of order |
| total | Decimal | Yes | Sum of items |
| createdAt | Date | Yes | Auto-set |
| updatedAt | Date | Yes | Auto-updated |

### Indexes
```javascript
// Primary query patterns
db.orders.createIndex({ userId: 1, createdAt: -1 })   // user's order history
db.orders.createIndex({ userId: 1, status: 1 })        // filter by status
db.orders.createIndex({ status: 1, createdAt: -1 })    // admin order management
db.orders.createIndex({ createdAt: 1 }, { expireAfterSeconds: 220752000 }) // 7yr TTL
```

### Migration Plan
This is a new collection — no migration required.
```

### Pattern 3: ADR Template
```markdown
## ADR-0015: Use idempotency keys for payment API

**Date**: 2026-01-15
**Status**: Accepted
**Deciders**: Technical Architect, Full-Stack Lead

### Context
Network failures during payment processing can cause duplicate charges if clients retry requests.

### Decision
Require an `Idempotency-Key` header on all payment mutation endpoints. Store key + result in Redis with 24hr TTL. Return cached result for duplicate keys.

### Consequences
**Positive**:
- Clients can safely retry without risk of duplicate charges
- Reduces customer support tickets for duplicate charges

**Negative**:
- Redis dependency for payment endpoints
- Additional implementation complexity

**Risks**:
- Redis outage would block payment processing (mitigate: degrade gracefully, log warning)
```

## Best Practices
1. Write TDD before coding starts — design review is cheaper than code review
2. API contracts should be agreed upon by consuming team before implementation
3. Include rejected alternatives in ADRs — they prevent re-litigating decisions later
4. Mark NFRs as "target" not "goal" — they must be measurable and testable
5. Implementation plan should be executable tickets, not vague phases
6. Every migration plan needs a rollback step

## Common Issues
- **TDD approved but implementation diverges**: establish checkpoint reviews at API contract + data model phases
- **Missing error codes in API contract**: enumerate all error conditions before implementation to avoid inconsistency
- **ADR written after the fact**: decisions lose context; write ADRs during the decision, not after
