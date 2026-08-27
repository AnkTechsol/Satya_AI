# Competitor Matrix

| Feature | Satya | Competitor A | Competitor B |
|---------|-------|--------------|--------------|
| Observability Depth | High (OpenTelemetry/Adapters) | Medium (proprietary) | High (token-level) |
| Agent Runtime Support | Yes (Zero-config) | Yes (heavy SDK) | No (UI only) |
| Self-host Friendliness | High (Zero-infra default) | Low (SaaS only) | Medium (Docker required) |
| Enterprise Features | RBAC, Audit, OTLP | SSO, Audit | SSO, RBAC |
| Export Adapters | Webhook, OTLP, Datadog | Custom only | Limited integrations |
| Pricing Model | OSS / Managed | Enterprise SaaS | Enterprise SaaS |

## Where Satya Wins
Satya differentiates itself with a **zero-infrastructure default** and an extensive, modular **Export Adapter framework**. This allows enterprises to adopt Satya effortlessly without ripping out their existing observability stack (e.g., Langfuse, LangSmith, OTLP, Webhooks).

## Where Satya Must Catch Up
Competitors offer deeper native SSO/RBAC integrations and more granular token-level prompt snapshots out-of-the-box in their SaaS offerings.
