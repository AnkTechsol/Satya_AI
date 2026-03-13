import time
from datetime import datetime, timezone
import argparse
import sys
import os

sys.path.insert(0, "src")
from satya.core.tasks import Tasks, STATUS_IN_PROGRESS, STATUS_QUEUED
from satya.core import storage

def start_orchestrator(repo_path: str = ".", timeout_minutes: int = 5, poll_interval: int = 30, run_once: bool = False):
    """
    Runs the AI Orchestrator / Project Manager.
    Monitors agent heartbeats and re-assigns tasks from dead agents.
    """
    print(f"Starting Satya AI Orchestrator. Monitoring for agents dead for > {timeout_minutes}m.")
    tasks_mgr = Tasks(repo_path)

    while True:
        try:
            # Refresh directory paths
            storage.TASKS_DIR = os.path.join(repo_path, "satya_data", "tasks")
            storage.TRUTH_DIR = os.path.join(repo_path, "satya_data", "truth")
            storage.AGENTS_DIR = os.path.join(repo_path, "satya_data", "agents")
            storage.HEARTBEATS_DIR = os.path.join(repo_path, "satya_data", "heartbeats")

            heartbeats = storage.get_heartbeats()
            now = datetime.now(timezone.utc)

            dead_agents = set()

            # Check heartbeats
            for agent_name, hb_data in heartbeats.items():
                last_seen_str = hb_data.get("last_seen")
                if not last_seen_str:
                    continue

                try:
                    clean_iso = last_seen_str
                    if clean_iso.endswith('Z'):
                        clean_iso = clean_iso[:-1]
                        if not ('+' in clean_iso or '-' in clean_iso.split('T')[-1]):
                            clean_iso += '+00:00'

                    last_seen = datetime.fromisoformat(clean_iso)
                    if last_seen.tzinfo is None:
                        last_seen = last_seen.replace(tzinfo=timezone.utc)

                    diff_minutes = (now - last_seen).total_seconds() / 60

                    if diff_minutes > timeout_minutes:
                        dead_agents.add(agent_name)
                except ValueError as e:
                    print(f"Error parsing date {last_seen_str}: {e}")
                    continue

            if dead_agents:
                # Find tasks assigned to dead agents that are In Progress
                all_tasks = tasks_mgr.list_all()
                for task in all_tasks:
                    if task.get("status") == STATUS_IN_PROGRESS and task.get("assignee") in dead_agents:
                        print(f"Agent {task.get('assignee')} is dead. Forcibly unlocking task {task['id']} ({task['title']})")

                        # Add a comment that the orchestrator intervened
                        tasks_mgr.add_comment(
                            task["id"],
                            f"Orchestrator: Agent {task.get('assignee')} missed heartbeat for >{timeout_minutes}m. Re-queueing task.",
                            agent_name="System_Orchestrator"
                        )

                        # Unlock and move back to queued
                        tasks_mgr.unlock_task(task["id"])

                        # Manually bypass completion check to queue
                        task_data = storage.load_json(storage.get_task_path(task["id"]))
                        task_data["status"] = STATUS_QUEUED
                        task_data["assignee"] = "Unassigned"
                        storage.save_json(storage.get_task_path(task["id"]), task_data)

                        # Also update the heartbeat status so it doesn't repeatedly log
                        hb_data = heartbeats.get(task.get("assignee"))
                        if hb_data:
                            hb_data["status"] = "offline"
                            storage.save_heartbeat(task.get("assignee"), hb_data)

        except Exception as e:
            print(f"Orchestrator Error: {e}")

        if run_once:
            break

        time.sleep(poll_interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Satya AI Orchestrator / Project Manager")
    parser.add_argument("--timeout", type=int, default=5, help="Minutes before an agent is considered dead")
    parser.add_argument("--interval", type=int, default=30, help="Polling interval in seconds")
    parser.add_argument("--repo-path", type=str, default=".", help="Path to Satya repository")
    args = parser.parse_args()

    start_orchestrator(args.repo_path, args.timeout, args.interval)
