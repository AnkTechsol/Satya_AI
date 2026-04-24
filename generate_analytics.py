import json
import os
import subprocess
import time
from datetime import datetime, timezone
import statistics

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as e:
        return e.output.strip()

# Git stats
git_log = run_cmd('git log -1 --format="%cd"')
commits_count = run_cmd('git rev-list --count HEAD')
commits_90d = run_cmd('git rev-list --count --since="90 days ago" HEAD')

# Issues (simulated since no GH CLI)
open_issues = "Unknown"
closed_issues = "Unknown"

# Code health
large_files = run_cmd('find . -type f -not -path "*/\\.*" -not -path "*/venv/*" -not -path "*/satya_data/*" -not -path "*/__pycache__/*" -exec ls -l {} + | sort -k 5 -nr | head -n 20').split('\n')
largest_files = [f.split()[-1] for f in large_files if f]

# Tests
has_tests = "Yes" if os.path.exists("tests") else "No"
has_github_actions = "Yes" if os.path.exists(".github/workflows") else "No"

test_out = run_cmd('PYTHONPATH=$PWD AUDIT_SECRET=dummy_secret SATYA_AGENT_KEY=DEMO_KEY SATYA_AGENT_KEYS=DEMO_KEY python -m pytest tests/ --maxfail=1 -q')
failing_tests = "0" if "failed" not in test_out.lower() else "1+"
ci_status = "passing" if failing_tests == "0" else "failing"

def main():
    # Run sim and calculate latencies
    sim_out = run_cmd('python run_sim.py')
    try:
        lats = json.loads(sim_out)
        create_lats = [lat[1] for lat in lats if lat[0] == "create"]
        complete_lats = [lat[1] for lat in lats if lat[0] == "complete"]

        create_median = statistics.median(create_lats) if create_lats else 0
        create_p95 = statistics.quantiles(create_lats, n=100)[94] if len(create_lats) > 1 else (create_lats[0] if create_lats else 0)
    except Exception as e:
        print(f"Error parsing sim: {e}")
        create_median = 0
        create_p95 = 0

    analytics = {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "git_stats": {
            "total_commits": int(commits_count) if commits_count.isdigit() else 0,
            "commits_90d": int(commits_90d) if commits_90d.isdigit() else 0,
            "last_commit_date": git_log
        },
        "issues": {
            "open": open_issues,
            "closed": closed_issues
        },
        "ci": {
            "latest_run": ci_status,
            "has_workflows": has_github_actions
        },
        "tests": {
            "has_tests": has_tests,
            "failing": failing_tests
        },
        "performance": {
            "task_create_median_s": create_median,
            "task_create_p95_s": create_p95
        },
        "code_health": {
            "top_largest_files": largest_files
        }
    }

    top_files = "\n".join(largest_files)

    with open('repo_analytics.json', 'w') as f:
        json.dump(analytics, f, indent=2)

    md = f"""# Repo Analytics

**Last Run**: {analytics['timestamp']}

## Git Stats
- **Commits (last 90d)**: {analytics['git_stats']['commits_90d']}
- **Last Commit Date**: {analytics['git_stats']['last_commit_date']}

## Issues & PRs
- **Open**: {analytics['issues']['open']}
- **Closed**: {analytics['issues']['closed']}

## CI & Tests
- **GitHub Actions**: {analytics['ci']['has_workflows']}
- **Tests Exist**: {analytics['tests']['has_tests']}
- **Failing Tests**: {analytics['tests']['failing']}

## Runtime Simulation
- **Median Task Creation Latency**: {analytics['performance']['task_create_median_s']:.4f}s
- **P95 Task Creation Latency**: {analytics['performance']['task_create_p95_s']:.4f}s

## Code Health
**Top 20 Largest Files:**
```text
{top_files}
```
"""
    with open('REPO_ANALYTICS.md', 'w') as f:
        f.write(md)

    # Auto-update README.md
    try:
        with open('README.md', 'r') as f:
            readme_content = f.read()

        import re
        status_block = f"""## Repository Status
- **Last Analytics Run:** {analytics['timestamp']}
- **Open Issues:** {analytics['issues']['open']}
- **Recent CI Status:** {analytics['ci']['latest_run']}
"""
        if "## Repository Status" in readme_content:
            readme_content = re.sub(
                r"## Repository Status.*?(?=## Human-Observer Policy|\Z)",
                status_block + "\n",
                readme_content,
                flags=re.DOTALL
            )
        else:
            readme_content = readme_content.replace(
                "## Human-Observer Policy",
                status_block + "\n## Human-Observer Policy"
            )

        with open('README.md', 'w') as f:
            f.write(readme_content)
    except Exception as e:
        print(f"Failed to auto-update README: {e}")

if __name__ == '__main__':
    main()
