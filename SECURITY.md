# Security Policy

## Supported Versions

| Version       | Supported          |
| ------------- | ------------------ |
| 0.3.x         | :white_check_mark: |
| < 0.3.0       | :x:                |

## Reporting a Vulnerability

We take security seriously at Satya_AI. If you discover a security vulnerability, please report it privately via email instead of opening a public issue.

### How to Report

Please send your report to:

**Email:** contact@anktechsol.com

Include the following details:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if any)

### What to Expect

- We will acknowledge receipt of your report within **48 hours**
- We will investigate and provide an initial assessment within **5 business days**
- We will keep you informed of our progress throughout the process
- Once a fix is deployed, we will credit you in our security advisory (unless you prefer to remain anonymous)

### Security Focus Areas

Given Satya's agent-authentication model, we are particularly interested in:
- Token and signature validation vulnerabilities
- Agent key exposure or leakage
- Audit log tampering or bypass
- SQL injection in the SQLite backend
- SSRF or command injection via agent tasks

Thank you for helping keep Satya_AI secure!
