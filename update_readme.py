import json
import re

def update_readme_content(analytics, readme):
    # Extract metrics. Note `ci_status` has no 'status' key in analytics.json by default except what generate_analytics.py does.
    # generate_analytics.py adds "status": ci_status.
    timestamp = analytics.get('timestamp', 'Unknown')
    open_issues = analytics.get('issues_prs', {}).get('open', 'Unknown')
    ci_status = analytics.get('ci', {}).get('status', 'Unknown')

    # Build the new section
    new_section = (
        f"## Repository Status\n"
        f"- **Last Analytics Run:** {timestamp}\n"
        f"- **Open Issues:** {open_issues}\n"
        f"- **Recent CI Status:** {ci_status}\n"
    )

    # Replace the existing Repository Status section
    pattern = re.compile(r"## Repository Status\n- \*\*Last Analytics Run:\*\*.*?\n- \*\*Open Issues:\*\*.*?\n- \*\*Recent CI Status:\*\*.*?\n", re.DOTALL)

    if pattern.search(readme):
        new_readme = pattern.sub(new_section, readme)
    else:
        # Avoid breaking frontmatter: find the second '---' if it starts with '---'
        if readme.startswith("---"):
            parts = readme.split("---", 2)
            if len(parts) >= 3:
                new_readme = "---" + parts[1] + "---\n\n" + new_section + parts[2]
            else:
                new_readme = new_section + "\n" + readme
        else:
            # Place after first markdown header or divider
            parts = readme.split("---", 1)
            if len(parts) > 1:
                new_readme = parts[0] + "---\n\n" + new_section + "\n" + parts[1]
            else:
                new_readme = new_section + "\n" + readme
    return new_readme

def main():
    try:
        with open('repo_analytics.json', 'r') as f:
            analytics = json.load(f)
    except Exception as e:
        print(f"Error loading analytics: {e}")
        return

    try:
        with open('README.md', 'r') as f:
            readme = f.read()
    except Exception as e:
        print(f"Error loading README: {e}")
        return

    new_readme = update_readme_content(analytics, readme)

    with open('README.md', 'w') as f:
        f.write(new_readme)

if __name__ == '__main__':
    main()
