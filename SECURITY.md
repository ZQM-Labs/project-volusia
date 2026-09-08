# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.x     | ✅ Yes    |

## Reporting a Vulnerability

If you discover a security vulnerability in Project Volusia, please report it responsibly:

1. **Email**: Send details to security@zqm-computing.io
2. **GitHub Security Advisory**: Use the [Security tab](https://github.com/ZQM-Labs/project-volusia/security/advisories/new) on GitHub

Please **do NOT** open public issues for security vulnerabilities.

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Investigation**: Within 7 days
- **Fix or Mitigation**: Within 30 days (depending on severity)

## Security Measures

Project Volusia implements the following security measures:

- **Rate Limiting**: API endpoints are rate limited to prevent abuse
- **Input Validation**: All API inputs are validated and sanitized
- **Parameterized Queries**: SQL queries use parameterized statements to prevent injection
- **CORS**: Configurable Cross-Origin Resource Sharing restrictions
- **Dependency Scanning**: Automated weekly scans with Dependabot
- **Security Scanning**: Bandit static analysis and Safety vulnerability checks in CI

## API Keys

Some data sources require API keys. These are:

- Stored in environment variables (never committed to the repository)
- Validated at startup (see `config.py`)
- Rotated regularly

### Obtaining API Keys

| Source | Registration URL |
|--------|-----------------|
| Census | https://api.census.gov/data/key_signup.html |
| BLS | https://data.bls.gov/registrationEngine/ |
| BEA | https://apps.bea.gov/API/signup/index.cfm |

## Data Privacy

Project Volusia only collects publicly available data. No personal data is stored or processed.
