import sys
from unittest.mock import MagicMock

# Mocking dependencies that are missing in the environment and imported by core modules
sys.modules['requests'] = MagicMock()
sys.modules['bs4'] = MagicMock()
sys.modules['markdownify'] = MagicMock()
sys.modules['pandas'] = MagicMock()
sys.modules['git'] = MagicMock()
sys.modules['streamlit'] = MagicMock()


import os
os.environ["AUDIT_SECRET"] = "dummy_secret"
