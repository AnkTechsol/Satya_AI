import uuid
from datetime import datetime
from . import storage
from .git_handler import GitHandler

STATUS_TODO = "To Do"
STATUS_IN_PROGRESS = "In Progress"
STATUS_DONE = "Done"
PRIORITIES = ["Low", "Medium", "High", "Critical"]

class Tasks:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.git_handler = GitHandler(repo_path)
        storage.ensure_satya_dirs()

    def create_task(self, title, description, assignee=None, priority="Medium", agent_name="System"):
        task_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()

        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "status": STATUS_TODO,
            "priority": priority,
            "assignee": assignee or "Unassigned",
            "created_at": now,
            "updated_at": now,
            "comments": [],
            "audit_trail": [{
                "timestamp": now,
                "agent": agent_name,
                "action": "Task Created",
                "details": f"Created with status '{STATUS_TODO}' and priority '{priority}'"
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
        now = datetime.now().isoformat()
        task["status"] = new_status
        task["updated_at"] = now

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

    def update_task(self, task_id, updates, agent_name="System"):
        filepath = storage.get_task_path(task_id)
        task = storage.load_json(filepath)

        if not task:
            return False

        now = datetime.now().isoformat()
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

        now = datetime.now().isoformat()
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

    def get_stats(self):
        tasks = self.list_all()
        total = len(tasks)
        todo = sum(1 for t in tasks if t.get("status") == STATUS_TODO)
        in_progress = sum(1 for t in tasks if t.get("status") == STATUS_IN_PROGRESS)
        done = sum(1 for t in tasks if t.get("status") == STATUS_DONE)
        return {"total": total, "todo": todo, "in_progress": in_progress, "done": done}
