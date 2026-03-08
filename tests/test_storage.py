import os
import shutil
import unittest
from unittest.mock import patch, MagicMock
import json
import sys
from types import ModuleType

# Mock 'requests' and other potentially missing dependencies
sys.modules['requests'] = ModuleType('requests')
bs4_mock = ModuleType('bs4')
bs4_mock.BeautifulSoup = MagicMock()
sys.modules['bs4'] = bs4_mock
sys.modules['markdownify'] = ModuleType('markdownify')
sys.modules['git'] = ModuleType('git')
sys.modules['pandas'] = ModuleType('pandas')
sys.modules['streamlit'] = ModuleType('streamlit')

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from satya.core.storage import save_json, load_json, ensure_satya_dirs

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_storage_dir"
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_load_json_success(self):
        filepath = os.path.join(self.test_dir, "test.json")
        data = {"key": "value"}

        self.assertTrue(save_json(filepath, data))
        self.assertTrue(os.path.exists(filepath))

        loaded_data = load_json(filepath)
        self.assertEqual(loaded_data, data)

    @patch("os.rename")
    def test_save_json_cleanup_on_failure(self, mock_rename):
        mock_rename.side_effect = OSError("Mock rename failure")

        filepath = os.path.join(self.test_dir, "fail.json")
        tmp_filepath = filepath + ".tmp"
        data = {"key": "value"}

        # We expect it to return False
        self.assertFalse(save_json(filepath, data))

        # The temp file should have been cleaned up
        self.assertFalse(os.path.exists(tmp_filepath))
        # The target file should not exist
        self.assertFalse(os.path.exists(filepath))

    def test_load_json_nonexistent(self):
        filepath = os.path.join(self.test_dir, "nonexistent.json")
        self.assertEqual(load_json(filepath), {})

    def test_ensure_satya_dirs(self):
        import satya.core.storage as storage
        with patch.multiple(storage,
                          TASKS_DIR=os.path.join(self.test_dir, "tasks"),
                          TRUTH_DIR=os.path.join(self.test_dir, "truth"),
                          AGENTS_DIR=os.path.join(self.test_dir, "agents")):
            ensure_satya_dirs()

            self.assertTrue(os.path.exists(os.path.join(self.test_dir, "tasks")))
            self.assertTrue(os.path.exists(os.path.join(self.test_dir, "truth")))
            self.assertTrue(os.path.exists(os.path.join(self.test_dir, "agents")))

if __name__ == "__main__":
    unittest.main()
