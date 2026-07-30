import os
import shutil
import unittest
from unittest.mock import patch, MagicMock
import sys
from types import ModuleType

# Use existing mocked modules from conftest or default to MagicMock if not present
if 'requests' not in sys.modules or not hasattr(sys.modules['requests'], 'post'):
    from unittest.mock import MagicMock
    sys.modules['requests'] = MagicMock()
if 'bs4' not in sys.modules:
    bs4_mock = MagicMock()
    sys.modules['bs4'] = bs4_mock
if 'markdownify' not in sys.modules:
    sys.modules['markdownify'] = MagicMock()
if 'git' not in sys.modules:
    sys.modules['git'] = MagicMock()
if 'pandas' not in sys.modules:
    sys.modules['pandas'] = MagicMock()
if 'streamlit' not in sys.modules:
    sys.modules['streamlit'] = MagicMock()


# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from satya.core.goal_guardian import GoalGuardian, save_goal, load_goal, load_goal_alerts
from satya.sdk.client import SatyaClient, GoalDriftError
from satya.core import storage

class TestGoalGuardian(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_goals_dir"
        os.makedirs(self.test_dir, exist_ok=True)
        storage.set_root(self.test_dir)
        
        # set up mock agent key env var
        os.environ["SATYA_AGENT_KEY"] = "DEMO_KEY"
        # Mock auth verification to keep it simple
        self.auth_patcher = patch("satya.auth.require_agent")
        self.mock_require_agent = self.auth_patcher.start()

    def tearDown(self):
        self.auth_patcher.stop()
        if os.environ.get("SATYA_AGENT_KEY"):
            del os.environ["SATYA_AGENT_KEY"]
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_and_load_goal(self):
        agent = "test_agent"
        goal = "Build user auth system using JWT"
        save_goal(agent, goal, 0.20, 0.10)
        
        loaded = load_goal(agent)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["goal"], goal)
        self.assertEqual(loaded["threshold"], 0.20)
        self.assertEqual(loaded["halt_threshold"], 0.10)

    def test_goal_guardian_alignment_ok(self):
        gg = GoalGuardian(agent_name="test_agent", goal="Build REST API", threshold=0.20, halt_threshold=0.05)
        # Highly aligned
        res = gg.check("Implement REST API endpoint for user data")
        self.assertTrue(res["aligned"])
        self.assertEqual(res["action"], "ok")

    def test_goal_guardian_alignment_drift_warn(self):
        gg = GoalGuardian(agent_name="test_agent", goal="Build user auth", threshold=0.50, halt_threshold=0.05)
        # Marginally/non-aligned message but above halt
        res = gg.check("Let's write a simple calculator application instead of auth")
        self.assertFalse(res["aligned"])
        self.assertEqual(res["action"], "warn")

    def test_goal_guardian_alignment_drift_halt(self):
        gg = GoalGuardian(agent_name="test_agent", goal="Build user auth", threshold=0.20, halt_threshold=0.15)
        # Totally unrelated message triggers halt
        res = gg.check("unrelated text to verify low score")
        self.assertFalse(res["aligned"])
        self.assertEqual(res["action"], "halt")
        self.assertIsNotNone(res["halt_directive"])

    def test_sdk_integration_raises_drift_error(self):
        # Initialize client
        client = SatyaClient(agent_name="test_agent", repo_path=self.test_dir)
        client.set_goal("Build user auth system", threshold=0.20, halt_threshold=0.15)
        # Set window to 1 so the aligned log doesn't carry over to the drifted log
        if client.goal_guardian:
            client.goal_guardian.window = 1
        
        # A highly aligned log should succeed
        client.log("Writing user login verification functionality")
        
        # A drifted log should raise GoalDriftError
        with self.assertRaises(GoalDriftError):
            client.log("unrelated word list that has completely zero similarity")

if __name__ == "__main__":
    unittest.main()
