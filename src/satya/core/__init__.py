from .storage import *
from .git_handler import GitHandler
from .tasks import Tasks
from .scraper import Scraper
from .project_manager import AIOrchestrator
from .pulse import compute_agent_health, compute_velocity_matrix, detect_cascade_failures, snapshot_pulse
from .goal_guardian import GoalGuardian, save_context_snapshot, get_latest_context_snapshot

__all__ = [
    'GitHandler',
    'Tasks',
    'Scraper',
    'AIOrchestrator',
    'get_stale_tasks',
    'compute_agent_health',
    'compute_velocity_matrix',
    'detect_cascade_failures',
    'snapshot_pulse',
    'GoalGuardian',
    'save_context_snapshot',
    'get_latest_context_snapshot'
]

def get_stale_tasks(tasks_list=None):
    from .watchdog import WatchdogChecker
    checker = WatchdogChecker()
    return checker.scan(tasks_list)
