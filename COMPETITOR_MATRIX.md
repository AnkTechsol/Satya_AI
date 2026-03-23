# Competitor Matrix

| Feature | Satya | LangSmith | Langfuse |
| --- | --- | --- | --- |
| Observability Depth | High (Flat-file architecture, event-level traces) | High (Token-level, prompt snapshots) | High (Detailed execution traces, token usage) |
| Agent Runtime Support | Yes (Agent-first, automatic task lifecycle) | Limited (Primarily observability) | Limited (Primarily observability) |
| Self-Host Friendliness | Very High (Zero DB, purely flat JSON/MD files) | Medium (Docker required, DB overhead) | Medium (Postgres/Redis needed) |
| Enterprise Features | WIP (Export adapters coming soon) | High (SSO, RBAC, Data Retention) | High (SSO, Audit Logs, Data Export) |
| Export Adapters | Extensible (Console, OTLP adapters) | Limited | Limited |
| Pricing Model Signal | Open Source (100% Free) | Managed (SaaS) with enterprise tiers | Managed (SaaS) and Open Source |

## Where Satya Wins
- **Zero Infrastructure overhead**: Flat-file architecture means no database management, making it trivial to deploy.
- **Agent-First Design**: Native multi-agent task tracking integrated directly with execution context.
- **Self-Hosting**: True out-of-the-box self-hosting without complex Docker or Kubernetes setups.

## Where Satya Must Catch Up
- **Enterprise Features**: Needs robust SSO, RBAC, and deeper audit stores.
- **Observability Granularity**: While good at task/event levels, token-level and prompt snapshot observability are currently missing compared to LangSmith.
