"""
pulse.py — Agent Pulse: Semantic Health & Velocity Intelligence

Computes per-agent health scores, cross-agent velocity matrices, and
cascade failure alerts entirely from existing satya_data flat files.

Zero external dependencies. Zero LLM calls. Zero schema changes.
All analysis is derived from audit_trail, comments, timestamps, and heartbeats.
"""

from __future__ import annotations

import os
import json
import math
from datetime import datetime, timezone, timedelta
from typing import Any

# ──────────────────────────────────────────────────────────
# Data Types (plain dicts, not dataclasses, for JSON compat)
# ──────────────────────────────────────────────────────────

PRIORITY_WEIGHT = {"Critical": 2.0, "High": 1.5, "Medium": 1.0, "Low": 0.5}


def _parse_iso(s: str | None) -> datetime | None:
    """Safe ISO-8601 parser; handles trailing Z."""
    if not s:
        return None
    try:
        clean = s.replace("Z", "+00:00") if s.endswith("Z") else s
        dt = datetime.fromisoformat(clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


# ──────────────────────────────────────────────────────────
# 1. PER-AGENT HEALTH SCORE
# ──────────────────────────────────────────────────────────

def compute_agent_health(agent_name: str, tasks: list[dict]) -> dict:
    """
    Returns a health record for a single agent:
    {
        "agent": str,
        "score": int,          # 0–100
        "grade": str,          # A / B / C / D / F
        "trend": str,          # "up" / "down" / "stable"
        "throughput": float,   # tasks completed per hour (last 24 h)
        "rework_rate": float,  # 0.0–1.0
        "log_density": float,  # avg comments per completed task
        "overrun_rate": float, # fraction of tasks that exceeded time_limit
        "abandon_rate": float, # fraction reassigned away
        "details": dict        # raw sub-metric values
    }
    """
    now = _now_utc()
    window_24h = now - timedelta(hours=24)

    # Filter tasks involving this agent (assigned or ever locked)
    agent_tasks = [
        t for t in tasks
        if t.get("assignee") == agent_name or t.get("locked_by") == agent_name
    ]

    total = len(agent_tasks)
    if total == 0:
        return {
            "agent": agent_name, "score": 0, "grade": "N/A",
            "trend": "stable", "throughput": 0.0, "rework_rate": 0.0,
            "log_density": 0.0, "overrun_rate": 0.0, "abandon_rate": 0.0,
            "details": {}
        }

    # ── Throughput (tasks/hour in last 24 h) ──────────────
    done_recent = [
        t for t in agent_tasks
        if t.get("status") == "done"
        and _parse_iso(t.get("completed_at", t.get("updated_at"))) is not None
        and _parse_iso(t.get("completed_at", t.get("updated_at"))) >= window_24h
    ]
    throughput = len(done_recent) / 24.0

    # ── Rework Rate ───────────────────────────────────────
    # A task is "reworked" when its audit_trail shows status going backwards
    # or contains a "failed" terminal state that was then re-created.
    rework_count = 0
    for t in agent_tasks:
        trail = t.get("audit_trail", [])
        statuses = [
            e.get("details", "").split("'")[-2]
            for e in trail
            if e.get("action") == "Status Changed"
        ]
        if "failed" in statuses:
            rework_count += 1
        # repeated in_progress transitions
        ip_count = statuses.count("in_progress")
        if ip_count > 1:
            rework_count += 1
    rework_rate = min(rework_count / total, 1.0)

    # ── Log Density ───────────────────────────────────────
    done_tasks = [t for t in agent_tasks if t.get("status") == "done"]
    if done_tasks:
        total_comments = sum(
            len([c for c in t.get("comments", []) if c.get("agent") == agent_name])
            for t in done_tasks
        )
        log_density = total_comments / len(done_tasks)
    else:
        log_density = 0.0

    # ── Time Overrun Rate ─────────────────────────────────
    overrun_count = 0
    for t in agent_tasks:
        locked_at = _parse_iso(t.get("locked_at"))
        completed_at = _parse_iso(t.get("completed_at"))
        time_limit = t.get("time_limit_minutes", 30)
        if locked_at and completed_at:
            elapsed = (completed_at - locked_at).total_seconds() / 60
            if elapsed > time_limit:
                overrun_count += 1
        elif t.get("status") == "in_progress" and locked_at:
            elapsed = (_now_utc() - locked_at).total_seconds() / 60
            if elapsed > time_limit:
                overrun_count += 1
    overrun_rate = overrun_count / total

    # ── Abandonment Rate ──────────────────────────────────
    abandon_count = sum(
        1 for t in tasks
        if t.get("locked_by") == agent_name
        and t.get("assignee") != agent_name
        and t.get("status") not in ("done", "failed")
    )
    abandon_rate = abandon_count / max(total, 1)

    # ── Composite Score (0–100) ───────────────────────────
    # Weights tuned to reflect real-world importance
    score = 100.0
    score -= rework_rate * 25          # max -25 for high rework
    score -= overrun_rate * 20         # max -20 for time overruns
    score -= abandon_rate * 20         # max -20 for abandonment
    # Reward throughput (capped contribution)
    throughput_bonus = min(throughput * 10, 15)  # max +15
    score += throughput_bonus
    # Reward log density (capped)
    density_bonus = min(log_density * 5, 10)     # max +10
    score += density_bonus
    score = max(0.0, min(100.0, score))

    # ── Grade ─────────────────────────────────────────────
    grade = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D" if score >= 40 else "F"

    return {
        "agent": agent_name,
        "score": round(score),
        "grade": grade,
        "trend": "stable",  # updated in snapshot diff
        "throughput": round(throughput, 3),
        "rework_rate": round(rework_rate, 3),
        "log_density": round(log_density, 2),
        "overrun_rate": round(overrun_rate, 3),
        "abandon_rate": round(abandon_rate, 3),
        "details": {
            "total_tasks": total,
            "done_recent_24h": len(done_recent),
            "rework_count": rework_count,
            "overrun_count": overrun_count,
            "abandon_count": abandon_count,
        }
    }


# ──────────────────────────────────────────────────────────
# 2. CROSS-AGENT VELOCITY MATRIX
# ──────────────────────────────────────────────────────────

def compute_velocity_matrix(tasks: list[dict]) -> dict:
    """
    Returns a velocity matrix showing avg completion time per agent per task-priority bucket.
    Also computes hourly activity heatmap (0–23) per agent.

    {
        "agents": [str, ...],
        "priority_buckets": {
            agent: { "Critical": avg_min, "High": ..., "Medium": ..., "Low": ... }
        },
        "hourly_heatmap": {
            agent: [count_hour_0, count_hour_1, ..., count_hour_23]
        },
        "bottlenecks": [ { "task_id": ..., "blocked_by": ..., "waiting_agent": ... } ]
    }
    """
    agents = set()
    priority_times: dict[str, dict[str, list[float]]] = {}
    hourly_activity: dict[str, list[int]] = {}
    bottlenecks = []

    done_task_ids = {t["id"] for t in tasks if t.get("status") == "done"}

    for t in tasks:
        assignee = t.get("assignee", "Unassigned")
        agents.add(assignee)

        # Priority bucket timing
        if t.get("status") == "done":
            locked_at = _parse_iso(t.get("locked_at"))
            completed_at = _parse_iso(t.get("completed_at", t.get("updated_at")))
            priority = t.get("priority", "Medium")
            if locked_at and completed_at:
                elapsed_min = (completed_at - locked_at).total_seconds() / 60
                priority_times.setdefault(assignee, {}).setdefault(priority, []).append(elapsed_min)

        # Hourly heatmap from audit trail
        for event in t.get("audit_trail", []):
            if event.get("action") != "Status Changed":
                continue
            agent = event.get("agent", assignee)
            ts = _parse_iso(event.get("timestamp"))
            if ts:
                hour = ts.hour
                hourly_activity.setdefault(agent, [0] * 24)
                hourly_activity[agent][hour] += 1

        # Bottleneck detection
        deps = t.get("dependencies", [])
        for dep_id in deps:
            if dep_id not in done_task_ids:
                dep_task = next((x for x in tasks if x["id"] == dep_id), None)
                if dep_task:
                    bottlenecks.append({
                        "task_id": t["id"],
                        "task_title": t.get("title", ""),
                        "waiting_agent": t.get("assignee", "Unassigned"),
                        "blocked_by_task": dep_id,
                        "blocked_by_agent": dep_task.get("assignee", "Unassigned"),
                    })

    # Average the timing lists
    priority_buckets = {}
    for agent, buckets in priority_times.items():
        priority_buckets[agent] = {
            p: round(sum(times) / len(times), 1) if times else None
            for p, times in buckets.items()
        }

    return {
        "agents": sorted(agents),
        "priority_buckets": priority_buckets,
        "hourly_heatmap": hourly_activity,
        "bottlenecks": bottlenecks,
    }


# ──────────────────────────────────────────────────────────
# 3. CASCADE FAILURE DETECTION
# ──────────────────────────────────────────────────────────

def detect_cascade_failures(tasks: list[dict]) -> list[dict]:
    """
    Returns a list of active alerts when failure patterns are detected.

    Patterns:
    - PATTERN_SEQUENTIAL_FAIL: agent has ≥3 consecutive failed tasks
    - PATTERN_SILENT_AGENT: agent in_progress task + log frequency dropped to 0 in last 30 min
    - PATTERN_CHAIN_FAIL: dependency chain where upstream failure will cascade

    Each alert:
    {
        "alert_id": str,
        "pattern": str,
        "severity": "warning" | "critical",
        "agent": str,
        "message": str,
        "task_ids": [str],
        "detected_at": str (ISO)
    }
    """
    alerts = []
    now = _now_utc()

    # Group tasks by agent, sorted by updated_at
    by_agent: dict[str, list[dict]] = {}
    for t in tasks:
        agent = t.get("assignee", "Unassigned")
        by_agent.setdefault(agent, []).append(t)

    for agent, agent_tasks in by_agent.items():
        sorted_tasks = sorted(agent_tasks, key=lambda x: x.get("updated_at", ""))

        # ── Pattern 1: Sequential Failures ───────────────
        fail_streak = []
        for t in sorted_tasks:
            if t.get("status") == "failed":
                fail_streak.append(t["id"])
            else:
                fail_streak = []
            if len(fail_streak) >= 3:
                alerts.append({
                    "alert_id": f"cascade_{agent}_{len(alerts)}",
                    "pattern": "PATTERN_SEQUENTIAL_FAIL",
                    "severity": "critical",
                    "agent": agent,
                    "message": f"Agent '{agent}' has {len(fail_streak)} consecutive failed tasks. Possible runaway loop.",
                    "task_ids": fail_streak[-3:],
                    "detected_at": now.isoformat(),
                })
                break

        # ── Pattern 2: Silent Agent (in_progress + no recent logs) ──
        in_progress_tasks = [t for t in agent_tasks if t.get("status") == "in_progress"]
        for t in in_progress_tasks:
            locked_at = _parse_iso(t.get("locked_at"))
            time_limit = t.get("time_limit_minutes", 30)
            if locked_at:
                elapsed_min = (now - locked_at).total_seconds() / 60
                if elapsed_min > time_limit * 2:
                    # Check if agent has logged anything in last 30 min
                    recent_comment = None
                    for c in reversed(t.get("comments", [])):
                        ts = _parse_iso(c.get("timestamp"))
                        if ts and (now - ts).total_seconds() < 1800:
                            recent_comment = ts
                            break
                    if not recent_comment:
                        alerts.append({
                            "alert_id": f"silent_{agent}_{t['id']}",
                            "pattern": "PATTERN_SILENT_AGENT",
                            "severity": "warning",
                            "agent": agent,
                            "message": (
                                f"Task '{t.get('title', t['id'])}' has been in_progress for "
                                f"{elapsed_min:.0f}m (limit: {time_limit}m) with no recent logs. "
                                "Agent may be stuck."
                            ),
                            "task_ids": [t["id"]],
                            "detected_at": now.isoformat(),
                        })

    # ── Pattern 3: Dependency Chain Failures ─────────────
    failed_ids = {t["id"] for t in tasks if t.get("status") == "failed"}
    for t in tasks:
        if t.get("status") in ("queued", "in_progress"):
            deps = t.get("dependencies", [])
            failed_deps = [d for d in deps if d in failed_ids]
            if failed_deps:
                alerts.append({
                    "alert_id": f"chain_{t['id']}",
                    "pattern": "PATTERN_CHAIN_FAIL",
                    "severity": "critical",
                    "agent": t.get("assignee", "Unassigned"),
                    "message": (
                        f"Task '{t.get('title', t['id'])}' depends on {len(failed_deps)} "
                        "failed task(s). Downstream work will be blocked."
                    ),
                    "task_ids": [t["id"]] + failed_deps,
                    "detected_at": now.isoformat(),
                })

    return alerts


# ──────────────────────────────────────────────────────────
# 4. FULL SNAPSHOT (called periodically to persist state)
# ──────────────────────────────────────────────────────────

def snapshot_pulse(tasks: list[dict], heartbeats: dict) -> dict:
    """
    Computes a full pulse snapshot from all tasks and heartbeat data.
    Saves to satya_data/pulse/latest.json and returns the snapshot dict.
    """
    from . import storage

    now = _now_utc()
    all_agents = set()

    for t in tasks:
        if t.get("assignee"):
            all_agents.add(t["assignee"])
    for agent in heartbeats:
        all_agents.add(agent)
    all_agents.discard("Unassigned")

    health_scores = {
        agent: compute_agent_health(agent, tasks)
        for agent in all_agents
    }

    # Compute trend vs previous snapshot
    prev = storage.get_pulse_latest()
    if prev:
        prev_scores = prev.get("health_scores", {})
        for agent, rec in health_scores.items():
            prev_score = prev_scores.get(agent, {}).get("score")
            if prev_score is not None:
                diff = rec["score"] - prev_score
                rec["trend"] = "up" if diff > 3 else "down" if diff < -3 else "stable"

    velocity = compute_velocity_matrix(tasks)
    alerts = detect_cascade_failures(tasks)

    snapshot = {
        "generated_at": now.isoformat(),
        "health_scores": health_scores,
        "velocity": velocity,
        "alerts": alerts,
        "summary": {
            "total_agents": len(all_agents),
            "live_agents": sum(
                1 for a, h in heartbeats.items()
                if h.get("status") == "online"
            ),
            "critical_alerts": sum(1 for a in alerts if a["severity"] == "critical"),
            "warning_alerts": sum(1 for a in alerts if a["severity"] == "warning"),
            "avg_health": (
                round(sum(r["score"] for r in health_scores.values()) / len(health_scores))
                if health_scores else 0
            ),
        }
    }

    storage.save_pulse_snapshot(snapshot)
    return snapshot
