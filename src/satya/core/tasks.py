import uuid
from datetime import datetime, timezone
from . import storage
from .git_handler import GitHandler

STATUS_QUEUED = "queued"
STATUS_IN_PROGRESS = "in_progress"
STATUS_DONE = "done"
STATUS_FAILED = "failed"
PRIORITIES = ["Low", "Medium", "High", "Critical"]

class Tasks:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.git_handler = GitHandler(repo_path)
        storage.ensure_satya_dirs()

    def create_task(self, title, description, assignee=None, priority="Medium", agent_name="System", time_limit_minutes=30, parent_trace_id=None):
        task_id = str(uuid.uuid4())[:8]
        trace_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat() + "Z"

        task = {
            "id": task_id,
            "trace_id": trace_id,
            "parent_trace_id": parent_trace_id,
            "title": title,
            "description": description,
            "status": STATUS_QUEUED,
            "priority": priority,
            "assignee": assignee or "Unassigned",
            "allowed_actions": [],
            "forbidden_actions": [],
            "output_path": "",
            "completion_criteria": {
                "type": "manual"
            },
            "time_limit_minutes": time_limit_minutes,
            "locked_by": None,
            "locked_at": None,
            "created_at": now,
            "updated_at": now,
            "completed_at": None,
            "comments": [],
            "audit_trail": [{
                "timestamp": now,
                "agent": agent_name,
                "action": "Task Created",
                "details": f"Created with status '{STATUS_QUEUED}' and priority '{priority}'"
            }]
        }

        filepath = storage.get_task_path(task_id)
        if storage.save_json(filepath, task):
            self.git_handler.commit_and_push([filepath], f"Task created: {title} ({task_id})")
            return task
        return None

    def update_task_status(self, task_id, new_status, agent_name="System"):
        filepath = storage.get_task_path(task_id)
        task = storage.load_json(filepath)

        if not task:
            return False

        old_status = task.get("status", "Unknown")

        # Validate status transitions
        valid_transitions = {
            STATUS_QUEUED: [STATUS_IN_PROGRESS],
            STATUS_IN_PROGRESS: [STATUS_DONE, STATUS_FAILED],
            STATUS_DONE: [],
            STATUS_FAILED: []
        }

        if old_status in valid_transitions and new_status not in valid_transitions[old_status]:
            raise Exception(f"InvalidStatusTransition: Cannot move from {old_status} to {new_status}")

        if new_status == STATUS_DONE:
            from .completion import CompletionChecker, CompletionCriteriaNotMet, TaskNotFound
            checker = CompletionChecker(self.repo_path)
            try:
                if not checker.check(task):
                    raise CompletionCriteriaNotMet(f"CompletionCriteriaNotMet: Criteria not met for task {task_id}")
            except (CompletionCriteriaNotMet, TaskNotFound) as e:
                raise CompletionCriteriaNotMet(f"CompletionCriteriaNotMet: {str(e)}")

        now = datetime.now(timezone.utc).isoformat() + "Z"
        task["status"] = new_status
        task["updated_at"] = now

        if new_status == STATUS_IN_PROGRESS:
            task["locked_by"] = agent_name
            task["locked_at"] = now
        elif new_status in [STATUS_DONE, STATUS_FAILED]:
            task["completed_at"] = now

        if "audit_trail" not in task:
            task["audit_trail"] = []

        task["audit_trail"].append({
            "timestamp": now,
            "agent": agent_name,
            "action": "Status Changed",
            "details": f"Status changed from '{old_status}' to '{new_status}'"
        })

        if storage.save_json(filepath, task):
            self.git_handler.commit_and_push([filepath], f"Task {task_id} moved to {new_status}")
            return True
        return False

    def lock_task(self, task_id, agent_name):
        filepath = storage.get_task_path(task_id)
        task = storage.load_json(filepath)

        if not task:
            return False

        if task.get("locked_by") is not None and task.get("locked_by") != agent_name:
            raise Exception(f"Task already locked by {task.get('locked_by')}")

        now = datetime.now(timezone.utc).isoformat() + "Z"
        task["locked_by"] = agent_name
        task["locked_at"] = now
        task["updated_at"] = now

        if storage.save_json(filepath, task):
            self.git_handler.commit_and_push([filepath], f"Task {task_id} locked by {agent_name}")
            return True
        return False

    def unlock_task(self, task_id):
        filepath = storage.get_task_path(task_id)
        task = storage.load_json(filepath)

        if not task:
            return False

        now = datetime.now(timezone.utc).isoformat() + "Z"
        task["locked_by"] = None
        task["locked_at"] = None
        task["updated_at"] = now

        if storage.save_json(filepath, task):
            self.git_handler.commit_and_push([filepath], f"Task {task_id} unlocked")
            return True
        return False

    def update_task(self, task_id, updates, agent_name="System"):
        filepath = storage.get_task_path(task_id)
        task = storage.load_json(filepath)

        if not task:
            return False

        now = datetime.now(timezone.utc).isoformat() + "Z"
        changed_fields = []
        for key, value in updates.items():
            if key != "id":
                old_val = task.get(key)
                if old_val != value:
                    changed_fields.append(f"{key}: '{old_val}' -> '{value}'")
                task[key] = value

        task["updated_at"] = now

        if changed_fields:
            if "audit_trail" not in task:
                task["audit_trail"] = []

            task["audit_trail"].append({
                "timestamp": now,
                "agent": agent_name,
                "action": "Task Updated",
                "details": ", ".join(changed_fields)
            })

        if storage.save_json(filepath, task):
            self.git_handler.commit_and_push([filepath], f"Task {task_id} updated")
            return True
        return False

    def delete_task(self, task_id):
        filepath = storage.get_task_path(task_id)
        result = storage.delete_task_file(task_id)
        if result:
            self.git_handler.commit_and_push([filepath], f"Task {task_id} deleted")
        return result

    def list_all(self):
        return storage.list_tasks()

    def get_tasks(self, status=None, assignee=None, tasks_list=None):
        """
        ⚡ Bolt Optimization:
        Accepts an optional `tasks_list` to allow in-memory filtering.
        In zero-database architectures, calling `list_all()` performs N file reads.
        If the caller already has the full task list, passing it here eliminates
        redundant I/O, reducing fetch time significantly.
        """
        all_tasks = tasks_list if tasks_list is not None else self.list_all()
        filtered_tasks = []
        for task in all_tasks:
            if status and task.get("status") != status:
                continue
            if assignee and task.get("assignee") != assignee:
                continue
            filtered_tasks.append(task)
        return filtered_tasks

    def get_task(self, task_id):
        filepath = storage.get_task_path(task_id)
        return storage.load_json(filepath)

    def add_comment(self, task_id, comment, commit=False, agent_name="System"):
        filepath = storage.get_task_path(task_id)
        task = storage.load_json(filepath)

        if not task:
            return False

        if "comments" not in task:
            task["comments"] = []

        now = datetime.now(timezone.utc).isoformat() + "Z"
        entry = {
            "timestamp": now,
            "agent": agent_name,
            "text": comment
        }
        task["comments"].append(entry)
        task["updated_at"] = now

        if "audit_trail" not in task:
            task["audit_trail"] = []

        task["audit_trail"].append({
            "timestamp": now,
            "agent": agent_name,
            "action": "Comment Added",
            "details": f"Comment: '{comment[:50]}...'" if len(comment) > 50 else f"Comment: '{comment}'"
        })

        if storage.save_json(filepath, task):
            if commit:
                self.git_handler.commit_and_push([filepath], f"Comment on task {task_id}")
            return True
        return False

    def get_stats(self, tasks_list=None) -> dict[str, int]:
        """
        ⚡ Bolt Optimization:
        Accepts an optional `tasks_list` to allow in-memory computation.
        In zero-database architectures, calling `list_all()` performs N file reads.
        If the caller already has the full task list, passing it here eliminates
        redundant I/O, reducing stat computation time significantly.
        """
        tasks = tasks_list if tasks_list is not None else self.list_all()
        counts = {
            STATUS_QUEUED: 0,
            STATUS_IN_PROGRESS: 0,
            STATUS_DONE: 0,
            STATUS_FAILED: 0
        }
        for t in tasks:
            status = t.get("status")
            if status in counts:
                counts[status] += 1

        return {
            "total": len(tasks),
            "queued": counts[STATUS_QUEUED],
            "in_progress": counts[STATUS_IN_PROGRESS],
            "done": counts[STATUS_DONE],
            "failed": counts[STATUS_FAILED]
        }
