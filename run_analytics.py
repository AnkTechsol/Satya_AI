import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as e:
        return e.output.strip()

def collect_analytics():
    analytics = {}

    # Git Stats
    print("Collecting Git stats...")
    last_90d = run_cmd("git log --since='90 days ago' --format='%ad' --date=short | wc -l")
    analytics["git"] = {
        "commits_last_90d": int(last_90d) if last_90d.isdigit() else 0,
        "last_commit_date": run_cmd("git log -1 --format='%cd'"),
        "authors": run_cmd("git shortlog -sn --since='90 days ago' | head -n 5").split("\n")
    }

    # Files size
    print("Finding largest files...")
    largest_files = run_cmd("find . -type f -not -path '*/\.git/*' -not -path '*/__pycache__/*' -exec ls -lh {} + | sort -k 5 -rh | head -n 20")
    analytics["largest_files"] = largest_files.split("\n")

    # CI
    print("Checking CI...")
    has_github_actions = os.path.exists(".github/workflows")
    analytics["ci"] = {
        "has_github_actions": has_github_actions
    }

    # Tests
    print("Checking Tests...")
    has_tests = os.path.exists("tests")
    test_output = ""
    if has_tests:
        test_output = run_cmd("PYTHONPATH=. pytest --maxfail=1")

    analytics["tests"] = {
        "has_tests": has_tests,
        "output": test_output
    }

    # Dependencies
    print("Checking Dependencies...")
    analytics["dependencies"] = {
        "pyproject": run_cmd("cat pyproject.toml | grep -v '^#'"),
    }

    # Save JSON
    with open("repo_analytics.json", "w") as f:
        json.dump(analytics, f, indent=2)

    # Write MD
    with open("REPO_ANALYTICS.md", "w") as f:
        f.write("# Repository Analytics\n\n")
        f.write(f"Generated on: {datetime.now().isoformat()}\n\n")
        f.write("## Git Stats\n")
        f.write(f"- Commits (last 90d): {analytics['git']['commits_last_90d']}\n")
        f.write(f"- Last commit: {analytics['git']['last_commit_date']}\n")
        f.write("- Top authors:\n")
        for author in analytics['git']['authors']:
            f.write(f"  - {author}\n")

        f.write("\n## CI & Tests\n")
        f.write(f"- GitHub Actions: {'Yes' if has_github_actions else 'No'}\n")
        f.write(f"- Tests Directory: {'Yes' if has_tests else 'No'}\n")

        f.write("\n## Top Largest Files\n")
        f.write("```\n")
        f.write("\n".join(analytics["largest_files"]))
        f.write("\n```\n")

if __name__ == "__main__":
    collect_analytics()
