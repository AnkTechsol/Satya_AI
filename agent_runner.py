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
            # Send heartbeat to Orchestrator
            client.send_heartbeat()

            # Check for manual overrides or chat messages
            messages = client.poll_chat()
            for msg in messages:
                satya.log(f"Received chat message: {msg}")

            # Use the SDK's pick_task to handle claiming and queueing
            task = client.pick_task()

            if task:
                satya.log(f"Picked up task: {task['title']} ({task['id']})")

                # Execution happens here — task dispatch logic TBD per task type
                try:
                    # Interpret the task.payload. If it instructs to "Use Satya" or references the repo,
                    # create subtask(s) via client.use_satya() so Satya executes them natively.
                    instr = task.get("description", "")
                    if "use satya" in instr.lower() or "satya" in instr.lower():
                        client.log(f"Detected 'Use Satya' instruction. Delegating.")
                        child = client.use_satya(instr, parent_trace_id=task.get("trace_id"))
                        # Wait or finish immediately based on task type. Here we mark Done.
                        client.finish_task("Done")
                    else:
                        # Placeholder for actual skill runner
                        satya.log(f"Executing standard task {task['id']}...")
                        time.sleep(1) # simulate work
                        client.finish_task("Done")
                except Exception as e:
                    satya.log(f"Task execution failed: {e}")
                    client.finish_task("failed")
            else:
                pass
        except Exception as e:
            satya.log(f"ERROR in runner loop: {e}")

        time.sleep(poll_interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-name", default="default_agent")
    parser.add_argument("--poll-interval", type=int, default=10)
    args = parser.parse_args()
    run(args.agent_name, args.poll_interval)
