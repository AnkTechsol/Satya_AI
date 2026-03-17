import sys
sys.path.insert(0, "src")
import satya.sdk as satya
import time
import json
import statistics
from satya.core.tasks import STATUS_QUEUED, STATUS_IN_PROGRESS, STATUS_DONE

def test_harness():
    print("Starting agent self-test harness...")
    import os
    os.environ["SATYA_OTLP_ENDPOINT"] = "http://localhost:4318/v1/traces"
    client = satya.init(agent_name="test_runner")

    latencies = []

    for i in range(5):
        start = time.time()
        # Create a task with file_exists criteria that trivially passes
        task = client.create_task(f"Test Task {i}", f"This is an automated test task {i}")
        # Need to hack the DB to bypass completion criteria for tests
        import satya.core.storage as storage
        t = storage.load_json(storage.get_task_path(task["id"]))
        t["completion_criteria"] = {"type": "file_exists", "path": "run_self_test.py"}
        storage.save_json(storage.get_task_path(task["id"]), t)

        client.update_task(task["id"], "in_progress")
        satya.log(f"Working on task {i}...")
        client.update_task(task["id"], "done")
        duration = time.time() - start
        latencies.append(duration)

    client.flush_logs()

    metrics = {
        "median_latency_s": statistics.median(latencies),
        "p95_latency_s": statistics.quantiles(latencies, n=100)[94] if len(latencies) >= 2 else max(latencies),
        "p99_latency_s": statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 2 else max(latencies),
        "total_test_tasks_processed": len(latencies)
    }

    # Clean up test tasks
    for t_id in [t["id"] for t in client.tasks.list_all() if "Test Task" in t["title"]]:
        client.tasks.delete_task(t_id)

    print(f"Test Harness Metrics: {metrics}")

    # Update analytics JSON
    try:
        with open("repo_analytics.json", "r") as f:
            analytics = json.load(f)
    except FileNotFoundError:
        analytics = {}

    analytics["runtime_simulation"] = metrics

    with open("repo_analytics.json", "w") as f:
        json.dump(analytics, f, indent=2)

    print("Metrics saved to repo_analytics.json")

if __name__ == "__main__":
    test_harness()
