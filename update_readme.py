import json, re

with open("repo_analytics.json") as f:
    data = json.load(f)
timestamp = data["timestamp"]
open_issues = data["issues_prs"]["open"]
ci_status = data["ci"]["status"]

with open("README.md", "r") as f:
    content = f.read()

content = re.sub(r"- \*\*Last Analytics Run:\*\* .*", f"- **Last Analytics Run:** {timestamp}", content)
content = re.sub(r"- \*\*Open Issues:\*\* .*", f"- **Open Issues:** {open_issues}", content)
content = re.sub(r"- \*\*Recent CI Status:\*\* .*", f"- **Recent CI Status:** {ci_status}", content)

with open("README.md", "w") as f:
    f.write(content)
