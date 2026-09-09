# Security — Project Volusia

> Security practices and considerations for Project Volusia.

---

## Security Principles

1. **Least Privilege** — Services run with minimal permissions
2. **Defense in Depth** — Multiple layers of security
3. **Zero Trust** — Verify all requests
4. **Transparency** — Open source, auditable code

---

## Network Security

### Cloudflare Tunnel

- All traffic encrypted via HTTPS
- No direct exposure of backend servers
- DDoS protection via Cloudflare
- IP masking

### GitHub Pages

- HTTPS enforced
- CDN distribution
- No server-side code execution

---

## API Security

### CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting

- 100 requests/minute per IP
- 1000 requests/hour per IP
- Configurable via environment variables

### Input Validation

- All user inputs validated
- Parameterized SQL queries (no injection)
- Type checking on all API parameters

---

## Data Security

### At Rest

- SQLite database file permissions: 600
- No sensitive data stored (all public sources)
- Regular backups

### In Transit

- HTTPS for all API communications
- Certificate validation
- No plaintext credentials

---

## Authentication

Currently, the API is open (no authentication required). For production deployments requiring authentication:

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

@app.get("/api/protected")
async def protected_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Verify token
    return {"status": "authenticated"}
```

---

## Vulnerability Reporting

To report a security vulnerability:

1. Email: zqmcomputing@gmail.com
2. Include: Description, steps to reproduce, impact
3. Do NOT open a public issue

---

## Dependencies

Regular dependency updates via Dependabot:

| Package | Current | Latest |
|---------|---------|--------|
| fastapi | 0.115.x | Check Dependabot |
| uvicorn | 0.30.x | Check Dependabot |
| react | 18.3.x | Check Dependabot |

---

**Last Updated**: 2026-09-08
**Maintainer**: ZQM Labs / ZQM Computing
