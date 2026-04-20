# Satya AI

> Agentic Governance Framework — Programmable policy enforcement for AI agents.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI](https://img.shields.io/badge/PyPI-0.1.0-green.svg)](https://pypi.org/project/satya-ai/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

## What is Satya AI?
Satya AI is an open-source programmable layer to govern, observe, and enforce policy on AI agents and LLM-powered pipelines. It acts as an admission controller for your AI workloads, evaluating every action against predefined rules in real-time. Governance is treated as infrastructure, ensuring it is invisible at scale but auditable always.

## Why governance matters
- **Data Privacy:** Prevent accidental leakage of PII (Aadhaar, PAN) or proprietary data.
- **DPDP Act 2023:** Ensure compliance with the Digital Personal Data Protection Act by enforcing strict consent and redaction rules.
- **Regulated Sectors:** Maintain immutable audit logs for BFSI and healthcare applications.
- **Safety:** Block prompt injections, jailbreaks, and out-of-scope model behaviors before they hit the LLM provider.

## Quickstart

```bash
# 1. Clone the repository
git clone https://github.com/AnkTechsol/satya-ai.git
cd satya-ai

# 2. Set up environment
cp .env.example .env

# 3. Start the infrastructure
docker-compose up -d

# 4. View documentation
# Navigate to http://localhost:8000/docs
```

## Core concepts
- **Agents:** The entities performing actions (e.g., Customer Support Bot).
- **Policies:** Collections of rules attached to agents.
- **Rules:** Specific conditions (e.g., `contains_keyword`, `custom_regex`) that trigger actions (`ALLOW`, `DENY`, `REDACT`).
- **Audit Log:** An immutable ledger of every evaluation and decision made by the system.

```text
Incoming Request -> [ Interceptor ] -> [ Policy Engine ] -> (ALLOW | DENY | REDACT) -> LLM Provider
                                              |
                                              v
                                       [ Audit Logger ]
```

## API Reference
The full OpenAPI documentation is available at `/docs` when the server is running.

- `POST /v1/evaluate` - Core evaluation endpoint
- `POST /v1/policies` - Create a new policy
- `POST /v1/agents` - Register a new agent
- `GET /v1/audit/events` - Query the immutable audit log

## Deployment
Satya AI is designed to be self-hosted. Use the provided `docker-compose.yml` to spin up the FastAPI application alongside an asynchronous PostgreSQL database.

| Environment Variable | Description | Default |
|----------------------|-------------|---------|
| `SATYA_AGENT_KEYS` | Comma-separated API keys | `DEMO_KEY` |
| `AUDIT_SECRET` | Secret for audit logs | (Required) |
| `DATABASE_URL` | Async SQLAlchemy URL | SQLite fallback |

## Contributing
We welcome contributions! The most common contribution is adding new rule condition types.
1. Add the condition logic in `satya/core/policy_engine.py`
2. Update the Pydantic schema in `satya/schemas/policy.py`
3. Add a test in `tests/test_policy_engine.py`
4. Submit a Pull Request

## Roadmap
- **v0.2:** Redis queue for distributed audit logging, webhook alerts for rule violations.
- **v0.3:** Model Context Protocol (MCP) integration, SarvaData connector.

## License
Apache 2.0
