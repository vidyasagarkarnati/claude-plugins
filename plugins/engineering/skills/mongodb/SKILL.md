---
name: mongodb
description: MongoDB document modeling, indexing strategies, aggregation pipelines, replica sets, Atlas configuration, and query optimization
---

# MongoDB

Mastery of this skill enables you to design performant MongoDB schemas, write efficient queries and aggregations, and configure MongoDB Atlas for production workloads.

## When to Use This Skill
- Designing a new MongoDB collection or schema
- Optimizing slow queries or aggregations
- Building aggregation pipelines for analytics
- Setting up indexes for a new query pattern
- Reviewing a schema for anti-patterns

## Core Concepts

### 1. Embed vs Reference
**Embed** (subdocument) when:
- Data is always accessed together ("has-a" relationship)
- Child data is small and bounded
- One-to-one or one-to-few relationships
- No independent access to child needed

**Reference** (foreign key) when:
- Data is accessed independently
- Many-to-many relationships
- Unbounded arrays (could grow forever)
- Child documents are large

### 2. Index Types
- **Single field**: `{ userId: 1 }` — basic equality/range
- **Compound**: `{ userId: 1, createdAt: -1 }` — multi-field queries
- **Text**: `{ description: "text" }` — full-text search
- **TTL**: `{ createdAt: 1 }, { expireAfterSeconds: 86400 }` — auto-expiry
- **Partial**: `{ status: 1 }, { partialFilterExpression: { status: "active" } }` — sparse indexes
- **2dsphere**: for geospatial queries

### 3. Aggregation Pipeline Stages
`$match` → `$lookup` → `$unwind` → `$group` → `$project` → `$sort` → `$limit`

## Quick Reference
```javascript
// Explain a query (check if index is used)
db.orders.find({ userId: "abc" }).explain("executionStats")
// Look for: IXSCAN (good) vs COLLSCAN (bad)

// Index on compound query pattern
db.orders.createIndex({ userId: 1, status: 1, createdAt: -1 })

// Atlas Search (full-text)
db.products.createIndex({ "$**": "text" })
```

## Key Patterns

### Pattern 1: Schema Design (Orders)
```javascript
// GOOD: embed order items (always accessed together, bounded count)
{
  _id: ObjectId("..."),
  userId: ObjectId("..."),     // reference to users collection
  status: "pending",
  items: [                      // embedded (bounded, co-accessed)
    { productId: ObjectId("..."), quantity: 2, price: 29.99 }
  ],
  total: 59.98,
  createdAt: ISODate("2026-01-15"),
  updatedAt: ISODate("2026-01-15")
}

// Indexes for common query patterns:
// List user's orders sorted by date
db.orders.createIndex({ userId: 1, createdAt: -1 })
// Filter by status
db.orders.createIndex({ userId: 1, status: 1 })
// Admin queries
db.orders.createIndex({ status: 1, createdAt: -1 })
```

### Pattern 2: Aggregation Pipeline
```javascript
// Monthly revenue by product category
db.orders.aggregate([
  // Stage 1: Filter date range
  { $match: {
    createdAt: { $gte: ISODate("2026-01-01"), $lt: ISODate("2026-02-01") },
    status: "completed"
  }},
  // Stage 2: Unwind items array
  { $unwind: "$items" },
  // Stage 3: Join with products
  { $lookup: {
    from: "products",
    localField: "items.productId",
    foreignField: "_id",
    as: "product"
  }},
  { $unwind: "$product" },
  // Stage 4: Group by category
  { $group: {
    _id: "$product.category",
    revenue: { $sum: { $multiply: ["$items.quantity", "$items.price"] } },
    orderCount: { $addToSet: "$_id" }
  }},
  // Stage 5: Clean up output
  { $project: {
    category: "$_id",
    revenue: 1,
    orderCount: { $size: "$orderCount" }
  }},
  { $sort: { revenue: -1 } }
])
```

### Pattern 3: TTL Index (Session Expiry)
```javascript
// Sessions expire after 24 hours of inactivity
db.sessions.createIndex(
  { lastActivity: 1 },
  { expireAfterSeconds: 86400 }
)

// Update lastActivity on each request
db.sessions.updateOne(
  { _id: sessionId },
  { $set: { lastActivity: new Date() } }
)
```

### Pattern 4: Partial Index (Active Users Only)
```javascript
// Index only active users — smaller index, faster queries
db.users.createIndex(
  { email: 1 },
  {
    unique: true,
    partialFilterExpression: { status: "active" }
  }
)
```

## Best Practices
1. Always run `explain("executionStats")` on new queries — look for IXSCAN, not COLLSCAN
2. Compound index field order: equality first, range last, sort last
3. Avoid arrays of arrays — MongoDB indexes the outer array, not the inner
4. Use `$project` early in pipelines to reduce document size in memory
5. Cap collections at reasonable sizes — don't let arrays grow unbounded
6. Use `bulkWrite` for batch inserts/updates — far more efficient than loops
7. Atlas: enable Performance Advisor to get index suggestions automatically

## Common Issues
- **Slow query despite index**: check compound index field order; ESR rule (Equality, Sort, Range)
- **`$lookup` is slow**: add index on the `foreignField` of the joined collection
- **Large documents causing memory issues in aggregation**: add `$project` right after `$match` to trim fields early
- **Unbounded array growth**: switch from push-to-array to separate collection with reference
