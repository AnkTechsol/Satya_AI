import json
import os
import subprocess
import datetime
import sys

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except Exception as e:
        return ""

def main():
    # Git stats
    commits_90d = run_cmd('git log --since="90 days ago" --oneline | wc -l')
    last_commit_date = run_cmd('git log -1 --format=%cd')
    authors = run_cmd('git shortlog -sn --since="90 days ago"')

    # CI
    has_github_actions = os.path.isdir('.github/workflows')
    ci_status = "Unknown (no .github/workflows found)" if not has_github_actions else "Requires GH CLI to check"

    # Tests
    test_output = run_cmd('PYTHONPATH=. pytest tests/ --maxfail=1 --tb=short')
    has_tests = os.path.isdir('tests')
    failing_tests = "failed" in test_output.lower()

    # Dependencies
    deps = []
    try:
        with open('pyproject.toml', 'r') as f:
            deps = [line.strip() for line in f.readlines() if '>=' in line or '==' in line]
    except:
        pass

    # Files
    top_files = run_cmd('find src -type f -exec wc -c {} + | sort -nr | head -20')

    # PRs and Issues
    open_issues = "Unknown without GH CLI"
    closed_issues = "Unknown without GH CLI"

    # Runtime Artifacts
    runtime_artifacts = run_cmd('find satya_data -type f | head -10')

    # Simulation (Mocking the requests since the environment lacks requests library)
    import time
    from unittest.mock import MagicMock
    sys.modules['requests'] = MagicMock()
    sys.modules['bs4'] = MagicMock()
    sys.modules['git'] = MagicMock()
    sys.modules['streamlit'] = MagicMock()
    sys.modules['markdownify'] = MagicMock()

    os.environ['SATYA_AGENT_KEY'] = 'test-run'
    os.environ['SATYA_AGENT_KEYS'] = 'test-run'

    from src.satya.sdk import init
    from src.satya.core.storage import save_json, load_json, get_task_path
    from unittest.mock import patch

    client = init("sim_agent")
    latencies = []

    try:
        with patch('src.satya.core.completion.CompletionChecker.check', return_value=True):
            for i in range(5):
                t0 = time.time()
                task = client.create_task(f"Sim Task {i}", "Simulating runtime performance testing.")
                latencies.append(time.time() - t0)

                client.update_task(task['id'], "in_progress")
                client.log(f"Doing work on {task['id']}")
                client.update_task(task['id'], "done")
    except Exception as e:
        print(f"Simulation failed: {e}")

    lat_sorted = sorted(latencies)
    median = lat_sorted[len(lat_sorted)//2] if lat_sorted else 0
    p95 = lat_sorted[int(len(lat_sorted)*0.95)] if lat_sorted else 0
    p99 = lat_sorted[int(len(lat_sorted)*0.99)] if lat_sorted else 0

    analytics = {
        "git": {
            "commits_last_90d": commits_90d,
            "last_commit_date": last_commit_date,
            "authors": authors.split('\n') if authors else []
        },
        "issues_prs": {
            "open": open_issues,
            "closed": closed_issues
        },
        "ci": {
            "has_github_actions": has_github_actions,
            "status": ci_status
        },
        "tests": {
            "has_tests": has_tests,
            "failing_tests": failing_tests
        },
        "dependencies": deps,
        "code_health": {
            "top_20_largest_files": top_files.split('\n') if top_files else []
        },
        "runtime_artifacts": runtime_artifacts.split('\n') if runtime_artifacts else [],
        "runtime_simulation": {
            "median_latency_s": median,
            "p95_latency_s": p95,
            "p99_latency_s": p99
        },
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    with open('repo_analytics.json', 'w') as f:
        json.dump(analytics, f, indent=2)

    md = f"""# Repo Analytics

**Last Run**: {analytics['timestamp']}

## Git Stats
- **Commits (last 90d)**: {commits_90d}
- **Last Commit Date**: {last_commit_date}

## Issues & PRs
- **Open**: {open_issues}
- **Closed**: {closed_issues}

## CI & Tests
- **GitHub Actions**: {has_github_actions}
- **Tests Exist**: {has_tests}
- **Failing Tests**: {failing_tests}

## Runtime Simulation
- **Median Task Creation Latency**: {median:.4f}s
- **P95 Task Creation Latency**: {p95:.4f}s

## Code Health
**Top 20 Largest Files:**
```
{top_files}
```

## Runtime Artifacts
```
{runtime_artifacts}
```
"""
    with open('REPO_ANALYTICS.md', 'w') as f:
        f.write(md)

if __name__ == '__main__':
    main()
