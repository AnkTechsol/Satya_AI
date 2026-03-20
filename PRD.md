# Satya AI: Product Requirements Document (PRD)

## 1. Product Vision
**Satya AI** is the zero-infrastructure, flat-file source of truth for AI agent operations. As AI agents increasingly operate autonomously, humans need an observability layer to monitor, govern, and orchestrate their tasks without complex database setups.

Our vision is to become the **"Jira for AI Agents"** — a standardized, multi-agent project management and observability platform that AI agents can self-deploy and interact with programmatically, while humans maintain oversight.

## 2. Target Audience
* **AI Developers & Engineers:** Building multi-agent systems and needing a simple way to track agent progress without standing up PostgreSQL or Redis.
* **Product Managers & Operations:** Needing a clear, visual Kanban board to see what their autonomous AI workforce is doing in real time.
* **Enterprise Compliance Teams:** Requiring strict audit trails, governance, and Proof of Work for autonomous actions.

## 3. Current State & Core Features
1. **Zero-Database Architecture:** Uses `.json` and `.md` files to store tasks, knowledge (Truth Sources), and agent logs.
2. **Agent SDK:** Python SDK for agents to self-report progress (`satya.log()`, `satya.pick_task()`, `satya.finish_task()`).
3. **Web Dashboard:** Streamlit-based UI for humans to monitor tasks, completion rates, and agent logs.
4. **Governance Rules:** Built-in checks (e.g., tasks require minimum description lengths, completion requires agent comments).
5. **Main Owner Role:** Master administrator oversight for the workspace.

## 4. New Feature: AI Project Manager & Agent Heartbeats
**Problem:** Currently, if an AI agent crashes or gets stuck in an infinite loop while executing an "In Progress" task, the task remains locked indefinitely. The existing watchdog can identify stale tasks but lacks an active agent lifecycle manager.
**Solution:** A centralized "AI Project Manager" (Orchestrator) tool that monitors agent health via a "Heartbeat" concept.

### 4.1. Requirements
* **Agent Heartbeat (SDK):** Agents must be able to call `satya.heartbeat()` periodically. This writes a timestamp to a dedicated heartbeat file.
* **Orchestrator Tool:** A new script (`project_manager.py` or similar) that runs continuously as the central "Scrum Master". It polls the heartbeat files.
* **Task Re-assignment (Self-Healing):** If the Orchestrator detects that an agent has missed its heartbeat for X minutes, it declares the agent "Offline". Any "In Progress" tasks held by that agent are forcibly unlocked, marked "queued" (To Do), and the assignee is cleared so another agent can pick them up.
* **UI Updates:** The dashboard must display real-time agent status (Online/Offline) based on heartbeat freshness.

## 5. Success Metrics
* **Agent Reliability:** 100% of stuck tasks are automatically recovered and re-queued by the Project Manager.
* **Observability:** Users can identify crashed agents within X minutes via the Dashboard UI.

## 6. Future Roadmap (Updated)
* **REST API Layer:** Support for non-Python agents (Node.js, Go, Rust) to interact with Satya securely.
* **WebSocket Real-Time Log Streaming:** Stream logs to the dashboard without full page reloads, providing instant feedback on agent actions.
* **Multi-Agent Collaboration Protocols:** Allow agents to pass tasks to specific specialized agents (e.g., "Reviewer Agent") and manage cross-agent dependencies.
* **Plugin Marketplace:** Create an extensible architecture where community developers can publish 'Truth Source Extractors' and 'Governance Validators' for public use.
* **Public Workspaces:** Enable sharing read-only views of AI agent execution dashboards directly to the public via customizable sharing links to foster trust and demonstrate AI competence.
* **Mobile Companion App:** Develop a cross-platform mobile app (React Native) for product managers to monitor agent health and approve critical tasks on the go.

## 7. Business & Ecosystem Strategy
To position Satya AI as a winning, widely-adopted platform and enterprise standard:
* **Self-Serve Onboarding:** Offer a frictionless 1-click deployment system using tools like Replit to minimize time to value.
* **Template Galleries:** Provide pre-configured "AI Missions" allowing non-technical users to launch curated agent workflows (e.g., "SEO Content Writer", "Code Reviewer Swarm") out-of-the-box.
* **Ecosystem Integrations:** Build pre-configured integrations with popular AI frameworks (LangChain, AutoGen, CrewAI) and standard tools (Slack, GitHub, Notion, Jira) to drive organic growth.
* **Webhooks & Event Triggers:** Enable external systems to react to task changes or agent failures instantly, supporting complex automation chains.
* **Advanced Analytics Dashboard:** Provide executive-level metrics, such as agent efficiency, average task duration, ROI estimation per agent, and error rates.
* **Enterprise Security & SSO:** Implement role-based access control (RBAC), Single Sign-On (SAML/OAuth), and automated compliance reporting (SOC2 readiness) to support large-scale organizational deployments.
* **Community-Led Growth:** Sponsor hackathons and offer a generous free-tier for indie-hackers to build public agent swarms using Satya as the backbone.

## 8. Recently Completed Work
* **Automated Issue Resolution Workflow (RCA):** Integrated Root Cause Analysis mechanism into the orchestrator where failed tasks automatically spawn targeted debugging sub-tasks for agents to triage errors autonomously.
* **AI Project Manager & Agent Heartbeats:** Successfully implemented `project_manager.py` (Orchestrator Tool) to continuously monitor agent health via `satya.send_heartbeat()`.
* **Self-Healing Task Re-assignment:** Stuck tasks from dead/offline agents are now automatically unlocked and returned to the `queued` state after the grace period expires.
* **Dashboard Agent Status:** Streamlit UI dynamically displays real-time agent 'Online/Offline' statuses using the heartbeat freshness metrics.
