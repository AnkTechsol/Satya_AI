import os
import json
import logging
import fcntl
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from . import storage
from .tasks import Tasks, STATUS_IN_PROGRESS, STATUS_QUEUED

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    AI Orchestrator that acts as an automated Project Manager.
    Monitors agent heartbeats and automatically reassigns 'in_progress' tasks
    back to 'queued' if an agent stops sending heartbeats.
    """
    def __init__(self, repo_path: str = ".", timeout_minutes: int = 5):
        self.repo_path = repo_path
        self.timeout_minutes = timeout_minutes
        self.tasks = Tasks(repo_path)
        storage.ensure_satya_dirs()

    def record_heartbeat(self, agent_name: str) -> bool:
        """
        Records the current timestamp as the latest heartbeat for the given agent.
        """
        if not agent_name:
            return False

        now = datetime.now(timezone.utc).isoformat() + "Z"
        data = {
            "agent": agent_name,
            "last_heartbeat": now
        }

        safe_agent_name = os.path.basename(agent_name)
        filepath = os.path.join(storage.HEARTBEATS_DIR, f"{safe_agent_name}.json")

        return storage.save_json(filepath, data)

    def _get_last_heartbeat(self, agent_name: str) -> Optional[datetime]:
        """
        Retrieves the last recorded heartbeat for an agent.
        """
        safe_agent_name = os.path.basename(agent_name)
        filepath = os.path.join(storage.HEARTBEATS_DIR, f"{safe_agent_name}.json")

        # Load directly because load_json creates an empty dict instead of None,
        # which evaluates to false if empty
        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except Exception as e:
            return None
        if not data or "last_heartbeat" not in data:
            return None

        last_heartbeat_str = data["last_heartbeat"]
        try:
            if last_heartbeat_str.endswith("Z"):
                last_heartbeat_str = last_heartbeat_str[:-1] + "+00:00"
            return datetime.fromisoformat(last_heartbeat_str)
        except ValueError:
            return None

    def check_heartbeats(self, run_once: bool = False) -> List[Dict[str, Any]]:
        """
        Scans all 'in_progress' tasks. If the assigned agent hasn't sent a heartbeat
        within `timeout_minutes`, the task is marked as stale, unlocked, and moved back to 'queued'.

        Returns a list of recovered tasks.
        """
        recovered_tasks = []

        # Get all tasks currently in progress
        in_progress_tasks = self.tasks.get_tasks(status=STATUS_IN_PROGRESS)

        now = datetime.now(timezone.utc)

        for task in in_progress_tasks:
            agent_name = task.get("locked_by")
            if not agent_name:
                continue

            last_heartbeat = self._get_last_heartbeat(agent_name)

            is_dead = False
            if not last_heartbeat:
                # If no heartbeat file exists but task is locked, we assume dead
                # unless they just started (compare locked_at)
                locked_at_str = task.get("locked_at")
                if locked_at_str:
                    try:
                        if locked_at_str.endswith("Z"):
                            locked_at_str = locked_at_str[:-1] + "+00:00"
                        locked_at = datetime.fromisoformat(locked_at_str)
                        if locked_at.tzinfo is None:
                            locked_at = locked_at.replace(tzinfo=timezone.utc)

                        elapsed = now - locked_at
                        if elapsed.total_seconds() / 60 > self.timeout_minutes:
                            is_dead = True
                    except ValueError:
                        is_dead = True
                else:
                    is_dead = True
            else:
                # Calculate time since last heartbeat
                if last_heartbeat.tzinfo is None:
                    last_heartbeat = last_heartbeat.replace(tzinfo=timezone.utc)

                elapsed = now - last_heartbeat
                if elapsed.total_seconds() / 60 > self.timeout_minutes:
                    is_dead = True

            if is_dead:
                task_id = task["id"]
                logger.warning(f"Agent '{agent_name}' heartbeat timeout. Recovering task '{task_id}'.")

                # We need to manually update it to avoid the state machine transition check in update_task_status
                # which doesn't allow IN_PROGRESS -> QUEUED

                filepath = storage.get_task_path(task_id)
                current_task = storage.load_json(filepath)

                if current_task and current_task.get("status") == STATUS_IN_PROGRESS:
                    current_task["status"] = STATUS_QUEUED
                    current_task["locked_by"] = None
                    current_task["locked_at"] = None
                    current_task["updated_at"] = now.isoformat() + "Z"

                    if "audit_trail" not in current_task:
                        current_task["audit_trail"] = []

                    current_task["audit_trail"].append({
                        "timestamp": now.isoformat() + "Z",
                        "agent": "Orchestrator",
                        "action": "Task Recovered",
                        "details": f"Agent '{agent_name}' timed out. Task returned to queued."
                    })

                    if storage.save_json(filepath, current_task):
                        self.tasks.git_handler.commit_and_push(
                            [filepath],
                            f"Orchestrator recovered task {task_id} from unresponsive agent {agent_name}"
                        )
                        recovered_tasks.append(current_task)

        return recovered_tasks
