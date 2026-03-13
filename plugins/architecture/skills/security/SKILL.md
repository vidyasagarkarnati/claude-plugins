---
name: security
description: OWASP Top 10, STRIDE threat modeling, input validation patterns, secrets management, JWT best practices, and TLS/HTTPS configuration
---

# Security

Mastery of this skill enables you to identify and remediate security vulnerabilities, design secure systems from the ground up, and communicate risk clearly using industry-standard frameworks.

## When to Use This Skill
- Reviewing code for security vulnerabilities
- Designing authentication and authorization systems
- Modeling threats for a new feature or system
- Handling secrets, credentials, and sensitive data
- Assessing security compliance requirements

## Core Concepts

### 1. OWASP Top 10 (2021)
1. **Broken Access Control** — Most common; enforce authz server-side
2. **Cryptographic Failures** — Protect data at rest and in transit
3. **Injection** — Parameterize all queries
4. **Insecure Design** — Threat model early
5. **Security Misconfiguration** — No defaults, disable unused features
6. **Vulnerable Components** — Audit dependencies regularly
7. **Auth Failures** — MFA, rate limiting, secure session management
8. **Data Integrity Failures** — Verify signatures on serialized data
9. **Logging Failures** — Log auth events and anomalies
10. **SSRF** — Validate and restrict outbound requests

### 2. STRIDE Threat Model
| Category | Description | Example |
|----------|-------------|---------|
| **S**poofing | Impersonating a user/system | JWT forgery |
| **T**ampering | Modifying data or code | SQL injection |
| **R**epudiation | Denying an action | Missing audit log |
| **I**nformation Disclosure | Exposing secrets | Verbose error messages |
| **D**enial of Service | Making system unavailable | No rate limiting |
| **E**levation of Privilege | Gaining unauthorized access | IDOR, BOLA |

## Quick Reference
```bash
# Check for secrets in code
git log -p | grep -i "password\|secret\|api_key\|token"

# Dependency audit
npm audit --audit-level=high
pip-audit
go list -m -json all | nancy sleuth

# HTTPS headers check
curl -I https://yourapp.com | grep -E "Strict-Transport|Content-Security|X-Frame"
```

## Key Patterns

### Pattern 1: Input Validation (Python/Pydantic)
```python
from pydantic import BaseModel, EmailStr, Field
from typing import Literal

class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100, pattern=r'^[a-zA-Z\s]+$')
    role: Literal['user', 'admin']
    age: int = Field(ge=0, le=150)

# MongoDB — parameterized queries only
# NEVER: collection.find({"name": user_input})
# ALWAYS:
collection.find({"name": {"$eq": user_input}})
```

### Pattern 2: JWT Best Practices
```javascript
// Signing — use RS256 for public verification, HS256 for internal
const token = jwt.sign(
  { sub: userId, role: user.role, iat: Math.floor(Date.now()/1000) },
  privateKey,
  { algorithm: 'RS256', expiresIn: '15m' }  // short expiry
);

// Verification — always verify signature AND claims
const decoded = jwt.verify(token, publicKey, {
  algorithms: ['RS256'],
  audience: 'https://api.example.com',
  issuer: 'https://auth.example.com'
});
```

### Pattern 3: Webhook Signature Verification
```python
import hmac, hashlib

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(f"sha256={expected}", signature)
```

### Pattern 4: Secrets Management
```bash
# AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id prod/myapp/db-password

# Never in code:
DB_PASSWORD = "hardcoded"  # ❌

# Always from environment or secrets manager:
DB_PASSWORD = os.environ["DB_PASSWORD"]  # ✅
```

## Best Practices
1. Never log PII, tokens, passwords, or full request bodies with sensitive fields
2. Hash passwords with bcrypt (cost ≥ 12) or Argon2 — never MD5/SHA1
3. Implement rate limiting on all auth endpoints (5 attempts/15 min)
4. Use `httpOnly; Secure; SameSite=Strict` for cookies
5. Add CSP, HSTS, X-Frame-Options headers on all responses
6. Rotate secrets regularly; design for rotation from day 1
7. Separate credentials per environment — dev/staging/prod never share

## Common Issues
- **Hardcoded secret found in git history** → Rotate immediately; use `git filter-branch` or BFG to purge; audit all systems that used it
- **Missing authorization check on API** → Every route handler must verify the caller has permission to that specific resource (BOLA)
- **Verbose error messages leaking stack traces** → Return generic errors to clients; log full details server-side only
