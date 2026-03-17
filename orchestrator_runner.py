#!/usr/bin/env python3
"""
orchestrator_runner.py — Satya AI Orchestrator Daemon
Run this script to monitor agent heartbeats and reassign orphaned tasks.

Usage:
    python orchestrator_runner.py --timeout 60 --poll-interval 10
"""

import sys
import argparse
import logging
from datetime import datetime

sys.path.insert(0, "src")
from satya.core.project_manager import AIOrchestrator

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

def run(timeout_seconds: int, poll_interval: int):
    logger.info(f"Starting AI Orchestrator... (Timeout: {timeout_seconds}s, Poll: {poll_interval}s)")
    orchestrator = AIOrchestrator(timeout_seconds=timeout_seconds)
    orchestrator.run(poll_interval=poll_interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Satya AI Orchestrator Daemon")
    parser.add_argument("--timeout", type=int, default=60, help="Seconds before considering an agent dead.")
    parser.add_argument("--poll-interval", type=int, default=10, help="Seconds between heartbeat checks.")
    args = parser.parse_args()

    run(args.timeout, args.poll_interval)
