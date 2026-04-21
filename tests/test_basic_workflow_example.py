import importlib.util
import json
from pathlib import Path

import pytest


@pytest.fixture
def example_module():
    module_path = Path(__file__).resolve().parents[1] / "examples" / "basic_workflow" / "run_example.py"
    spec = importlib.util.spec_from_file_location("basic_workflow_example", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_basic_workflow_example_runs(monkeypatch, tmp_path, example_module):
    monkeypatch.setenv("SATYA_AGENT_KEYS", "DEMO_KEY")
    monkeypatch.setenv("SATYA_AGENT_KEY", "DEMO_KEY")
    monkeypatch.setenv("AUDIT_SECRET", "test_audit_secret")

    from satya.sdk.client import SatyaClient

    def fake_scrape_url(self, url):
        truth_dir = Path(self.repo_path) / "satya_data" / "truth"
        truth_dir.mkdir(parents=True, exist_ok=True)
        output_file = truth_dir / "Example_Domain.md"
        output_file.write_text(f"# Example Domain\n\nSource: {url}\n", encoding="utf-8")
        self.log(f"Saved scraped content to {output_file.name}")
        return output_file.name

    monkeypatch.setattr(SatyaClient, "scrape_url", fake_scrape_url)

    repo_path = tmp_path / "demo_repo"
    repo_path.mkdir()
    output_dir = repo_path / "satya_data" / "example_outputs" / "basic_workflow"

    summary = example_module.run_example(
        repo_path=repo_path,
        output_dir=output_dir,
        reference_url="https://example.com",
        agent_name="example_test_agent",
    )

    assert summary["scraped_filename"] == "Example_Domain.md"
    assert summary["completed_tasks"] == [
        "Capture a shared reference",
        "Draft an execution checklist",
    ]

    task_files = sorted((repo_path / "satya_data" / "tasks").glob("*.json"))
    assert len(task_files) == 2

    for task_file in task_files:
        task = json.loads(task_file.read_text(encoding="utf-8"))
        assert task["status"] == "done"
        assert task["comments"]
        assert task["audit_trail"]

    assert (repo_path / "satya_data" / "truth" / "Example_Domain.md").exists()
    assert (output_dir / "shared_reference_summary.md").exists()
    assert (output_dir / "execution_checklist.md").exists()
    assert (output_dir / "session_summary.json").exists()

    log_files = list((repo_path / "satya_data" / "agents").glob("example_test_agent_*.log"))
    assert len(log_files) == 1
