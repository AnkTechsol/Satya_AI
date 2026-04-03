# Competitor Matrix

**Satya vs The Ecosystem**

| Feature | Satya (OSS) | LangSmith / Langfuse | AgentOps |
|---------|-------------|-----------------------|-----------|
| **Observability Depth** | Tasks, logs, flat files | Token-level, prompt snapshots | Event-level, performance traces |
| **Agent Runtime Support** | Core (SDK, Agent Chat, overrides) | Observability only | Observability & Testing |
| **Self-Host Friendliness** | **Extremely High (Zero DB, flat files)** | Medium (Docker, Postgres/Clickhouse) | Low (SaaS primarily) |
| **Enterprise Features** | RBAC, Audit Trails (HMAC) | SSO, RBAC, Data Retention | SSO, RBAC |
| **Export Adapters** | **Coming soon (OTLP, etc.)** | High (native + exports) | High |
| **Pricing Model** | 100% OSS | Managed + OSS core | Managed SaaS |

### Where Satya Wins (Defensible Differentiators)
- **Simplicity and Zero-DB Architecture**: Satya is uniquely defensible because it requires absolutely zero infrastructure. A single `pip install` and its flat-file design make it the easiest way to add governance to agentic workflows without DB migrations or cloud ops.
- **Agent-First Paradigm**: The "Humans = Observers, Agents = Actors" strict RBAC combined with Agent Chat overrides is built specifically for autonomous workforces, unlike tools built merely for LLM API monitoring.

### Where Satya Must Catch Up
- **Deep Traceability**: Satya currently lacks token-level insights and prompt snapshot tracing (though OTLP adapters can bridge this).
- **Ecosystem Integration**: Needs more robust export adapters (like OTLP, LangSmith, and Datadog) so enterprises can pipe Satya's agent-level orchestration data into their existing observability stacks.
