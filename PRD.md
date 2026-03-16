# Product Requirements Document (PRD): Satya AI Platform

## 1. Executive Summary
Satya is an enterprise-grade AI agent governance and observability platform built on a zero-database (flat-file JSON/Markdown) architecture. It separates the execution of AI tasks (by autonomous agents) from the oversight (by human observers). The platform acts as a "Scrum Master" for AI agents, enforcing guardrails, automated prioritization, and multi-agent coordination.

This document outlines the requirements for extending Satya with an "AI Orchestrator" and "Agent Chat" capabilities, enhancing real-time control, fault tolerance, and operational oversight.

## 2. Market Context & Product Strategy
In the rapidly evolving AI landscape, organizations are deploying swarms of autonomous agents. A critical challenge is maintaining visibility, control, and fault tolerance when agents operate independently. If an agent crashes while holding a lock on a task, that task becomes a bottleneck. Furthermore, human operators need the ability to course-correct agents mid-flight without complex code changes.

Satya solves this by providing:
1.  **Observability:** A Streamlit-based dashboard for real-time monitoring.
2.  **Governance:** SDK-level rules (e.g., proof of work required for task completion).
3.  **Resilience (New):** An AI Orchestrator to detect failed agents and reassign their work.
4.  **Control (New):** An Agent Chat interface for real-time human-to-agent communication and overrides.

**Goal:** Create a winning product that becomes the standard for public and enterprise usage by offering simple integration (3 lines of code), zero infrastructure overhead (flat-files), and robust enterprise-grade features.

## 3. Key Features & Requirements

### 3.1 AI Orchestrator (Project Manager)
**Objective:** Prevent task starvation caused by dead or disconnected agents.

*   **Mechanism:** Agents periodically send "heartbeats" (recording an ISO 8601 UTC timestamp in a flat JSON file).
*   **Orchestrator Role:** A background daemon (`orchestrator_runner.py`) running the `AIOrchestrator` class.
*   **Logic:**
    *   The Orchestrator continuously monitors the heartbeat files in `satya_data/heartbeats/`.
    *   If an agent's last heartbeat is older than a configurable timeout (e.g., 60 seconds), the Orchestrator considers the agent "dead".
    *   The Orchestrator identifies any tasks currently locked/assigned to the dead agent with the status `in_progress`.
    *   The Orchestrator reassigns these tasks back to the `queued` status and clears the `locked_by` / `locked_at` fields, allowing other healthy agents to pick them up via `pick_task()`.
*   **Testing:** The Orchestrator must support a `run_once=True` parameter for synchronous execution in test suites to prevent background thread leakage.

### 3.2 Agent Chat & Manual Overrides
**Objective:** Enable real-time human intervention and redirection of AI agents.

*   **Mechanism:** Flat-file polling mechanism (JSON files in `satya_data/chat/`).
*   **Human Interface:** The existing Streamlit dashboard (`app.py`) provides the UI to send messages/commands to specific agents. (Note: UI implementation is out of scope for the immediate backend update).
*   **Agent SDK:** The `SatyaClient` gains a `poll_chat()` SDK method.
*   **Logic:**
    *   Agents call `poll_chat()` during their execution cycles (e.g., in `agent_runner.py`).
    *   If a new message is found, the agent can parse it for manual overrides (e.g., "Stop current task", "Prioritize task X").

## 4. Pending Work & Implementation Steps

To fulfill these requirements, the following implementation steps are required in the codebase:

1.  **Storage Layer Updates (`src/satya/core/storage.py`):**
    *   Define `HEARTBEATS_DIR` and `CHAT_DIR`.
    *   Update `ensure_satya_dirs()` to create these directories.
    *   Ensure path traversal protections (`os.path.basename`) are used when accessing files dynamically based on agent names.

2.  **Orchestrator Logic (`src/satya/core/project_manager.py`):**
    *   Implement the `AIOrchestrator` class with the heartbeat monitoring and task reassignment logic.

3.  **Orchestrator Daemon (`orchestrator_runner.py`):**
    *   Create a runnable script to execute the Orchestrator continuously.

4.  **SDK Enhancements (`src/satya/sdk/client.py`):**
    *   Add `send_heartbeat()` to write the current UTC timestamp to `HEARTBEATS_DIR/{agent_name}.json`.
    *   Add `poll_chat()` to read messages from `CHAT_DIR/{agent_name}.json`.

5.  **Agent Integration (`agent_runner.py`):**
    *   Update the main polling loop to call `client.send_heartbeat()` and `client.poll_chat()`.

6.  **Public API Facade (`src/satya/core/__init__.py`):**
    *   Explicitly define `__all__` to manage exports and prevent unused import warnings.

7.  **Testing (`tests/test_project_manager.py`):**
    *   Write `pytest` tests for the `AIOrchestrator`, utilizing the `run_once=True` flag and mocking the time to simulate dead agents.

## 5. Architectural Constraints
*   **Data Safety:** All data must be written under `satya_data/` using atomic file writes and file locking (`fcntl.flock`).
*   **Timestamps:** Must strictly be ISO 8601 UTC everywhere, formatted as: `datetime.now(timezone.utc).isoformat() + "Z"`.
*   **Dependencies:** No new external dependencies allowed without updating `pyproject.toml` / `uv.lock`.
*   **Code Style:** Python 3.11+, use type hints, no print statements (use `logging` or `satya.log()`).
