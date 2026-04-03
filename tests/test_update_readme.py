import os
import json
from update_readme import update_readme_content

def test_update_readme_content():
    # Setup mock data
    analytics = {
        "timestamp": "2026-04-03T15:00:00Z",
        "issues_prs": {"open": "5"},
        "ci": {"status": "passing"}
    }

    original_readme = (
        "---\n"
        "title: Satya\n"
        "---\n\n"
        "## Some Header\n\n"
        "Some content."
    )

    new_readme = update_readme_content(analytics, original_readme)

    assert "## Repository Status" in new_readme
    assert "- **Last Analytics Run:** 2026-04-03T15:00:00Z" in new_readme
    assert "- **Open Issues:** 5" in new_readme
    assert "- **Recent CI Status:** passing" in new_readme

    # Check it doesn't break frontmatter
    assert new_readme.startswith("---\n")
