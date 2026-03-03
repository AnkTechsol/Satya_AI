import os
from datetime import datetime
from ..core import storage, Tasks, Scraper, GitHandler

class SatyaClient:
    def __init__(self, agent_name="default_agent", repo_path="."):
        self.agent_name = agent_name
        self.repo_path = repo_path
        storage.set_root(repo_path)
        self.tasks = Tasks(repo_path)
        self.scraper = Scraper(repo_path)
        self.git = GitHandler(repo_path)

        storage.ensure_satya_dirs()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_filename = f"{self.agent_name}_{self.session_id}.log"
        self.log_path = os.path.join(storage.AGENTS_DIR, self.log_filename)

        try:
            with open(self.log_path, 'a') as f:
                f.write(f"Session started for agent: {self.agent_name} at {datetime.now()}\n")
            self.git.commit_and_push([self.log_path], f"Agent {self.agent_name} started session {self.session_id}")
        except Exception as e:
            print(f"Failed to initialize log file: {e}")

    def log(self, message):
        timestamp = datetime.now().isoformat()
        entry = f"[{timestamp}] {message}\n"
        try:
            with open(self.log_path, 'a') as f:
                f.write(entry)
        except Exception as e:
            print(f"Failed to write log: {e}")

    def flush_logs(self):
        self.git.commit_and_push([self.log_path], f"Update logs for {self.agent_name}")

    def create_task(self, title, description):
        self.log(f"Creating task: {title}")
        return self.tasks.create_task(title, description, assignee=self.agent_name)

    def update_task(self, task_id, status):
        self.log(f"Updating task {task_id} to {status}")
        return self.tasks.update_task_status(task_id, status)

    def scrape_url(self, url):
        self.log(f"Scraping URL: {url}")
        filename = self.scraper.fetch_and_save(url)
        if filename:
            self.log(f"Saved scraped content to {filename}")
            return filename
        else:
            self.log(f"Failed to scrape {url}")
            return None
