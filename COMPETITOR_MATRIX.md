# Competitor Matrix

| Feature | Satya | LangSmith | Langfuse |
|---|---|---|---|
| Observability Depth | High (Log/Task level) | High (Token/Prompt level) | High (Token/Prompt level) |
| Agent Runtime Support | Native (Task Board/Chat) | API only | API only |
| Self-host Friendliness | Excellent (Zero infra, flat-file) | Complex (Docker/K8s) | Good (Docker) |
| Enterprise Features | **NEW: Durable Postgres/S3 Audit** | Full (SSO, RBAC, Audit) | Full (SSO, RBAC) |
| Export Adapters | **NEW: OTLP/Langfuse support** | N/A | N/A |
| Pricing Model | OSS | Managed (SaaS) | Managed / OSS |
| Agent Self-Testing | **Native (Harness/CI Integration)** | Custom via tests | Custom via tests |

## Strategic Gaps & Differentiators
*   **Where Satya wins:** Zero-infrastructure setup, native task tracking, flat-file architecture, human-observer paradigm, baked-in agent self-testing.
*   **Where Satya must catch up:** Deep trace analytics and robust enterprise identity. (Long-term durable storage gap closed via Postgres/S3).
