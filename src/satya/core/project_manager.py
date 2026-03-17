import os
import time
from datetime import datetime, timezone
import logging
from . import storage
from .tasks import Tasks, STATUS_IN_PROGRESS, STATUS_QUEUED

logger = logging.getLogger(__name__)

class AIOrchestrator:
    def __init__(self, repo_path=".", timeout_seconds=60):
        self.repo_path = repo_path
        self.timeout_seconds = timeout_seconds
        self.tasks = Tasks(repo_path)
        storage.ensure_satya_dirs()

    def _get_agent_heartbeats(self) -> dict[str, datetime]:
        """Reads all heartbeat files and returns a dictionary of agent_name -> last_heartbeat_time."""
        heartbeats = {}
        if not os.path.exists(storage.HEARTBEATS_DIR):
            return heartbeats

        for filename in os.listdir(storage.HEARTBEATS_DIR):
            if not filename.endswith(".json"):
                continue

            agent_name = filename[:-5]
            filepath = os.path.join(storage.HEARTBEATS_DIR, filename)

            data = storage.load_json(filepath)
            if data and "timestamp" in data:
                ts_str = data["timestamp"]
                try:
                    if ts_str.endswith("Z"):
                        ts_str = ts_str[:-1] + "+00:00"

                    dt = datetime.fromisoformat(ts_str)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    heartbeats[agent_name] = dt
                except ValueError as e:
                    logger.error(f"Invalid heartbeat timestamp for {agent_name}: {e}")

        return heartbeats

    def _reassign_tasks_for_agent(self, agent_name: str, active_tasks_for_agent: list[dict] = None):
        """Finds tasks locked by the dead agent and resets them to queued.

        ⚡ Bolt Optimization:
        Accepts an optional `active_tasks_for_agent` list to avoid redundant
        file system scans (N+1 reads) for each dead agent in the orchestrator loop.
        """
        if active_tasks_for_agent is not None:
            all_tasks = active_tasks_for_agent
        else:
            all_tasks = self.tasks.get_tasks(status=STATUS_IN_PROGRESS, assignee=agent_name)

        for task in all_tasks:
            logger.info(f"Orchestrator: Reassigning task {task['id']} from dead agent {agent_name}")

            # Use update_task to directly modify fields without status transition restrictions,
            # since update_task_status doesn't allow in_progress -> queued.
            # However, we must ensure consistency and follow the same update rules.

            # Since update_task_status only allows specific transitions, and in_progress -> queued is not one of them,
            # we need to manually update it using update_task, but we should also update the audit trail.

            updates = {
                "status": STATUS_QUEUED,
                "assignee": "Unassigned",
                "locked_by": None,
                "locked_at": None
            }
            self.tasks.update_task(task["id"], updates, agent_name="AI_Orchestrator")

            # Add a specific comment about the failure
            self.tasks.add_comment(
                task["id"],
                f"Task reassigned to queue because agent '{agent_name}' stopped sending heartbeats.",
                commit=False,
                agent_name="AI_Orchestrator"
            )

    def scan_once(self):
        """Performs a single scan of heartbeats and reassigns tasks if necessary."""
        now = datetime.now(timezone.utc)
        heartbeats = self._get_agent_heartbeats()

        # Also need to check all active tasks to see if their assignee has a heartbeat.
        # If an agent never sent a heartbeat, but has tasks, we shouldn't kill them immediately,
        # but the standard is they must send heartbeats.

        in_progress_tasks = self.tasks.get_tasks(status=STATUS_IN_PROGRESS)
        tasks_by_agent = {}
        for t in in_progress_tasks:
            assignee = t.get("assignee")
            if assignee and assignee != "Unassigned":
                tasks_by_agent.setdefault(assignee, []).append(t)

        for agent_name, agent_tasks in tasks_by_agent.items():
            last_heartbeat = heartbeats.get(agent_name)

            # If no heartbeat at all, or it's too old
            if not last_heartbeat:
                # To be safe, maybe don't kill agents with NO heartbeat file,
                # as they might be old agents that don't support it.
                # But strict orchestrator requires heartbeats.
                # Let's say if there is NO heartbeat file, we assume dead.
                logger.warning(f"Agent {agent_name} has no heartbeat file. Reassigning tasks.")
                self._reassign_tasks_for_agent(agent_name, active_tasks_for_agent=agent_tasks)
            else:
                elapsed = (now - last_heartbeat).total_seconds()
                if elapsed > self.timeout_seconds:
                    logger.warning(f"Agent {agent_name} heartbeat timeout ({elapsed}s > {self.timeout_seconds}s). Reassigning tasks.")
                    self._reassign_tasks_for_agent(agent_name, active_tasks_for_agent=agent_tasks)

    def run(self, poll_interval=10, run_once=False):
        """Main loop for the orchestrator."""
        logger.info(f"AI Orchestrator started. Polling every {poll_interval}s, timeout {self.timeout_seconds}s.")
        while True:
            try:
                self.scan_once()
            except Exception as e:
                logger.error(f"Error in orchestrator loop: {e}")

            if run_once:
                break

            time.sleep(poll_interval)
