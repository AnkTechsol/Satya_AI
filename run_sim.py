import sys
import time
import os
import json
from src.satya.sdk import init

# Ensure we're authorized
os.environ['SATYA_AGENT_KEY'] = 'test-run'
os.environ['SATYA_AGENT_KEYS'] = 'test-run'

def run():
    client = init("sim_agent")
    latencies = []

    # create tasks
    for i in range(5):
        t0 = time.time()
        task = client.create_task(f"Sim Task {i}", "Simulating runtime performance testing.")
        latencies.append(("create", time.time() - t0))

        t0 = time.time()
        client.update_task(task['id'], "In Progress")
        latencies.append(("update", time.time() - t0))

        t0 = time.time()
        client.log(f"Doing work on {task['id']}")
        latencies.append(("log", time.time() - t0))

        t0 = time.time()
        client.update_task(task['id'], "Done")
        latencies.append(("complete", time.time() - t0))

    return latencies

if __name__ == '__main__':
    lats = run()
    print(json.dumps(lats))
