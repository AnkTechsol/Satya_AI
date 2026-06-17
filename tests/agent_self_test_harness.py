import os
import sys
import json
import time
import subprocess
import statistics
from datetime import datetime, timezone

def main():
    print("Running Agent Self-Test Harness...")
    start_time = time.time()

    try:
        sim_out = subprocess.check_output(
            ["python3", "run_sim.py"],
            text=True, stderr=subprocess.STDOUT
        ).strip()

        # Test the core features using pytest with proper env vars
        env = dict(os.environ)
        env["PYTHONPATH"] = "."
        env["AUDIT_SECRET"] = "dummy_secret"
        env["SATYA_AGENT_KEY"] = "DEMO_KEY"
        env["SATYA_AGENT_KEYS"] = "DEMO_KEY"

        test_out = subprocess.check_output(
            ["python3", "-m", "pytest", "tests/", "-q", "--maxfail=1"],
            text=True, stderr=subprocess.STDOUT, env=env
        )
        duration = time.time() - start_time
        print(f"Agent Self-Test Harness passed successfully in {duration:.2f}s.")

        # Update repo_analytics.json with the results
        # Run generate_analytics to get the latest base
        subprocess.check_output(["python3", "generate_analytics.py"], env=env)

        print("Metrics updated in repo_analytics.json and REPO_ANALYTICS.md")

    except subprocess.CalledProcessError as e:
        print(f"Harness failed:\n{e.output}")
        sys.exit(1)

if __name__ == '__main__':
    main()
