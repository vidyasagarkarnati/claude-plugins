---
name: architecture
description: System design patterns, scalability strategies, C4 diagrams, ADR format, and API design principles for building resilient distributed systems
---

# Architecture

Mastery of this skill enables you to design systems that are scalable, maintainable, and aligned with business goals. You can evaluate trade-offs between architectural styles, document decisions formally, and communicate designs clearly using standard notation.

## When to Use This Skill
- Designing a new service, platform, or system from scratch
- Evaluating whether to break a monolith into microservices
- Documenting an architectural decision that will be hard to reverse
- Reviewing a proposal for scalability or reliability concerns
- Defining API contracts between teams or services

## Core Concepts

### 1. Architectural Styles
**Microservices**: Independent deployable services, each owning its data store. Best when teams are large and domains are distinct.

**Event-Driven (EDA)**: Services communicate via events on a broker (Kafka, SNS/SQS). Decouples producers from consumers; enables replay and audit trails.

**CQRS**: Separate write (command) and read (query) models. Eliminates read/write contention; enables optimized projections.

**Hexagonal (Ports & Adapters)**: Core domain logic isolated from infrastructure. Adapters plug in (HTTP, DB, queue). Maximizes testability.

### 2. Scalability Dimensions
- Horizontal scaling: stateless services + load balancers
- Data partitioning: sharding (hash vs range)
- Caching: L1 (in-process) → L2 (Redis) → CDN (edge)
- Async processing: queues + workers for non-blocking operations

### 3. C4 Model
- **Context (L1)**: System and users/external systems
- **Container (L2)**: Apps, databases, queues inside the system
- **Component (L3)**: Internal structure of a container
- **Code (L4)**: Class diagrams (usually generated)

## Quick Reference

| Pattern | Use When | Trade-off |
|---------|----------|-----------|
| Microservices | Large teams, independent scaling | Operational complexity |
| Monolith | Small team, early stage | Hard to scale selectively |
| Event-driven | Loose coupling, audit needed | Eventual consistency |
| CQRS | High read/write imbalance | Two models to maintain |
| Saga | Distributed transactions | Complex rollback logic |

**CAP Theorem**: Pick 2 of: Consistency, Availability, Partition Tolerance.

## Key Patterns

### Pattern 1: RESTful API Design
```
# Resource naming: nouns, plural, hierarchical
GET    /orders              # list (paginated)
POST   /orders              # create
GET    /orders/{id}         # read
PATCH  /orders/{id}         # partial update
DELETE /orders/{id}         # delete

# Versioning
GET /v2/orders

# Pagination
GET /orders?cursor=abc&limit=50
# Response: { "data": [...], "meta": { "cursor": "xyz", "hasMore": true } }

# RFC 7807 Error Shape
{
  "type": "https://api.example.com/errors/not-found",
  "title": "Order not found",
  "status": 404,
  "detail": "No order with id=abc123 exists."
}
```

### Pattern 2: ADR Template
```markdown
## ADR-0012: Use Kafka for inter-service events

**Date**: 2025-01-15
**Status**: Accepted
**Deciders**: Platform team

### Context
Services need to communicate order state changes. REST callbacks are brittle.

### Decision
Adopt Apache Kafka as event backbone.

### Consequences
- (+) Consumers can replay events
- (+) Producer/consumer deploy independently
- (-) Operational burden of Kafka cluster
- (-) At-least-once delivery; consumers must be idempotent
```

### Pattern 3: Event-Driven Saga (Choreography)
```
OrderService → [order.created] → InventoryService
                              → [inventory.reserved] → PaymentService
                                                    → [payment.captured] → ShippingService

Rollback:
payment.failed → [payment.failed] → InventoryService → [inventory.released]
```

## Best Practices
1. Choose boring technology — proven tools over exotic ones
2. Design for failure: every network call will fail eventually
3. Make services idempotent so retries are safe
4. Services small enough to be rewritten in two weeks
5. Own your data — no two services share the same table
6. Write ADRs only for decisions that are hard to reverse
7. Start modular monolith; extract microservices when pain is proven
8. Define SLOs before choosing infrastructure

## Common Issues
- **Distributed monolith** (microservices sharing DB) → Each service owns its schema; communicate via API or events only
- **Chatty microservices** causing latency spikes → Use BFF aggregation or async events
- **No rollback plan for migrations** → Use expand-contract pattern (add column → migrate → drop old)
