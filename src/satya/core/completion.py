import os
import subprocess
import shlex
from .tasks import Tasks, STATUS_DONE

class CompletionCriteriaNotMet(Exception):
    pass

class TaskNotFound(Exception):
    pass

class CompletionChecker:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.tasks = Tasks(repo_path)

    def check(self, task: dict) -> bool:
        criteria = task.get("completion_criteria", {})
        if not criteria:
            return False

        c_type = criteria.get("type")

        if c_type == "file_exists":
            path = criteria.get("path")
            min_length = criteria.get("min_length_chars", 0)

            if not path or not os.path.exists(path):
                raise CompletionCriteriaNotMet(f"File {path} does not exist.")

            file_size = os.path.getsize(path)
            if file_size < min_length:
                raise CompletionCriteriaNotMet(f"File {path} is too small ({file_size} bytes < {min_length} bytes required).")

            return True

        elif c_type == "tests_pass":
            test_command = criteria.get("test_command")
            required_code = criteria.get("required_exit_code", 0)

            if not test_command:
                raise CompletionCriteriaNotMet("No test_command specified.")

            try:
                # Security Fix: Avoid shell=True to prevent arbitrary command injection.
                # By using shell=False and shlex.split, we ensure that operators like &&, |, ;
                # are not interpreted by a shell. This is a breaking change for tasks that
                # rely on shell features, but it is necessary for security in an environment
                # where agents can programmatically set these commands.
                args = shlex.split(test_command)
                result = subprocess.run(args, shell=False, capture_output=True, text=True)
                if result.returncode != required_code:
                    raise CompletionCriteriaNotMet(f"Test command failed with exit code {result.returncode} (expected {required_code}).\nOutput: {result.stdout}\nError: {result.stderr}")
                return True
            except Exception as e:
                raise CompletionCriteriaNotMet(f"Error running test command: {str(e)}")

        elif c_type == "all_subtasks_done":
            subtask_ids = criteria.get("subtask_ids", [])
            if not subtask_ids:
                return False

            for subtask_id in subtask_ids:
                subtask = self.tasks.get_task(subtask_id)
                if not subtask:
                    raise TaskNotFound(f"Subtask {subtask_id} not found.")
                if subtask.get("status") != STATUS_DONE:
                    raise CompletionCriteriaNotMet(f"Subtask {subtask_id} is not done.")
            return True

        elif c_type == "manual":
            return False

        else:
            raise CompletionCriteriaNotMet(f"Unknown completion criteria type: {c_type}")
