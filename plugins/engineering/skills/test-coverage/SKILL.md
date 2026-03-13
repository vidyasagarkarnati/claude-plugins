---
name: test-coverage
description: Coverage tools (Jest/nyc, pytest-cov, go test -cover), coverage report interpretation, test generation patterns, mocking strategies, and coverage thresholds
---

# Test Coverage

Mastery of this skill enables you to audit test coverage across multiple frameworks, generate targeted tests for low-coverage code, and establish coverage standards that catch real bugs rather than just padding percentages.

## When to Use This Skill
- Auditing a codebase for test coverage gaps
- Generating tests for existing untested code
- Setting up coverage tooling in a CI pipeline
- Determining which files need tests first (risk-based prioritization)
- Reviewing whether coverage thresholds are meaningful

## Core Concepts

### 1. Coverage Types
- **Line coverage**: every line executed? (most common, least rigorous)
- **Branch coverage**: every if/else branch taken? (catches more bugs)
- **Function coverage**: every function called?
- **Statement coverage**: every statement executed?

**Recommendation**: Use branch coverage as your primary metric — it's more meaningful than line coverage.

### 2. Coverage Thresholds
| Code Type | Minimum | Target |
|-----------|---------|--------|
| Business logic | 80% | 90%+ |
| Auth/payments/data mutations | 90% | 95%+ |
| Utility functions | 70% | 85%+ |
| Config/setup files | 0% | Skip |
| Generated code | 0% | Skip |

### 3. Risk-Based Prioritization
Prioritize coverage for files that are:
1. Changed frequently (git log --follow)
2. High cyclomatic complexity
3. Critical user paths (auth, payments, core data mutations)
4. Recently introduced bugs

## Quick Reference
```bash
# Jest
npx jest --coverage --collectCoverageFrom="src/**/*.ts"
# Config in jest.config.ts: coverageThreshold: { global: { branches: 80 } }

# pytest
pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Go
go test ./... -coverprofile=coverage.out
go tool cover -html=coverage.out -o coverage.html
go tool cover -func=coverage.out | sort -k3 -n | head -20  # lowest coverage first

# nyc (Istanbul) for Node
nyc --reporter=lcov --reporter=text npm test
```

## Key Patterns

### Pattern 1: Jest Coverage Setup
```typescript
// jest.config.ts
export default {
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.tsx',
    '!src/generated/**',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
    // Stricter for critical paths
    './src/auth/**/*.ts': {
      branches: 95,
      lines: 95,
    },
  },
  coverageReporters: ['text', 'lcov', 'html'],
};
```

### Pattern 2: Generating Tests for Uncovered Functions
```typescript
// Source: src/utils/price.ts
export function calculateDiscount(price: number, code: string): number {
  if (code === 'SAVE10') return price * 0.9;
  if (code === 'SAVE20') return price * 0.8;
  if (price > 100) return price * 0.95;  // ← UNTESTED BRANCH
  return price;
}

// Generated test covering all branches:
describe('calculateDiscount', () => {
  it('applies 10% discount for SAVE10', () => {
    expect(calculateDiscount(100, 'SAVE10')).toBe(90);
  });
  it('applies 20% discount for SAVE20', () => {
    expect(calculateDiscount(100, 'SAVE20')).toBe(80);
  });
  it('applies 5% discount for orders over $100 with no code', () => {
    expect(calculateDiscount(150, '')).toBe(142.5);  // ← the uncovered branch
  });
  it('returns original price for no discount conditions', () => {
    expect(calculateDiscount(50, '')).toBe(50);
  });
  it('handles zero price', () => {
    expect(calculateDiscount(0, 'SAVE10')).toBe(0);
  });
});
```

### Pattern 3: Mocking External Dependencies
```typescript
// Mock HTTP calls — don't call real APIs in unit tests
jest.mock('../services/stripe', () => ({
  createPaymentIntent: jest.fn().mockResolvedValue({
    id: 'pi_test_123',
    client_secret: 'test_secret',
    status: 'requires_payment_method'
  }),
}));

// Mock the database — use real DB for integration tests only
jest.mock('../db/orders', () => ({
  findById: jest.fn(),
  create: jest.fn(),
}));

// Reset mocks between tests
beforeEach(() => {
  jest.clearAllMocks();
});
```

## Best Practices
1. Measure branch coverage, not just line coverage — 100% lines but 60% branches means untested conditionals
2. Don't write tests just to hit a number — test behavior, not implementation
3. High coverage + no assertions = useless coverage. Require `expect` calls.
4. Exclude generated files, migrations, and config from coverage metrics
5. Run coverage in CI as a gate — never let it regress
6. For legacy code: set the current coverage as the floor, raise it incrementally
7. Prioritize mutation testing for critical paths when high coverage isn't enough

## Common Issues
- **Coverage passes but bugs slip through**: switch from line to branch coverage; add negative test cases
- **Coverage is slow in CI**: use `--changedSince main` in Jest to only test changed files in PR checks
- **Mocks making tests meaningless**: write integration tests for the seam between your code and external dependencies
- **100% coverage, still bugs**: coverage can't catch wrong business logic — add property-based testing with fast-check or hypothesis
