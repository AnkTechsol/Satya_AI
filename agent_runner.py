#!/usr/bin/env python3
"""
agent_runner.py — Satya Agent Polling Loop
Run this script to start an agent that picks up queued tasks automatically.

Usage:
    python agent_runner.py --agent-name my_agent --poll-interval 10
"""

import sys, time, argparse
sys.path.insert(0, "src")
import satya.sdk as satya
from satya.core.tasks import get_tasks, update_task_status, lock_task
from satya.core.completion import CompletionChecker

def run(agent_name: str, poll_interval: int):
    client = satya.init(agent_name=agent_name)
    satya.log(f"Agent '{agent_name}' started. Polling every {poll_interval}s...")

    while True:
        try:
            queued = get_tasks(status="queued", assignee=agent_name)
            if queued:
                task = queued[0]
                satya.log(f"Picked up task: {task['title']} ({task['id']})")
                lock_task(task["id"], agent_name)
                update_task_status(task["id"], "in_progress", agent_name)
                # Execution happens here — task dispatch logic TBD per task type
                satya.log(f"Task {task['id']} marked in_progress. Awaiting execution.")
            else:
                satya.log("No queued tasks. Waiting...")
        except Exception as e:
            satya.log(f"ERROR in runner loop: {e}")

        time.sleep(poll_interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-name", default="default_agent")
    parser.add_argument("--poll-interval", type=int, default=10)
    args = parser.parse_args()
    run(args.agent_name, args.poll_interval)
