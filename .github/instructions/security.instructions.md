---
applyTo: "**"
---

# Security Instructions

## Non-Negotiables (Always Enforce)
- **Never commit secrets**: no API keys, passwords, tokens, or connection strings in code
- **Never log PII**: no emails, names, phone numbers, SSNs in logs
- **Never trust user input**: validate and sanitize at every system boundary
- **Always use parameterized queries**: never string-concatenate SQL or MongoDB queries
- **Always verify webhook signatures**: HMAC-SHA256 before processing any webhook

## Authentication & Authorization
- Use established auth libraries — never roll your own crypto
- JWT: short expiry (15 min access, 7 day refresh), verify signature and claims
- RBAC: check permissions at the service layer, not just the API gateway
- Rate limit all auth endpoints: max 5 failed attempts before lockout
- Use `httpOnly` + `Secure` + `SameSite=Strict` for session cookies

## Input Validation
```python
# Always validate at boundaries
from pydantic import BaseModel, EmailStr

class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    role: Literal['user', 'admin']
```

## Secrets Management
- Use environment variables or a secrets manager (AWS Secrets Manager, Azure Key Vault)
- Rotate secrets regularly — design for rotation from day 1
- Use different credentials per environment (dev/staging/prod never share secrets)

## OWASP Top 10 Reminders
1. **Injection**: Always parameterize queries
2. **Broken Auth**: Use MFA, short-lived tokens
3. **Sensitive Data**: Encrypt at rest (AES-256) and in transit (TLS 1.3)
4. **XXE**: Disable external entity processing in XML parsers
5. **Access Control**: Deny by default, explicit allow
6. **Misconfiguration**: No default credentials, disable unused features
7. **XSS**: Escape output, use CSP headers
8. **Insecure Deserialization**: Validate serialized data, use allow-lists
9. **Known Vulnerabilities**: Run `npm audit` / `pip-audit` in CI
10. **Insufficient Logging**: Log auth events, access denials, and anomalies

## Supply Chain
- Pin dependency versions in production
- Run dependency audit in every PR
- Review changelogs before major upgrades
- Never install packages from untrusted sources
