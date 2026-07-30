import os
import shutil
import unittest
from unittest.mock import patch, MagicMock
import sys
from types import ModuleType
from datetime import datetime, timezone, timedelta

# Ensure mock dependencies are loaded to avoid import errors in other modules
sys.modules['requests'] = ModuleType('requests')
bs4_mock = ModuleType('bs4')
bs4_mock.BeautifulSoup = MagicMock()
sys.modules['bs4'] = bs4_mock
sys.modules['markdownify'] = ModuleType('markdownify')
sys.modules['git'] = ModuleType('git')
sys.modules['pandas'] = ModuleType('pandas')
sys.modules['streamlit'] = ModuleType('streamlit')

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from src.satya.core.pulse import compute_agent_health, compute_velocity_matrix, detect_cascade_failures, snapshot_pulse
from src.satya.core import storage

class TestPulse(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_pulse_dir"
        os.makedirs(self.test_dir, exist_ok=True)
        storage.set_root(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_compute_agent_health_empty(self):
        result = compute_agent_health("test_agent", [])
        self.assertEqual(result["agent"], "test_agent")
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["grade"], "N/A")

    def test_compute_agent_health_perfect(self):
        now_str = datetime.now(timezone.utc).isoformat() + "Z"
        tasks = [
            {
                "id": "task1",
                "assignee": "test_agent",
                "status": "done",
                "priority": "Medium",
                "completed_at": now_str,
                "comments": [{"agent": "test_agent", "timestamp": now_str, "text": "log1"}]
            }
        ]
        result = compute_agent_health("test_agent", tasks)
        self.assertEqual(result["agent"], "test_agent")
        self.assertTrue(result["score"] > 80)
        self.assertEqual(result["grade"], "A")

    def test_detect_cascade_failures(self):
        tasks = [
            {"id": "t1", "assignee": "test_agent", "status": "failed", "priority": "High", "updated_at": "2026-06-18T10:00:00Z"},
            {"id": "t2", "assignee": "test_agent", "status": "failed", "priority": "High", "updated_at": "2026-06-18T10:05:00Z"},
            {"id": "t3", "assignee": "test_agent", "status": "failed", "priority": "High", "updated_at": "2026-06-18T10:10:00Z"}
        ]
        alerts = detect_cascade_failures(tasks)
        self.assertTrue(any(a["severity"] == "critical" for a in alerts))

    def test_compute_velocity_matrix(self):
        tasks = [
            {
                "id": "t1",
                "assignee": "test_agent",
                "status": "done",
                "priority": "High",
                "locked_at": "2026-06-18T10:00:00Z",
                "completed_at": "2026-06-18T10:30:00Z"
            }
        ]
        matrix = compute_velocity_matrix(tasks)
        self.assertIn("test_agent", matrix["agents"])
        self.assertEqual(matrix["priority_buckets"]["test_agent"]["High"], 30.0)

    def test_snapshot_pulse(self):
        tasks = []
        heartbeats = {"test_agent": {"status": "online", "last_seen": "2026-06-18T10:00:00Z"}}
        snapshot = snapshot_pulse(tasks, heartbeats)
        self.assertEqual(snapshot["summary"]["total_agents"], 1)
        self.assertEqual(snapshot["summary"]["live_agents"], 1)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "satya_data", "pulse", "latest.json")))

if __name__ == "__main__":
    unittest.main()
