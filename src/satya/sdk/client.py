import os
from datetime import datetime, timezone
from ..core import storage, Tasks, Scraper, GitHandler
from ..auth import require_agent, get_agent_key_from_env, append_audit_event

class SatyaClient:
    def __init__(self, agent_name="default_agent", repo_path="."):
        self.agent_key = get_agent_key_from_env()
        require_agent(self.agent_key)

        self.agent_name = agent_name
        self.repo_path = repo_path
        self.tasks = Tasks(repo_path)
        self.scraper = Scraper(repo_path)
        self.git = GitHandler(repo_path)

        self.current_task = None
        storage.ensure_satya_dirs()

        # Load adapters based on environment configuration
        self.adapters = []
        if os.environ.get("SATYA_OTLP_ENDPOINT"):
            from ..adapters import OTLPAdapter
            self.adapters.append(OTLPAdapter(os.environ.get("SATYA_OTLP_ENDPOINT")))

        # use daily log file format: agent_name_YYYYMMDD.log
        today_str = datetime.now().strftime("%Y%m%d")
        safe_agent_name = os.path.basename(self.agent_name)
        self.log_filename = f"{safe_agent_name}_{today_str}.log"
        self.log_path = os.path.join(storage.AGENTS_DIR, self.log_filename)

        try:
            with open(self.log_path, 'a') as f:
                f.write(f"Session started for agent: {self.agent_name} at {datetime.now()}\n")
            # We don't need a session ID for the commit message anymore, just the timestamp
            self.git.commit_and_push([self.log_path], f"Agent {self.agent_name} active on {today_str}")
        except Exception as e:
            print(f"Failed to initialize log file: {e}")

    def heartbeat(self, status: str = "online"):
        """Sends a heartbeat to indicate the agent is alive."""
        now = datetime.now(timezone.utc).isoformat() + "Z"
        heartbeat_data = {
            "last_seen": now,
            "status": status,
            "agent_name": self.agent_name,
            "current_task_id": self.current_task["id"] if self.current_task else None
        }
        storage.save_heartbeat(self.agent_name, heartbeat_data)

    def log(self, message):
        timestamp = datetime.now(timezone.utc).isoformat() + "Z"
        entry = f"[{timestamp}] {message}\n"

        # Log to file (always)
        try:
            with open(self.log_path, 'a') as f:
                f.write(entry)
        except Exception as e:
            print(f"Failed to write log: {e}")

        # Log to task context (if active)
        if self.current_task:
            try:
                # Add comment to the task file
                self.tasks.add_comment(self.current_task["id"], message, commit=False, agent_name=self.agent_name)
            except Exception as e:
                print(f"Failed to add comment to task: {e}")

            for adapter in getattr(self, "adapters", []):
                adapter.on_log(self.current_task["id"], message)

    def flush_logs(self):
        self.git.commit_and_push([self.log_path], f"Update logs for {self.agent_name}")

    def can_do(self, action: str, task_id: str) -> bool:
        task = self.tasks.get_task(task_id)
        if not task:
            self.log(f"BLOCKED: Task {task_id} not found")
            return False

        allowed = task.get("allowed_actions", [])
        forbidden = task.get("forbidden_actions", [])

        if action in allowed and action not in forbidden:
            return True

        self.log(f"BLOCKED: '{action}' not permitted for task {task_id}")
        return False

    def create_task(self, title, description, parent_trace_id=None):
        require_agent(self.agent_key)
        # GOVERNANCE RULE 1: Tasks must have meaningful descriptions
        if not description or len(description.strip()) < 10:
            err_msg = "Governance Error: Task description must be at least 10 characters."
            print(err_msg)
            raise ValueError(err_msg)

        self.log(f"Creating task: {title}")
        task = self.tasks.create_task(title, description, assignee=self.agent_name, agent_name=self.agent_name, parent_trace_id=parent_trace_id)
        if task:
            append_audit_event(self.agent_name, task["id"], task["trace_id"], "task_created", f"Created task: {title}")
            for adapter in getattr(self, "adapters", []):
                adapter.on_task_created(task)
        return task

    def update_task(self, task_id, status):
        require_agent(self.agent_key)
        # GOVERNANCE RULE 2: Tasks cannot be marked Done without at least one log entry
        if status == "Done":
            task_data = self.tasks.get_task(task_id)
            if task_data:
                comments = task_data.get("comments", [])
                agent_comments = [c for c in comments if c.get("agent") == self.agent_name]
                if not agent_comments:
                    err_msg = f"Governance Error: Agent '{self.agent_name}' cannot mark task '{task_id}' as Done without logging any progress."
                    print(err_msg)
                    raise ValueError(err_msg)

        self.log(f"Updating task {task_id} to {status}")
        result = self.tasks.update_task_status(task_id, status, agent_name=self.agent_name)
        if result:
            task = self.tasks.get_task(task_id)
            append_audit_event(self.agent_name, task_id, task.get("trace_id", "unknown"), "status_updated", f"Status changed to {status}")
            for adapter in getattr(self, "adapters", []):
                adapter.on_task_updated(task)
        return result

    def scrape_url(self, url):
        require_agent(self.agent_key)
        self.log(f"Scraping URL: {url}")
        filename = self.scraper.fetch_and_save(url)
        if filename:
            self.log(f"Saved scraped content to {filename}")
            return filename
        else:
            self.log(f"Failed to scrape {url}")
            return None

    def pick_task(self):
        """
        Implements the Scrum Master logic:
        1. Check if agent already has a task.
        2. Find highest priority 'To Do' task.
        3. Assign it and mark In Progress.
        """
        if self.current_task:
            self.log(f"Guardrail: You already have a task in progress: {self.current_task['title']}")
            return self.current_task

        all_tasks = self.tasks.list_all()

        # Persistent check: Any task already assigned to me and In Progress?
        # This handles agent restarts.
        for t in all_tasks:
            if t.get("assignee") == self.agent_name and t.get("status") == "In Progress":
                self.log(f"Resuming existing task: {t['title']}")
                self.current_task = t
                return t

        # Guardrail: Check WIP limits (future: implement strict count)

        todo_tasks = [t for t in all_tasks if t.get("status") == "To Do"]

        if not todo_tasks:
            self.log("No tasks in 'To Do' column.")
            return None

        # Prioritization Logic
        priority_map = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}

        # Sort by Priority (asc) then Created At (asc - oldest first)
        todo_tasks.sort(key=lambda t: (
            priority_map.get(t.get("priority", "Medium"), 2),
            t.get("created_at", "")
        ))

        best_task = todo_tasks[0]

        # Assign and Start
        self.log(f"Picking highest priority task: {best_task['title']}")
        self.tasks.update_task(best_task["id"], {
            "status": "In Progress",
            "assignee": self.agent_name
        }, agent_name=self.agent_name)
        # Refresh task data to ensure we have latest state
        self.current_task = self.tasks.get_task(best_task["id"])
        if self.current_task:
            append_audit_event(self.agent_name, self.current_task["id"], self.current_task.get("trace_id", "unknown"), "task_claimed", "Claimed and started task")
        return self.current_task

    def finish_task(self, status="Done"):
        require_agent(self.agent_key)
        """
        Completes the current task context.
        """
        if not self.current_task:
            self.log("Guardrail: No active task to finish.")
            return False

        task_id = self.current_task["id"]

        # Check governance before finishing
        if status == "Done":
            # the task is kept in self.current_task but it might not have the latest comments loaded
            # lets reload it from storage to be sure
            latest_task = self.tasks.get_task(task_id)
            if latest_task:
                comments = latest_task.get("comments", [])
                agent_comments = [c for c in comments if c.get("agent") == self.agent_name]
                if not agent_comments:
                    err_msg = f"Governance Error: Cannot finish task '{self.current_task['title']}' without logging any progress."
                    print(err_msg)
                    raise ValueError(err_msg)

        self.log(f"Finishing task: {self.current_task['title']} -> {status}")

        self.tasks.update_task_status(task_id, status, agent_name=self.agent_name)
        append_audit_event(self.agent_name, task_id, self.current_task.get("trace_id", "unknown"), "task_completed", f"Finished with status {status}")
        self.current_task = None
        self.flush_logs()
        return True

    def use_satya(self, nl_instruction: str, parent_trace_id: str, capabilities: list = None):
        """
        Agent-level helper: when an agent receives instruction 'Use Satya from <repo> to ...',
        call this function to create a subtask, return task id and trace.
        """
        require_agent(self.agent_key)
        description = f"Instruction: {nl_instruction}\nCapabilities: {capabilities or []}"
        task = self.create_task(
            title=f"Subtask: {nl_instruction[:40]}...",
            description=description,
            parent_trace_id=parent_trace_id
        )
        if self.current_task:
            append_audit_event(
                self.agent_name,
                self.current_task["id"],
                self.current_task.get("trace_id", "unknown"),
                "spawned_subtask",
                str({"child_id": task.get("id"), "child_trace": task.get("trace_id")})
            )
        return task
