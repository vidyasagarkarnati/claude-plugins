---
applyTo: "**/*.test.ts,**/*.spec.ts,**/*.test.py,**/*_test.go,**/*.test.js"
---

# Testing Instructions

## Coverage Requirements
- Minimum **80% line coverage** for all new code
- Critical paths (auth, payments, data mutations) require **95%+**
- Run coverage check: `npm test -- --coverage` or `pytest --cov`

## Test Structure (AAA Pattern)
```
// Arrange
const user = createTestUser({ role: 'admin' });

// Act
const result = await service.doThing(user);

// Assert
expect(result.status).toBe('success');
```

## Unit Tests
- Test one behavior per test case
- Use descriptive names: `it('returns 404 when user not found')`
- Mock external dependencies (databases, APIs, filesystems)
- Keep tests fast (< 100ms each)
- No shared mutable state between tests

## Integration Tests
- Test the full request/response cycle
- Use a real test database (not mocks) for data layer tests
- Clean up test data in `afterEach`/`afterAll`
- Test happy path + common error scenarios

## E2E Tests (Playwright)
- Cover critical user journeys only (login, checkout, key workflows)
- Use `data-testid` attributes — never CSS class selectors
- Run against staging environment
- Keep suite under 10 minutes total

## Test Data
- Use factory functions, not hardcoded values
- Avoid relying on test execution order
- Use randomized IDs to prevent collisions

## What to Test
- Business logic functions
- API endpoints (status codes, response shapes, error cases)
- Auth/authorization boundaries
- Data validation
- Edge cases: empty inputs, nulls, boundary values

## What NOT to Test
- Third-party library internals
- Implementation details (private methods, internal state)
- Trivial getters/setters with no logic
