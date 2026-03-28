import json
import re

def main():
    try:
        with open("repo_analytics.json", "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading repo_analytics.json: {e}")
        return

    timestamp = data.get("timestamp", "Unknown")
    open_issues = data.get("issues_prs", {}).get("open", "Unknown without GH CLI")
    ci_status = data.get("ci", {}).get("status", "Unknown")

    try:
        with open("README.md", "r") as f:
            readme = f.read()
    except Exception as e:
        print(f"Error reading README.md: {e}")
        return

    # Update Last Analytics Run
    readme = re.sub(
        r"- \*\*Last Analytics Run:\*\* .*",
        f"- **Last Analytics Run:** {timestamp}",
        readme
    )
    # Update Open Issues
    readme = re.sub(
        r"- \*\*Open Issues:\*\* .*",
        f"- **Open Issues:** {open_issues}",
        readme
    )
    # Update Recent CI Status
    readme = re.sub(
        r"- \*\*Recent CI Status:\*\* .*",
        f"- **Recent CI Status:** {ci_status}",
        readme
    )

    try:
        with open("README.md", "w") as f:
            f.write(readme)
        print("Successfully updated README.md with analytics data.")
    except Exception as e:
        print(f"Error writing README.md: {e}")

if __name__ == "__main__":
    main()
