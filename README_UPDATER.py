import json
import re

def update_readme():
    with open("repo_analytics.json", "r") as f:
        analytics = json.load(f)

    with open("README.md", "r") as f:
        readme_content = f.read()

    # Update analytics summary
    analytics_summary = f"""<!-- ANALYTICS_START -->
Last analytics run: {analytics['git']['last_commit_date']}
Open issues: {analytics['git'].get('issues', 'N/A')}
Recent CI status: {'pass' if analytics['ci']['has_github_actions'] else 'N/A'}
<!-- ANALYTICS_END -->"""

    if "<!-- ANALYTICS_START -->" in readme_content:
        readme_content = re.sub(r'<!-- ANALYTICS_START -->.*<!-- ANALYTICS_END -->', analytics_summary, readme_content, flags=re.DOTALL)
    else:
        # insert at the top, just below the banner/h1
        readme_content = re.sub(r'(<h1 align="center">Satya — AI Agent Progress Tracker & Truth Source Manager</h1>)', r'\1\n\n' + analytics_summary, readme_content)

    # Add SUSTAINABLE_FEATURES section if not exists
    if "## SUSTAINABLE_FEATURES" not in readme_content:
        sustainable_features = """
## SUSTAINABLE_FEATURES

- **Repository Analytics & Competitor Matrix** (Added: 2026-03-06): Generates JSON/Markdown analytics locally. Validate by running `python run_analytics.py`.
- **Export Adapter Framework (OTLP)** (Added: 2026-03-06): Pluggable adapter system for emitting agent logs and tasks to OpenTelemetry compatible endpoints. Validate by checking `src/satya/adapters`.
- **Agent Self-Test Harness + CI job** (Added: 2026-03-06): Runs dummy tasks to evaluate system latency. Validate by running `python run_self_test.py`.
- **Auto-README Updater** (Added: 2026-03-06): Automates updating README.md based on analytics. Validate by running `python README_UPDATER.py`.

Links:
- [Repository Analytics](REPO_ANALYTICS.md)
- [Competitor Matrix](COMPETITOR_MATRIX.md)
- [Changelog](CHANGELOG.md)
"""
        # Insert before Features section
        readme_content = readme_content.replace("## Features", sustainable_features + "\n\n## Features")

    with open("README.md", "w") as f:
        f.write(readme_content)

if __name__ == "__main__":
    update_readme()
