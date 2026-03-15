#!/usr/bin/env python3
"""
orchestrator_runner.py — Satya AI Orchestrator Loop
Run this script to monitor agent heartbeats and automatically recover tasks
assigned to unresponsive agents.

Usage:
    python orchestrator_runner.py --poll-interval 30 --timeout-minutes 5
"""

import sys, time, argparse, logging
sys.path.insert(0, "src")

from satya.core.project_manager import Orchestrator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def run(poll_interval: int, timeout_minutes: int):
    orchestrator = Orchestrator(timeout_minutes=timeout_minutes)
    logging.info(f"Orchestrator started. Polling every {poll_interval}s with {timeout_minutes}m timeout.")

    while True:
        try:
            recovered = orchestrator.check_heartbeats()
            if recovered:
                logging.info(f"Recovered {len(recovered)} tasks.")
        except Exception as e:
            logging.error(f"ERROR in Orchestrator loop: {e}")

        time.sleep(poll_interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--poll-interval", type=int, default=30, help="How often to check heartbeats (seconds)")
    parser.add_argument("--timeout-minutes", type=int, default=5, help="Minutes before an agent is considered dead")
    args = parser.parse_args()
    run(args.poll_interval, args.timeout_minutes)
