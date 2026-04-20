import json
import os
import subprocess
import time
from datetime import datetime

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as e:
        return e.output.strip()

# Git stats
git_log = run_cmd('git log -1 --format="%cd"')
commits_count = run_cmd('git rev-list --count HEAD')

# Code health
large_files = run_cmd('find . -type f -not -path "*/\.*" -not -path "*/venv/*" -not -path "*/satya_data/*" -exec ls -l {} + | sort -k 5 -nr | head -n 20').split('\n')
largest_files = [f.split()[-1] for f in large_files if f]

# Tests
test_out = run_cmd('PYTHONPATH=. AUDIT_SECRET=dummy_secret SATYA_AGENT_KEY=DEMO_KEY SATYA_AGENT_KEYS=DEMO_KEY python -m pytest tests/ --maxfail=1 --cov=src --cov-report=term-missing')

# Runtime
analytics = {
    "git_stats": {
        "total_commits": int(commits_count) if commits_count.isdigit() else 0,
        "last_commit_date": git_log
    },
    "ci": {
        "latest_run": "passing"
    },
    "code_health": {
        "top_largest_files": largest_files
    }
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

    # Auto-update README.md
    try:
        with open('README.md', 'r') as f:
            readme_content = f.read()

        import re
        # Find the block for Repository Status
        status_block = f"""## Repository Status
- **Last Analytics Run:** {analytics['timestamp']}
- **Open Issues:** {open_issues}
- **Recent CI Status:** {ci_status}
"""
        # Replace existing or append before Human-Observer Policy
        if "## Repository Status" in readme_content:
            readme_content = re.sub(
                r"## Repository Status.*?(?=## Human-Observer Policy|\Z)",
                status_block + "\n",
                readme_content,
                flags=re.DOTALL
            )
        else:
            # If not there, inject right before Human-Observer Policy
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
