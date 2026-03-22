import re

with open("README.md", "r") as f:
    content = f.read()

# Add link to COMPETITOR_MATRIX.md and REPO_ANALYTICS.md
content = re.sub(
    r'- \*\*Repo Analytics & Competitor Matrix\*\*',
    r'- **Repo Analytics & Competitor Matrix**\n  - View [Repo Analytics](REPO_ANALYTICS.md) and [Competitor Matrix](COMPETITOR_MATRIX.md).',
    content
)

with open("README.md", "w") as f:
    f.write(content)
