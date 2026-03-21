import sys
import time
import os
import json

from unittest.mock import MagicMock
sys.modules['requests'] = MagicMock()
sys.modules['bs4'] = MagicMock()
sys.modules['git'] = MagicMock()
sys.modules['streamlit'] = MagicMock()
sys.modules['markdownify'] = MagicMock()

from src.satya.sdk import init

# Ensure we're authorized
os.environ['SATYA_AGENT_KEY'] = 'test-run'
os.environ['SATYA_AGENT_KEYS'] = 'test-run'

from unittest.mock import patch

def run():
    client = init("sim_agent")
    latencies = []

    try:
        with patch('src.satya.core.completion.CompletionChecker.check', return_value=True):
            # create tasks
            for i in range(5):
                t0 = time.time()
                task = client.create_task(f"Sim Task {i}", "Simulating runtime performance testing.")
                latencies.append(("create", time.time() - t0))

                t0 = time.time()
                client.update_task(task['id'], "in_progress")
                latencies.append(("update", time.time() - t0))

                t0 = time.time()
                client.log(f"Doing work on {task['id']}")
                latencies.append(("log", time.time() - t0))

                client.tasks.add_comment(task['id'], f"Progressing on {task['id']}", agent_name="sim_agent")

                t0 = time.time()
                client.update_task(task['id'], "done")
                latencies.append(("complete", time.time() - t0))
    except Exception as e:
        sys.stderr.write(f"Error during simulation: {e}\n")

    return latencies

if __name__ == '__main__':
    lats = run()
    print(json.dumps(lats))
