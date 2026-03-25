# Competitor Matrix

**Satya vs The Ecosystem**

| Feature | Satya (OSS) | LangSmith / Langfuse | AgentOps |
|---------|-------------|-----------------------|-----------|
| **Observability Depth** | Tasks, logs, flat files | Token-level, prompt snapshots | Event-level, performance traces |
| **Agent Runtime Support** | Core (SDK, Agent Chat, overrides) | Observability only | Observability & Testing |
| **Self-Host Friendliness** | **Extremely High (Zero DB, flat files)** | Medium (Docker, Postgres/Clickhouse) | Low (SaaS primarily) |
| **Enterprise Features** | RBAC, Audit Trails (HMAC) | SSO, RBAC, Data Retention | SSO, RBAC |
| **Export Adapters** | **Supported (OTLP, Console, via Framework)** | High (native + exports) | High |
| **Pricing Model** | 100% OSS | Managed + OSS core | Managed SaaS |

### Where Satya Wins
- **Simplicity and Zero-DB Architecture**: Satya is uniquely defensible because it requires zero infrastructure. A single `pip install` and flat files make it the easiest way to add governance to agentic workflows.
- **Agent-First Paradigm**: The "Humans = Observers, Agents = Actors" strict RBAC combined with the Agent Chat overrides is built specifically for autonomous workforces, unlike tools built for LLM API monitoring.

### Where Satya Must Catch Up
- **Deep Traceability**: Satya lacks token-level and prompt snapshot tracing.
- **Ecosystem Integration**: Continuing to expand the export adapters framework (like OTLP) so enterprises can pipe Satya's agent-level orchestration data into their existing observability stacks (Datadog, LangSmith).
