import os
import time
from datetime import datetime, timezone
import logging
from . import storage
from .tasks import Tasks, STATUS_IN_PROGRESS, STATUS_QUEUED, STATUS_FAILED

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

    def _reassign_task(self, task: dict, agent_name: str):
        """Resets a single task locked by a dead agent to queued."""
        logger.info(f"Orchestrator: Reassigning task {task['id']} from dead agent {agent_name}")

        updates = {
            "status": STATUS_QUEUED,
            "assignee": "Unassigned",
            "locked_by": None,
            "locked_at": None
        }
        self.tasks.update_task(task["id"], updates, agent_name="AI_Orchestrator")

        self.tasks.add_comment(
            task["id"],
            f"Task reassigned to queue because agent '{agent_name}' stopped sending heartbeats.",
            commit=False,
            agent_name="AI_Orchestrator"
        )

    def _escalate_stale_tasks(self, queued_tasks: list[dict], now: datetime):
        """Bumps priority of tasks that have been queued for too long."""
        priority_ladder = ["Low", "Medium", "High", "Critical"]
        # e.g. 5 minutes for demonstration
        stale_threshold_seconds = 300

        for task in queued_tasks:
            current_priority = task.get("priority", "Medium")
            if current_priority == "Critical":
                continue # Already at max priority

            created_at_str = task.get("created_at")
            if not created_at_str:
                continue

            try:
                if created_at_str.endswith("Z"):
                    created_at_str = created_at_str[:-1] + "+00:00"
                created_at = datetime.fromisoformat(created_at_str)
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)

                elapsed = (now - created_at).total_seconds()

                # Check when it was last updated or escalated
                # If there are comments by AI_Orchestrator about escalation, use that timestamp
                last_escalation_time = created_at
                audit_trail = task.get("audit_trail", [])
                for event in reversed(audit_trail):
                    if event.get("action") == "priority_escalated":
                        ts_str = event.get("timestamp")
                        if ts_str:
                            if ts_str.endswith("Z"):
                                ts_str = ts_str[:-1] + "+00:00"
                            last_escalation_time = datetime.fromisoformat(ts_str)
                            if last_escalation_time.tzinfo is None:
                                last_escalation_time = last_escalation_time.replace(tzinfo=timezone.utc)
                        break

                time_since_last_action = (now - last_escalation_time).total_seconds()

                if time_since_last_action > stale_threshold_seconds:
                    try:
                        idx = priority_ladder.index(current_priority)
                        new_priority = priority_ladder[idx + 1]

                        logger.info(f"Orchestrator: Escalating SLA for task {task['id']} ({current_priority} -> {new_priority})")

                        self.tasks.update_task(
                            task["id"],
                            {"priority": new_priority},
                            agent_name="AI_Orchestrator"
                        )

                        self.tasks.add_comment(
                            task["id"],
                            f"SLA Escalation: Task priority bumped from {current_priority} to {new_priority} due to queue time.",
                            commit=False,
                            agent_name="AI_Orchestrator"
                        )

                        # Add audit event
                        from satya.auth import append_audit_event
                        append_audit_event(
                            "AI_Orchestrator",
                            task["id"],
                            task.get("trace_id", "unknown"),
                            "priority_escalated",
                            f"Escalated priority to {new_priority}"
                        )
                    except ValueError:
                        pass # Should not happen if priority is in ladder

            except ValueError:
                pass

    def scan_once(self):
        """Performs a single scan of heartbeats and reassigns tasks if necessary."""
        logger.info("AI Orchestrator heartbeat scan running...")
        now = datetime.now(timezone.utc)
        heartbeats = self._get_agent_heartbeats()

        # Fetch all tasks once to prevent N+1 read bottleneck
        all_tasks = self.tasks.list_all()
        in_progress_tasks = [t for t in all_tasks if t.get("status") == STATUS_IN_PROGRESS]
        failed_tasks = [t for t in all_tasks if t.get("status") == STATUS_FAILED and not t.get("rca_spawned")]
        queued_tasks = [t for t in all_tasks if t.get("status") == STATUS_QUEUED]

        # Process SLA Escalation for Queued Tasks
        self._escalate_stale_tasks(queued_tasks, now)

        # Handle failed tasks (Automated Issue Resolution Workflow)
        for task in failed_tasks:
            logger.info(f"Orchestrator: Spawning RCA task for failed task {task['id']}")
            rca_title = f"RCA: Debug Failed Task '{task['title']}'"
            rca_desc = f"Automated Root Cause Analysis for task {task['id']} ({task['title']}). Please investigate the failure reasons and propose fixes."

            # Spawn the RCA task
            self.tasks.create_task(
                title=rca_title,
                description=rca_desc,
                assignee="Unassigned",
                priority="High",
                agent_name="AI_Orchestrator",
                parent_trace_id=task.get("trace_id")
            )

            # Mark the original task to prevent duplicate RCAs
            self.tasks.update_task(task["id"], {"rca_spawned": True}, agent_name="AI_Orchestrator")

        # Process Time-Box Enforcement for In Progress Tasks
        from .watchdog import WatchdogChecker
        checker = WatchdogChecker(self.repo_path)
        stale_tasks = checker.scan(in_progress_tasks)
        for task in stale_tasks:
            logger.warning(f"Orchestrator: Task {task['id']} exceeded time limit of {task.get('time_limit_minutes')} minutes.")
            self.tasks.update_task_status(task["id"], STATUS_FAILED, agent_name="AI_Orchestrator")
            self.tasks.add_comment(
                task["id"],
                f"Time-Box Enforcement: Task automatically failed because it exceeded its time limit of {task.get('time_limit_minutes')} minutes.",
                commit=False,
                agent_name="AI_Orchestrator"
            )

        # Refresh in_progress_tasks after potential failures
        all_tasks = self.tasks.list_all()
        in_progress_tasks = [t for t in all_tasks if t.get("status") == STATUS_IN_PROGRESS]

        # Group tasks by assignee in-memory
        tasks_by_agent = {}
        for task in in_progress_tasks:
            assignee = task.get("assignee")
            if assignee and assignee != "Unassigned":
                tasks_by_agent.setdefault(assignee, []).append(task)

        for agent_name, tasks in tasks_by_agent.items():
            last_heartbeat = heartbeats.get(agent_name)
            is_dead = False

            if not last_heartbeat:
                # Agent has never sent a heartbeat. We will still check grace period below.
                is_dead = True
            else:
                elapsed = (now - last_heartbeat).total_seconds()
                if elapsed > self.timeout_seconds:
                    is_dead = True

            if is_dead:
                for task in tasks:
                    locked_at_str = task.get("locked_at")
                    grace_period_expired = True

                    if locked_at_str:
                        try:
                            if locked_at_str.endswith("Z"):
                                locked_at_str = locked_at_str[:-1] + "+00:00"
                            locked_at = datetime.fromisoformat(locked_at_str)
                            if locked_at.tzinfo is None:
                                locked_at = locked_at.replace(tzinfo=timezone.utc)

                            lock_elapsed = (now - locked_at).total_seconds()
                            if lock_elapsed <= self.timeout_seconds:
                                grace_period_expired = False
                        except ValueError:
                            pass

                    if grace_period_expired:
                        logger.warning(f"Agent {agent_name} is dead. Reassigning task {task['id']}.")
                        self._reassign_task(task, agent_name)
                    else:
                        logger.info(f"Agent {agent_name} has no recent heartbeat but task {task['id']} is within grace period.")

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
