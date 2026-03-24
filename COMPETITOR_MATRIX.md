# Competitor Matrix

**Satya vs The Ecosystem**

| Feature | Satya (OSS) | LangSmith | Langfuse |
|---------|-------------|-----------|-----------|
| **Observability Depth** | Tasks, logs, flat files | Token-level, prompt snapshots | Token-level, traces, metrics |
| **Agent Runtime Support** | Core (SDK, Agent Chat, overrides) | Observability & limited testing | Observability only |
| **Self-Host Friendliness** | **Extremely High (Zero DB, flat files)** | Low (Primarily managed, hard to self-host) | High (Docker, Postgres) |
| **Enterprise Features** | RBAC, Audit Trails (HMAC) | SSO, RBAC, Data Retention, Hub | SSO, RBAC, Data Retention |
| **Export Adapters** | **Coming soon (OTLP, etc.)** | High (native + exports) | High (exports + webhooks) |
| **Pricing Model** | 100% OSS | Managed SaaS | Managed SaaS + OSS core |

### Where Satya Wins
- **Simplicity and Zero-DB Architecture**: Satya is uniquely defensible because it requires zero infrastructure. A single `pip install` and flat files make it the easiest way to add governance to agentic workflows.
- **Agent-First Paradigm**: The "Humans = Observers, Agents = Actors" strict RBAC combined with the Agent Chat overrides is built specifically for autonomous workforces, unlike tools built for LLM API monitoring.

### Where Satya Must Catch Up
- **Deep Traceability**: Satya lacks token-level and prompt snapshot tracing.
- **Ecosystem Integration**: Needs export adapters (like OTLP) so enterprises can pipe Satya's agent-level orchestration data into their existing observability stacks (Datadog, LangSmith).
