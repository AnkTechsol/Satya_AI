"""
goal_guardian.py — Goal Alignment Auditor

Continuously audits AI agent logs and task comments against a declared project goal
using lightweight NLTK-based semantic similarity (no LLM required).

When drift is detected:
  1. Raises a structured alert saved to satya_data/pulse/alerts.json
  2. Writes a HALT directive to the agent's chat channel (same mechanism as Agent Chat)
  3. Saves the last-known-good context snapshot so the agent can revert

Usage (agent side):
    client.set_goal("Build a REST API for user authentication using JWT")
    # ... agent works ...
    # check_alignment() is called automatically on each log() call
    # Or manually: client.check_alignment("I am now writing marketing copy")

Design Principles:
  - Zero LLM calls — uses NLTK TF-IDF cosine similarity
  - NLTK data is downloaded lazily once, cached locally
  - Falls back to keyword overlap if NLTK unavailable
  - Threshold-based: configurable sensitivity (default 0.25)
  - Does NOT block the agent's work on check failure — it warns and flags
"""

from __future__ import annotations

import os
import re
import json
import math
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────
# NLTK Bootstrap (lazy, graceful fallback)
# ──────────────────────────────────────────────────────────

_NLTK_READY = False
_STOPWORDS: set[str] = set()


def _bootstrap_nltk() -> bool:
    """
    Download required NLTK data on first use.
    Returns True if NLTK is available, False if we fall back to keyword overlap.
    """
    global _NLTK_READY, _STOPWORDS
    if _NLTK_READY:
        return True
    try:
        import nltk  # type: ignore
        # Use a local download dir inside the project so we don't pollute system
        nltk_data_dir = os.path.join(os.getcwd(), ".nltk_data")
        os.makedirs(nltk_data_dir, exist_ok=True)
        nltk.data.path.insert(0, nltk_data_dir)

        for resource in ("stopwords", "punkt", "punkt_tab"):
            try:
                nltk.data.find(f"tokenizers/{resource}" if "punkt" in resource else f"corpora/{resource}")
            except LookupError:
                nltk.download(resource, download_dir=nltk_data_dir, quiet=True)

        from nltk.corpus import stopwords  # type: ignore
        _STOPWORDS = set(stopwords.words("english"))
        _NLTK_READY = True
        return True
    except Exception as e:
        logger.warning(f"GoalGuardian: NLTK unavailable ({e}), falling back to keyword overlap.")
        return False


# ──────────────────────────────────────────────────────────
# Text Similarity
# ──────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    """Simple tokenizer — strips punctuation, lowercases."""
    return re.findall(r"[a-z]+", text.lower())


def _tf(tokens: list[str]) -> dict[str, float]:
    """Term frequency."""
    freq: dict[str, int] = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    total = len(tokens) or 1
    return {t: c / total for t, c in freq.items()}


def _cosine_similarity(a: dict[str, float], b: dict[str, float]) -> float:
    """Cosine similarity between two TF vectors."""
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
    mag_a = math.sqrt(sum(v**2 for v in a.values()))
    mag_b = math.sqrt(sum(v**2 for v in b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def _similarity(goal: str, text: str) -> float:
    """
    Returns a similarity score in [0, 1] between the project goal and a text snippet.

    Uses NLTK stopword filtering + TF-cosine if available,
    falls back to plain keyword overlap ratio.
    """
    use_nltk = _bootstrap_nltk()

    goal_tokens = _tokenize(goal)
    text_tokens = _tokenize(text)

    if use_nltk and _STOPWORDS:
        goal_tokens = [t for t in goal_tokens if t not in _STOPWORDS]
        text_tokens = [t for t in text_tokens if t not in _STOPWORDS]

    if not goal_tokens or not text_tokens:
        return 0.0

    tf_goal = _tf(goal_tokens)
    tf_text = _tf(text_tokens)
    return _cosine_similarity(tf_goal, tf_text)


# ──────────────────────────────────────────────────────────
# Context Snapshot (for revert-on-halt)
# ──────────────────────────────────────────────────────────

def _get_context_dir() -> str:
    from . import storage
    ctx_dir = os.path.join(storage.SATYA_DIR, "goal_contexts")
    os.makedirs(ctx_dir, exist_ok=True)
    return ctx_dir


def save_context_snapshot(agent_name: str, current_task: Optional[dict], log_path: str, notes: str = "") -> str:
    """
    Saves a timestamped snapshot of the agent's current context.
    Returns the snapshot filepath.
    Used as a 'checkpoint' before issuing a HALT so the agent can revert.
    """
    now = datetime.now(timezone.utc)
    ctx_dir = _get_context_dir()
    snapshot_id = now.strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(ctx_dir, f"{agent_name}_{snapshot_id}.json")

    # Read last N lines of agent log as context
    log_tail: list[str] = []
    try:
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                log_tail = [l.strip() for l in lines[-20:]]
    except Exception:
        pass

    snapshot = {
        "agent": agent_name,
        "snapshot_id": snapshot_id,
        "saved_at": now.isoformat(),
        "current_task": current_task,
        "log_tail": log_tail,
        "notes": notes,
    }

    from . import storage
    storage.save_json(filepath, snapshot)
    return filepath


def get_latest_context_snapshot(agent_name: str) -> Optional[dict]:
    """Returns the most recent saved context snapshot for an agent."""
    ctx_dir = _get_context_dir()
    if not os.path.exists(ctx_dir):
        return None
    snapshots = sorted(
        [f for f in os.listdir(ctx_dir) if f.startswith(agent_name) and f.endswith(".json")],
        reverse=True,
    )
    if not snapshots:
        return None
    from . import storage
    return storage.load_json(os.path.join(ctx_dir, snapshots[0]))


# ──────────────────────────────────────────────────────────
# GoalGuardian Class
# ──────────────────────────────────────────────────────────

class GoalGuardian:
    """
    Monitors AI agent activity against a declared project goal.

    Parameters
    ----------
    agent_name : str
        Name of the agent being monitored.
    goal : str
        Free-text description of the project goal.
    threshold : float
        Minimum similarity score (0–1) below which a message is flagged as drift.
        Default 0.20 — anything below 20% similarity triggers a warning.
    halt_threshold : float
        Below this score, issue a HALT directive (default 0.10).
    window : int
        Number of recent messages to include in the rolling window check.
    """

    def __init__(
        self,
        agent_name: str,
        goal: str,
        threshold: float = 0.20,
        halt_threshold: float = 0.10,
        window: int = 5,
    ):
        self.agent_name = agent_name
        self.goal = goal
        self.threshold = threshold
        self.halt_threshold = halt_threshold
        self.window = window
        self._message_buffer: list[str] = []

        # Pre-warm NLTK (non-blocking — will warn if unavailable)
        _bootstrap_nltk()

    # ── Public API ────────────────────────────────────────

    def check(self, message: str, current_task: Optional[dict] = None, log_path: str = "") -> dict:
        """
        Check a log message or task comment for goal alignment.

        Returns an alignment result:
        {
            "aligned": bool,
            "score": float,
            "action": "ok" | "warn" | "halt",
            "message": str,
            "snapshot_path": str | None,
            "halt_directive": dict | None,
        }
        """
        self._message_buffer.append(message)
        if len(self._message_buffer) > self.window:
            self._message_buffer.pop(0)

        # Use rolling window concatenation for context-aware scoring
        window_text = " ".join(self._message_buffer)
        score = _similarity(self.goal, window_text)

        result: dict = {
            "aligned": score >= self.threshold,
            "score": round(score, 4),
            "action": "ok",
            "message": message,
            "snapshot_path": None,
            "halt_directive": None,
        }

        if score < self.halt_threshold:
            # Critical drift — issue HALT
            snapshot_path = None
            if current_task and log_path:
                snapshot_path = save_context_snapshot(
                    self.agent_name,
                    current_task,
                    log_path,
                    notes=f"Auto-snapshot before HALT. Drift score={score:.4f}",
                )
            halt_directive = self._issue_halt_directive(score, snapshot_path)
            result["action"] = "halt"
            result["snapshot_path"] = snapshot_path
            result["halt_directive"] = halt_directive
            self._save_alert(score, "halt", message, snapshot_path)

        elif score < self.threshold:
            # Warn — drift is happening but not critical yet
            result["action"] = "warn"
            self._save_alert(score, "warn", message, None)

        return result

    def is_aligned(self, message: str) -> bool:
        """Convenience method — returns True if message is goal-aligned."""
        return self.check(message)["aligned"]

    def reset_context(self):
        """Clear the rolling message window (call when starting a new task)."""
        self._message_buffer.clear()

    # ── Internal ──────────────────────────────────────────

    def _issue_halt_directive(self, score: float, snapshot_path: Optional[str]) -> dict:
        """
        Writes a HALT message to the agent's chat channel.
        The agent's `poll_chat()` will pick this up and can react to it.
        """
        from . import storage

        now = datetime.now(timezone.utc)
        directive = {
            "id": f"halt_{now.strftime('%Y%m%d_%H%M%S')}",
            "timestamp": now.isoformat(),
            "type": "GOAL_GUARDIAN_HALT",
            "sender": "GoalGuardian",
            "status": "unread",
            "message": (
                f"⛔ GOAL ALIGNMENT HALT — Drift score: {score:.3f} (threshold: {self.halt_threshold}).\n"
                f"Your recent activity appears to diverge from the project goal:\n"
                f"  Goal: \"{self.goal}\"\n\n"
                f"Action required: Revert to your last saved context and re-read the project goal.\n"
                f"Context snapshot: {snapshot_path or 'N/A'}\n"
                f"Resume only after reviewing your task alignment."
            ),
            "drift_score": score,
            "goal": self.goal,
            "snapshot_path": snapshot_path,
        }

        # Write to agent chat directory (same format as Agent Chat)
        safe_name = os.path.basename(self.agent_name)
        chat_dir = os.path.join(storage.SATYA_DIR, "chat", safe_name)
        os.makedirs(chat_dir, exist_ok=True)
        filepath = os.path.join(chat_dir, f"{directive['id']}.json")
        storage.save_json(filepath, directive)
        return directive

    def _save_alert(self, score: float, action: str, message: str, snapshot_path: Optional[str]):
        """Appends an alert to satya_data/pulse/goal_alerts.json."""
        from . import storage

        now = datetime.now(timezone.utc)
        alert = {
            "timestamp": now.isoformat(),
            "agent": self.agent_name,
            "action": action,
            "score": round(score, 4),
            "goal": self.goal,
            "message_excerpt": message[:200],
            "snapshot_path": snapshot_path,
        }

        alerts_path = os.path.join(storage.SATYA_DIR, "pulse", "goal_alerts.json")
        os.makedirs(os.path.dirname(alerts_path), exist_ok=True)

        existing: list = []
        if os.path.exists(alerts_path):
            try:
                with open(alerts_path, "r") as f:
                    existing = json.load(f)
            except Exception:
                existing = []

        existing.append(alert)
        # Keep last 500 alerts
        existing = existing[-500:]
        storage.save_json(alerts_path, existing)


# ──────────────────────────────────────────────────────────
# Goal State Persistence (so goal survives agent restarts)
# ──────────────────────────────────────────────────────────

def save_goal(agent_name: str, goal: str, threshold: float = 0.20, halt_threshold: float = 0.10) -> str:
    """
    Persists an agent's goal to disk so it can be restored on restart.
    Returns the path to the goal file.
    """
    from . import storage

    goals_dir = os.path.join(storage.SATYA_DIR, "goals")
    os.makedirs(goals_dir, exist_ok=True)

    safe_name = os.path.basename(agent_name)
    filepath = os.path.join(goals_dir, f"{safe_name}.json")

    goal_data = {
        "agent": agent_name,
        "goal": goal,
        "threshold": threshold,
        "halt_threshold": halt_threshold,
        "set_at": datetime.now(timezone.utc).isoformat(),
    }
    storage.save_json(filepath, goal_data)
    return filepath


def load_goal(agent_name: str) -> Optional[dict]:
    """Loads a persisted goal for an agent. Returns None if not set."""
    from . import storage

    safe_name = os.path.basename(agent_name)
    filepath = os.path.join(storage.SATYA_DIR, "goals", f"{safe_name}.json")
    if not os.path.exists(filepath):
        return None
    return storage.load_json(filepath)


def load_all_goals() -> dict[str, dict]:
    """Loads all persisted goals for all agents into a dictionary."""
    from . import storage
    goals = {}
    goals_dir = os.path.join(storage.SATYA_DIR, "goals")
    if not os.path.exists(goals_dir):
        return goals
    for filename in os.listdir(goals_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(goals_dir, filename)
            goal_data = storage.load_json(filepath)
            if goal_data and "agent" in goal_data:
                goals[goal_data["agent"]] = goal_data
    return goals


def load_goal_alerts(limit: int = 100) -> list[dict]:
    """Returns the most recent goal alignment alerts."""
    from . import storage

    alerts_path = os.path.join(storage.SATYA_DIR, "pulse", "goal_alerts.json")
    if not os.path.exists(alerts_path):
        return []
    try:
        with open(alerts_path, "r") as f:
            data = json.load(f)
        return data[-limit:] if isinstance(data, list) else []
    except Exception:
        return []
