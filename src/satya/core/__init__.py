from .storage import *
from .git_handler import GitHandler
from .tasks import Tasks
from .scraper import Scraper

def get_stale_tasks():
    from .watchdog import WatchdogChecker
    checker = WatchdogChecker()
    return checker.scan()
