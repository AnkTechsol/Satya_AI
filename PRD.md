# Product Requirements Document (PRD): Satya AI Orchestrator

## 1. Product Vision & Value Proposition

**Vision:** To establish Satya as the premier zero-database governance and observability platform for autonomous AI agent fleets.

**Value Proposition:** "Deploy your AI workforce with confidence. Satya provides real-time oversight, unified governance, and now, with the AI Orchestrator, automated resilience. Never let an agent fail silently again."

## 2. Target Audience & Customer Acquisition

**Primary Audience:** Engineering leaders, AI operations managers, and developers deploying multi-agent systems.
**Pain Points:**
- "My agents get stuck on tasks, blocking the pipeline."
- "I don't know if an agent crashed or is just taking a long time."
- "Managing agent state across different environments is a nightmare."

**Customer Acquisition Strategy:**
- **Open-Source Growth:** Position Satya as the standard boilerplate for AI agent projects. Encourage developers to "npm install" (or pip install) Satya from day one.
- **Content Marketing:** Publish case studies on how the AI Orchestrator recovers failed agent tasks automatically.
- **Enterprise Upsell:** "Main Owner" features and advanced governance rules (already in the platform) serve as the bridge to enterprise paid support or hosted versions.

## 3. Core Feature: The AI Orchestrator (Project Manager)

**Problem:** Agents crash or enter infinite loops. Tasks marked `in_progress` stay locked indefinitely, preventing other healthy agents from picking them up.

**Solution:** The AI Orchestrator acts as an automated Project Manager. It monitors agent "heartbeats." If an agent stops sending heartbeats while working on a task, the Orchestrator detects the failure, unlocks the task, and returns it to the `queued` state for reassignment.

### 3.1 Requirements

- **Heartbeat Mechanism:** Agents must periodically signal they are alive.
- **Data Storage:** Heartbeats must be stored in flat-file JSON formats within `satya_data/heartbeats/` to maintain the zero-database architecture.
- **Timeout Threshold:** If a heartbeat is older than a configurable threshold (e.g., 5 minutes), the agent is considered dead.
- **Auto-Recovery:** The Orchestrator must scan tasks in `in_progress`. If the assigned agent is dead, the task must be reverted to `queued` and unlocked (`locked_by` = None).
- **Audit Trail:** When the Orchestrator recovers a task, it must log this action in the task's `audit_trail`.

## 4. Pending Work (Execution Plan)

- [ ] Define `HEARTBEATS_DIR` in `src/satya/core/storage.py`.
- [ ] Create `src/satya/core/project_manager.py` with `Orchestrator` class.
- [ ] Add `send_heartbeat()` to SDK (`client.py`).
- [ ] Update `agent_runner.py` to send heartbeats during its polling loop.
- [ ] Write robust `pytest` tests validating heartbeat creation and task recovery.
