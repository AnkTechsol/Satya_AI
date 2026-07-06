import os

def test_auto_readme_action_exists():
    workflow_path = ".github/workflows/auto_analytics.yml"
    assert os.path.exists(workflow_path), "Workflow file missing"
    with open(workflow_path, "r") as f:
        content = f.read()
    assert "git push origin main" in content, "Must contain git push to main"
    assert "python generate_analytics.py" in content, "Must run analytics script"
