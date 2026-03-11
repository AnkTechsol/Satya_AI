import os
import shutil
import pytest
from src.satya.core.tasks import Tasks, STATUS_IN_PROGRESS, STATUS_DONE
from src.satya.core.completion import CompletionChecker

@pytest.fixture
def temp_tasks_and_checker():
    repo_path = "test_repo"
    os.makedirs(repo_path, exist_ok=True)

    import src.satya.core.storage as storage
    old_dir = storage.SATYA_DIR
    storage.SATYA_DIR = os.path.join(repo_path, "satya_data")
    storage.TASKS_DIR = os.path.join(storage.SATYA_DIR, "tasks")
    storage.TRUTH_DIR = os.path.join(storage.SATYA_DIR, "truth")
    storage.AGENTS_DIR = os.path.join(storage.SATYA_DIR, "agents")

    tasks = Tasks(repo_path)
    checker = CompletionChecker(repo_path)
    # mock tasks instance inside checker to point to the temp tasks
    checker.tasks = tasks
    yield tasks, checker, repo_path

    shutil.rmtree(repo_path)
    storage.SATYA_DIR = old_dir
    storage.TASKS_DIR = os.path.join(storage.SATYA_DIR, "tasks")
    storage.TRUTH_DIR = os.path.join(storage.SATYA_DIR, "truth")
    storage.AGENTS_DIR = os.path.join(storage.SATYA_DIR, "agents")

def test_file_exists_passes_when_file_present(temp_tasks_and_checker):
    tasks, checker, repo_path = temp_tasks_and_checker

    test_file_path = os.path.join(repo_path, "test.md")
    with open(test_file_path, "w") as f:
        f.write("A" * 600)  # 600 chars

    task = tasks.create_task("Test", "Desc")
    task_id = task["id"]

    tasks.update_task(task_id, {
        "completion_criteria": {
            "type": "file_exists",
            "path": test_file_path,
            "min_length_chars": 500
        }
    })

    tasks.update_task_status(task_id, STATUS_IN_PROGRESS)

    # Check returns True
    task_data = tasks.get_task(task_id)
    assert checker.check(task_data) == True

    # Can mark as done
    assert tasks.update_task_status(task_id, STATUS_DONE) == True

def test_file_exists_fails_when_file_missing(temp_tasks_and_checker):
    tasks, checker, repo_path = temp_tasks_and_checker

    test_file_path = os.path.join(repo_path, "missing.md")

    task = tasks.create_task("Test", "Desc")
    task_id = task["id"]

    tasks.update_task(task_id, {
        "completion_criteria": {
            "type": "file_exists",
            "path": test_file_path,
            "min_length_chars": 500
        }
    })

    tasks.update_task_status(task_id, STATUS_IN_PROGRESS)

    with pytest.raises(Exception, match="CompletionCriteriaNotMet.*does not exist"):
        tasks.update_task_status(task_id, STATUS_DONE)

def test_file_exists_fails_when_too_short(temp_tasks_and_checker):
    tasks, checker, repo_path = temp_tasks_and_checker

    test_file_path = os.path.join(repo_path, "test.md")
    with open(test_file_path, "w") as f:
        f.write("A" * 100)  # 100 chars, but needs 500

    task = tasks.create_task("Test", "Desc")
    task_id = task["id"]

    tasks.update_task(task_id, {
        "completion_criteria": {
            "type": "file_exists",
            "path": test_file_path,
            "min_length_chars": 500
        }
    })

    tasks.update_task_status(task_id, STATUS_IN_PROGRESS)

    with pytest.raises(Exception, match="CompletionCriteriaNotMet.*too small"):
        tasks.update_task_status(task_id, STATUS_DONE)

def test_all_subtasks_done_blocks_until_children_complete(temp_tasks_and_checker):
    tasks, checker, repo_path = temp_tasks_and_checker

    # Create child 1 and 2
    child1 = tasks.create_task("Child1", "Desc")
    child2 = tasks.create_task("Child2", "Desc")

    # Set child to manual completion (easiest way to bypass check since manual is False)
    # Wait, manual always returns False so we can't mark it as done!
    # Let's set it to file_exists and create the file so we CAN mark them done
    test_file = os.path.join(repo_path, "dummy.txt")
    with open(test_file, "w") as f: f.write("!")

    for cid in [child1["id"], child2["id"]]:
        tasks.update_task(cid, {
            "completion_criteria": {
                "type": "file_exists",
                "path": test_file,
                "min_length_chars": 1
            }
        })

    parent = tasks.create_task("Parent", "Desc")
    tasks.update_task(parent["id"], {
        "completion_criteria": {
            "type": "all_subtasks_done",
            "subtask_ids": [child1["id"], child2["id"]]
        }
    })

    tasks.update_task_status(parent["id"], STATUS_IN_PROGRESS)
    tasks.update_task_status(child1["id"], STATUS_IN_PROGRESS)
    tasks.update_task_status(child2["id"], STATUS_IN_PROGRESS)

    # Both not done -> parent fails
    with pytest.raises(Exception, match="CompletionCriteriaNotMet.*is not done"):
        tasks.update_task_status(parent["id"], STATUS_DONE)

    # One done -> parent fails
    tasks.update_task_status(child1["id"], STATUS_DONE)
    with pytest.raises(Exception, match="CompletionCriteriaNotMet.*is not done"):
        tasks.update_task_status(parent["id"], STATUS_DONE)

    # Both done -> parent passes
    tasks.update_task_status(child2["id"], STATUS_DONE)
    assert tasks.update_task_status(parent["id"], STATUS_DONE) == True

def test_manual_type_always_returns_false(temp_tasks_and_checker):
    tasks, checker, repo_path = temp_tasks_and_checker

    task = tasks.create_task("Test", "Desc")
    task_id = task["id"]

    # Default is manual
    tasks.update_task_status(task_id, STATUS_IN_PROGRESS)

    with pytest.raises(Exception, match="CompletionCriteriaNotMet"):
        tasks.update_task_status(task_id, STATUS_DONE)

def test_tests_pass_prevents_command_injection(temp_tasks_and_checker):
    tasks, checker, repo_path = temp_tasks_and_checker

    exploit_file = os.path.join(repo_path, "exploit_test.txt")
    if os.path.exists(exploit_file):
        os.remove(exploit_file)

    task = tasks.create_task("Exploit Task", "Testing command injection")
    task_id = task["id"]

    # Malicious command that uses shell features (redirection)
    # With shell=False and shlex.split, this will fail or execute 'echo' with the rest as arguments
    malicious_cmd = f"echo vulnerable > {exploit_file}"

    tasks.update_task(task_id, {
        "completion_criteria": {
            "type": "tests_pass",
            "test_command": malicious_cmd,
            "required_exit_code": 0
        }
    })

    tasks.update_task_status(task_id, STATUS_IN_PROGRESS)

    # Triggering the check should not create the exploit file
    try:
        tasks.update_task_status(task_id, STATUS_DONE)
    except Exception:
        pass

    assert not os.path.exists(exploit_file), "Vulnerability: exploit file was created!"
