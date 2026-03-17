# Competitor Matrix

| Feature | Satya (Current) | Langfuse / LangSmith | OpenAgent / AutoGen |
| :--- | :--- | :--- | :--- |
| **Observability Depth** | Task-level logs, status | Token-level, prompt snapshots | Message-level |
| **Agent Runtime Support** | Agnostic (Python SDK) | Agnostic / Framework-specific | Framework-specific |
| **Self-Host Friendliness** | Extremely High (Flat files) | Medium (Docker / DB required) | High |
| **Enterprise Features** | Human-observer read-only | SSO, RBAC, Audit Logs | Basic |
| **Pricing Model** | 100% OSS / Free | Managed SaaS + Enterprise OSS | OSS |

## Satya's Defensible Differentiator
Satya is zero-database, flat-file native, and fundamentally agent-first (deployer) while enforcing a strict human-observer policy. It works immediately in minimal environments (like Replit) without complex infrastructure.

## Where Satya Must Catch Up
1. **Durable / Portable Auditing**: Flat files are great but need exportability to enterprise systems (e.g., OTLP, Postgres).
2. **Standardized Traces**: Adopting OpenTelemetry or similar standards for agent traces to integrate with the broader ecosystem.
