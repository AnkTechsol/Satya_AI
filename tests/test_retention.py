import os
import time
from unittest.mock import patch
import pytest
from satya.core.retention import archive_old_data

def test_archive_old_data(tmp_path):
    satya_dir = tmp_path / "satya_data"
    tasks_dir = satya_dir / "tasks"
    agents_dir = satya_dir / "agents"
    archive_dir = satya_dir / "archive"

    tasks_dir.mkdir(parents=True)
    agents_dir.mkdir(parents=True)

    old_task = tasks_dir / "old_task.json"
    old_task.write_text('{}')
    new_task = tasks_dir / "new_task.json"
    new_task.write_text('{}')

    old_agent = agents_dir / "old_agent.log"
    old_agent.write_text('log')

    cutoff = time.time() - (30 * 86400)
    os.utime(old_task, (cutoff - 1000, cutoff - 1000))
    os.utime(new_task, (time.time(), time.time()))
    os.utime(old_agent, (cutoff - 1000, cutoff - 1000))

    with patch("satya.core.retention.SATYA_DIR", str(satya_dir)):
        count = archive_old_data(days_old=30, archive_dir=str(archive_dir))

    assert count == 2
    assert not old_task.exists()
    assert not old_agent.exists()
    assert new_task.exists()
    assert (archive_dir / "tasks" / "old_task.json").exists()
    assert (archive_dir / "agents" / "old_agent.log").exists()