---
applyTo: "**/*.ts,**/*.tsx,**/*.py,**/*.go,**/*.java,**/*.cs"
---

# Architecture Instructions

## System Design Principles
- Follow the established architecture documented in `.claude/memory/project-state.md`
- All new services must align with the tech stack decisions in ADR log
- Prefer composition over inheritance
- Design for horizontal scalability by default
- Use event-driven patterns for cross-service communication

## API Design
- RESTful APIs: follow resource-oriented naming (`/users/{id}`, not `/getUser`)
- Use semantic HTTP methods: GET (read), POST (create), PUT (replace), PATCH (update), DELETE
- Always version APIs: `/api/v1/`, `/api/v2/`
- Return consistent error shapes: `{ "error": { "code": "...", "message": "...", "details": {} } }`
- Include pagination for list endpoints: `{ "data": [], "pagination": { "cursor": "...", "hasMore": true } }`

## Database Patterns
- MongoDB: embed for 1:1 and 1:few relationships; reference for 1:many and many:many
- Always add indexes for: query fields, sort fields, and foreign key references
- Use TTL indexes for session data and temporary records
- Include `createdAt` and `updatedAt` timestamps on all documents

## Code Organization
- Keep functions under 50 lines — if longer, extract into named helpers
- One file per logical module/class
- Co-locate tests with source: `feature.ts` + `feature.test.ts`
- Barrel exports (`index.ts`) for public module APIs

## Performance
- Cache aggressively at the edge (CDN) and application layer (Redis)
- Use database connection pooling
- Implement circuit breakers for external service calls
- Profile before optimizing — measure, don't guess
