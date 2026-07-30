#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

os.environ.setdefault("SATYA_AGENT_KEYS", "DEMO_KEY")
os.environ.setdefault("SATYA_AGENT_KEY", "DEMO_KEY")
os.environ.setdefault("AUDIT_SECRET", "basic-workflow-secret")

SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import satya.sdk as satya

DEFAULT_REFERENCE_URL = "https://example.com"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a small Satya workflow that populates tasks, logs, and truth sources."
    )
    parser.add_argument(
        "--repo-path",
        default=str(REPO_ROOT),
        help="Repository path where satya_data/ should be created.",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory for generated task artifacts. Defaults under satya_data/example_outputs/basic_workflow/.",
    )
    parser.add_argument(
        "--reference-url",
        default=DEFAULT_REFERENCE_URL,
        help="Public URL to scrape into Satya's truth source.",
    )
    parser.add_argument(
        "--agent-name",
        default="basic_workflow_agent",
        help="Agent name recorded in the Satya logs and task comments.",
    )
    return parser.parse_args()


def _display_path(path: Path, repo_path: Path) -> str:
    try:
        return str(path.relative_to(repo_path))
    except ValueError:
        return str(path)


def _write_artifact(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _build_artifact(task: dict, reference_url: str, scraped_filename: str | None, artifact_path: Path) -> None:
    if task["title"] == "Capture a shared reference":
        content = "\n".join(
            [
                "# Shared Reference Summary",
                "",
                f"- Source URL: {reference_url}",
                f"- Saved truth file: {scraped_filename or 'scrape failed'}",
                "- Demo purpose: show how a Satya agent stores shared knowledge before doing work.",
                "- Next step: use the queued task list to turn this reference into visible execution progress.",
                "",
            ]
        )
    else:
        content = "\n".join(
            [
                "# Execution Checklist",
                "",
                "1. Start the Streamlit dashboard so observers can watch the workflow.",
                "2. Initialize the SDK with an authenticated agent key.",
                "3. Create tasks with descriptions long enough to satisfy governance rules.",
                "4. Scrape a public reference URL into the truth source.",
                "5. Pick the highest priority queued task, log progress, and finish it after writing an artifact.",
                "6. Flush logs so the latest session output is persisted.",
                "",
            ]
        )

    _write_artifact(artifact_path, content)


def run_example(
    repo_path: str | Path,
    output_dir: str | Path | None = None,
    reference_url: str = DEFAULT_REFERENCE_URL,
    agent_name: str = "basic_workflow_agent",
) -> dict:
    repo_path = Path(repo_path).resolve()
    output_dir = Path(output_dir).resolve() if output_dir else repo_path / "satya_data" / "example_outputs" / "basic_workflow"
    output_dir.mkdir(parents=True, exist_ok=True)

    client = satya.init(agent_name=agent_name, repo_path=str(repo_path))
    satya.log("Starting the basic workflow example session.")

    task_specs = [
        {
            "title": "Capture a shared reference",
            "description": "Scrape a public reference page and summarize why it matters to the team.",
            "priority": "High",
            "artifact": output_dir / "shared_reference_summary.md",
        },
        {
            "title": "Draft an execution checklist",
            "description": "Create a short checklist that shows the follow-up workflow after research is complete.",
            "priority": "Medium",
            "artifact": output_dir / "execution_checklist.md",
        },
    ]

    task_artifacts: dict[str, Path] = {}
    for spec in task_specs:
        task = satya.create_task(spec["title"], spec["description"])
        client.tasks.update_task(
            task["id"],
            {
                "priority": spec["priority"],
                "output_path": _display_path(spec["artifact"], repo_path),
                "completion_criteria": {
                    "type": "file_exists",
                    "path": str(spec["artifact"]),
                    "min_length_chars": 80,
                },
            },
            agent_name=client.agent_name,
        )
        task_artifacts[task["id"]] = spec["artifact"]

    satya.log(f"Created {len(task_specs)} example tasks.")

    scraped_filename = client.scrape_url(reference_url)
    satya.log(f"Scrape result: {scraped_filename or 'no file saved'}")

    completed_tasks = []
    while True:
        task = satya.pick_task()
        if not task:
            satya.log("No more queued tasks remain in the example backlog.")
            break

        artifact_path = task_artifacts[task["id"]]
        satya.log(f"Working on task: {task['title']}")
        _build_artifact(task, reference_url, scraped_filename, artifact_path)
        client.tasks.update_task(
            task["id"],
            {"output_path": _display_path(artifact_path, repo_path)},
            agent_name=client.agent_name,
        )
        satya.log(f"Wrote task artifact to {_display_path(artifact_path, repo_path)}")
        satya.finish_task()
        completed_tasks.append(task["title"])

    summary = {
        "repo_path": str(repo_path),
        "output_dir": str(output_dir),
        "reference_url": reference_url,
        "scraped_filename": scraped_filename,
        "completed_tasks": completed_tasks,
    }

    summary_path = output_dir / "session_summary.json"
    _write_artifact(summary_path, json.dumps(summary, indent=2))
    satya.log(f"Saved session summary to {_display_path(summary_path, repo_path)}")
    client.flush_logs()
    return summary


def main() -> int:
    args = parse_args()
    summary = run_example(
        repo_path=args.repo_path,
        output_dir=args.output_dir,
        reference_url=args.reference_url,
        agent_name=args.agent_name,
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
