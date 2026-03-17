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
6. **AI Project Manager & Agent Heartbeats:** Centralized Orchestrator tool that monitors agent health via heartbeats and auto-reassigns tasks from crashed agents.

## 4. New Features: Strict WIP Limits & Agent Optimization
**Problem:** Currently, agents can pick up multiple tasks or get assigned multiple tasks simultaneously, causing load balancing issues. Furthermore, agents without heartbeats might be marked offline immediately even if they just started processing a task.
**Solution:** Enforce strict Work-In-Progress (WIP) limits via the SDK and implement grace periods in the Orchestrator.

### 4.1. Requirements
* **Strict WIP Limits (SDK):** The `satya.pick_task()` SDK method enforces a strict Work In Progress limit. It queries the data layer to ensure the agent has exactly 0 or 1 active tasks before allowing a new task to be picked.
* **Orchestrator Grace Periods:** The Project Manager uses the `locked_at` property to provide a grace period. If an agent has no heartbeat file but just started a task (recent `locked_at`), they are not immediately declared offline.

## 5. Success Metrics
* **Agent Reliability:** 100% of stuck tasks are automatically recovered and re-queued by the Project Manager.
* **Load Balancing:** 0% of agents have more than 1 task in "In Progress" status simultaneously.
* **Observability:** Users can identify crashed agents within X minutes via the Dashboard UI.

## 6. Future Roadmap
* **REST API Layer:** Support for non-Python agents (Node.js, Go) to interact with Satya.
* **WebSocket Real-Time Log Streaming:** Stream logs to the dashboard without full page reloads.
* **Agent Roles / Skill-based Routing:** Allow agents to pick tasks specifically matching their specialized skills (e.g., "Reviewer Agent").
* **Multi-Agent Collaboration Protocols:** Enable agents to spawn subtasks and pass them directly to other agents, building a cryptographically signed audit chain.
