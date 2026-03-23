from .client import SatyaClient

_client = None

def init(agent_name="default_agent", repo_path=".", adapters=None):
    global _client
    _client = SatyaClient(agent_name, repo_path, adapters=adapters)
    return _client

def log(message):
    if _client:
        _client.log(message)
    else:
        print(f"[Satya Not Initialized] {message}")

def create_task(title, description):
    if _client:
        return _client.create_task(title, description)
    return None

def update_task(task_id, status):
    if _client:
        return _client.update_task(task_id, status)
    return False

def scrape(url):
    if _client:
        return _client.scrape_url(url)
    return None

def pick_task():
    """Pick the highest priority task and start working on it."""
    if _client:
        return _client.pick_task()
    return None

def finish_task(status="done"):
    """Finish the currently active task."""
    if _client:
        return _client.finish_task(status)
    return False

def poll_chat() -> list[dict]:
    """Poll for real-time manual overrides and commands."""
    if _client:
        return _client.poll_chat()
    return []

def send_heartbeat(status="online"):
    """Sends a heartbeat to indicate the agent is alive."""
    if _client:
        _client.send_heartbeat(status)

def can_do(action: str, task_id: str) -> bool:
    """Check if an action is allowed for a task."""
    if _client:
        return _client.can_do(action, task_id)
    return False

from .adapters import ConsoleAdapter, OTLPAdapter
__all__ = [
    "SatyaClient", "init", "log", "create_task", "update_task", "scrape",
    "pick_task", "finish_task", "poll_chat", "send_heartbeat", "can_do",
    "ConsoleAdapter", "OTLPAdapter"
]
