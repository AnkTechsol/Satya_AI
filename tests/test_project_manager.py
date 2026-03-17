import os
import shutil
import unittest
import json
from datetime import datetime, timezone, timedelta
import sys

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from satya.core.project_manager import AIOrchestrator
from satya.core.tasks import Tasks, STATUS_QUEUED, STATUS_IN_PROGRESS
from satya.core import storage

class TestProjectManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_pm_dir"
        os.makedirs(self.test_dir, exist_ok=True)

        # Override storage directories for tests
        storage.SATYA_DIR = self.test_dir
        storage.TASKS_DIR = os.path.join(self.test_dir, "tasks")
        storage.TRUTH_DIR = os.path.join(self.test_dir, "truth")
        storage.AGENTS_DIR = os.path.join(self.test_dir, "agents")
        storage.HEARTBEATS_DIR = os.path.join(self.test_dir, "heartbeats")
        storage.CHAT_DIR = os.path.join(self.test_dir, "chat")

        storage.ensure_satya_dirs()
        self.tasks = Tasks(self.test_dir)
        self.orchestrator = AIOrchestrator(repo_path=self.test_dir, timeout_seconds=10)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_reassign_dead_agent_task(self):
        # Create a task
        task = self.tasks.create_task("Test task", "Testing orchestrator", assignee="Unassigned")
        self.assertIsNotNone(task)
        task_id = task["id"]

        # Assign it to agent_1 and set to in_progress
        self.tasks.update_task_status(task_id, STATUS_IN_PROGRESS, agent_name="agent_1")
        self.tasks.update_task(task_id, {"assignee": "agent_1"}, agent_name="agent_1")

        updated_task = self.tasks.get_task(task_id)
        self.assertEqual(updated_task["status"], STATUS_IN_PROGRESS)
        self.assertEqual(updated_task["assignee"], "agent_1")

        # Create a stale heartbeat for agent_1
        stale_time = datetime.now(timezone.utc) - timedelta(seconds=20)
        heartbeat_data = {"timestamp": stale_time.isoformat().replace("+00:00", "") + "Z"}
        storage.save_json(os.path.join(storage.HEARTBEATS_DIR, "agent_1.json"), heartbeat_data)

        # Run orchestrator once
        self.orchestrator.run(run_once=True)

        # Verify task was reassigned to queued
        final_task = self.tasks.get_task(task_id)
        self.assertEqual(final_task["status"], STATUS_QUEUED)
        self.assertIsNone(final_task["locked_by"])
        self.assertIsNone(final_task["locked_at"])

    def test_ignore_active_agent_task(self):
        # Create a task
        task = self.tasks.create_task("Test task 2", "Testing orchestrator", assignee="Unassigned")
        self.assertIsNotNone(task)
        task_id = task["id"]

        # Assign it to agent_2 and set to in_progress
        self.tasks.update_task_status(task_id, STATUS_IN_PROGRESS, agent_name="agent_2")
        self.tasks.update_task(task_id, {"assignee": "agent_2"}, agent_name="agent_2")

        # Create a fresh heartbeat for agent_2
        fresh_time = datetime.now(timezone.utc) - timedelta(seconds=2)
        heartbeat_data = {"timestamp": fresh_time.isoformat().replace("+00:00", "") + "Z"}
        storage.save_json(os.path.join(storage.HEARTBEATS_DIR, "agent_2.json"), heartbeat_data)

        # Run orchestrator once
        self.orchestrator.run(run_once=True)

        # Verify task was NOT reassigned
        final_task = self.tasks.get_task(task_id)
        self.assertEqual(final_task["status"], STATUS_IN_PROGRESS)
        self.assertEqual(final_task["assignee"], "agent_2")

if __name__ == "__main__":
    unittest.main()
