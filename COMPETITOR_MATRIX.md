# Competitor Matrix

| Feature | Satya | Langfuse | LangSmith |
|---------|-------|----------|-----------|
| Observability Depth | Medium (Task/Log) | High (Token/Prompt) | High (Token/Prompt) |
| Agent Runtime Support | High | Low | Medium |
| Self-host Friendliness | High (Zero-infra default) | Medium (Docker) | Low |
| Enterprise Features (SSO/RBAC) | Partial (Admin tokens) | Yes | Yes |
| Export Adapters | Yes (OTLP, CSV/JSONL, Webhook, Langfuse, LangSmith) | N/A | N/A |
| Pricing Model | OSS | Open Core / SaaS | SaaS / Enterprise |

### Differentiator (Where Satya Wins)
Satya excels in **Self-host Friendliness** and **Agent Runtime Support**. With zero-infrastructure defaults and a lightweight footprint, it enables agent monitoring securely out-of-the-box. The export adapter system also bridges the gap by allowing integration into existing enterprise stacks.

### Gaps (Where Satya Must Catch Up)
Satya lags in **Observability Depth**. It doesn't capture token-level analytics or prompt snapshots yet, which are core features of Langfuse and LangSmith.