import os
import shutil
import pytest
from src.satya.core.tasks import Tasks, STATUS_QUEUED, STATUS_IN_PROGRESS, STATUS_DONE, STATUS_FAILED

@pytest.fixture
def temp_tasks():
    repo_path = "test_repo"
    os.makedirs(repo_path, exist_ok=True)

    # Also set the SATYA_DIR globally for tests to mock storage
    import src.satya.core.storage as storage
    old_dir = storage.SATYA_DIR
    storage.SATYA_DIR = os.path.join(repo_path, "satya_data")
    storage.TASKS_DIR = os.path.join(storage.SATYA_DIR, "tasks")
    storage.TRUTH_DIR = os.path.join(storage.SATYA_DIR, "truth")
    storage.AGENTS_DIR = os.path.join(storage.SATYA_DIR, "agents")

    tasks = Tasks(repo_path)
    yield tasks

    storage._json_cache.clear()

    shutil.rmtree(repo_path)
    # Restore old storage
    storage.SATYA_DIR = old_dir
    storage.TASKS_DIR = os.path.join(storage.SATYA_DIR, "tasks")
    storage.TRUTH_DIR = os.path.join(storage.SATYA_DIR, "truth")
    storage.AGENTS_DIR = os.path.join(storage.SATYA_DIR, "agents")

def test_valid_transitions(temp_tasks):
    task = temp_tasks.create_task("Test", "Description")
    task_id = task["id"]

    # Update to a completion criteria that will pass, so we can transition to done
    temp_tasks.update_task(task_id, {
        "completion_criteria": {
            "type": "file_exists",
            "path": __file__,
            "min_length_chars": 10
        }
    })

    # queued -> in_progress
    assert temp_tasks.update_task_status(task_id, STATUS_IN_PROGRESS, "agent") == True
    updated_task = temp_tasks.get_task(task_id)
    assert updated_task["status"] == STATUS_IN_PROGRESS
    assert updated_task["locked_by"] == "agent"
    assert updated_task["locked_at"] is not None

    # in_progress -> done
    assert temp_tasks.update_task_status(task_id, STATUS_DONE, "agent") == True
    updated_task = temp_tasks.get_task(task_id)
    assert updated_task["status"] == STATUS_DONE
    assert updated_task["completed_at"] is not None

def test_invalid_transitions_raise_exception(temp_tasks):
    task = temp_tasks.create_task("Test", "Description")
    task_id = task["id"]

    temp_tasks.update_task(task_id, {
        "completion_criteria": {
            "type": "file_exists",
            "path": __file__,
            "min_length_chars": 10
        }
    })

    # queued -> done is invalid
    with pytest.raises(Exception, match="InvalidStatusTransition"):
        temp_tasks.update_task_status(task_id, STATUS_DONE, "agent")

    # Valid transition to test more
    temp_tasks.update_task_status(task_id, STATUS_IN_PROGRESS, "agent")
    temp_tasks.update_task_status(task_id, STATUS_DONE, "agent")

    # done -> in_progress is invalid
    with pytest.raises(Exception, match="InvalidStatusTransition"):
        temp_tasks.update_task_status(task_id, STATUS_IN_PROGRESS, "agent")

def test_lock_prevents_double_pickup(temp_tasks):
    task = temp_tasks.create_task("Test", "Description")
    task_id = task["id"]

    assert temp_tasks.lock_task(task_id, "agent1") == True

    with pytest.raises(Exception, match="Task already locked by agent1"):
        temp_tasks.lock_task(task_id, "agent2")

    assert temp_tasks.unlock_task(task_id) == True
    assert temp_tasks.lock_task(task_id, "agent2") == True

def test_completed_at_set_on_done(temp_tasks):
    task = temp_tasks.create_task("Test", "Description")
    task_id = task["id"]

    temp_tasks.update_task(task_id, {
        "completion_criteria": {
            "type": "file_exists",
            "path": __file__,
            "min_length_chars": 10
        }
    })

    temp_tasks.update_task_status(task_id, STATUS_IN_PROGRESS, "agent")
    task = temp_tasks.get_task(task_id)
    assert task["completed_at"] is None

    temp_tasks.update_task_status(task_id, STATUS_DONE, "agent")
    task = temp_tasks.get_task(task_id)
    assert task["completed_at"] is not None
