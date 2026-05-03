# Competitor Matrix

| Feature | Satya | Competitor 1 | Competitor 2 |
| :--- | :--- | :--- | :--- |
| **Observability Depth** | Basic (traces, latencies) | Token-level, prompt snapshots | Advanced tracing |
| **Agent Runtime Support** | Strong (native tasks/agents) | Good | Moderate |
| **Self-Host Friendliness** | High (Zero-config sqlite/files) | Medium | Low (managed focus) |
| **Enterprise Features** | Limited (Basic auth key) | High (SSO, RBAC, Audit) | High (SSO, Audit) |
| **Export Adapters** | **Missing (Need to implement)** | Native LangSmith/OTLP | Native integrations |
| **Pricing Model** | OSS / Self-hosted | Managed + Enterprise OSS | Managed Cloud |

## Strategy
* **Where Satya wins (defensible differentiator):** Extremely lightweight, zero-configuration self-hosting, tightly integrated agent runtime loop.
* **Where Satya must catch up:** Observability (exporting traces cleanly) and Enterprise Features (durable audit stores).
