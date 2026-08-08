import os
import shutil
import time
from satya.core.storage import SATYA_DIR

def archive_old_data(days_old: int = 30, archive_dir: str = None) -> int:
    """
    Archives old JSON tasks and agent logs to prevent unbounded storage growth.
    """
    if archive_dir is None:
        archive_dir = os.path.join(SATYA_DIR, "archive")

    tasks_dir = os.path.join(SATYA_DIR, "tasks")
    agents_dir = os.path.join(SATYA_DIR, "agents")

    os.makedirs(archive_dir, exist_ok=True)
    os.makedirs(os.path.join(archive_dir, "tasks"), exist_ok=True)
    os.makedirs(os.path.join(archive_dir, "agents"), exist_ok=True)

    cutoff_time = time.time() - (days_old * 86400)
    archived_count = 0

    for directory, sub_archive in [(tasks_dir, "tasks"), (agents_dir, "agents")]:
        if not os.path.exists(directory):
            continue
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if not os.path.isfile(filepath):
                continue
            try:
                if os.path.getmtime(filepath) < cutoff_time:
                    dest = os.path.join(archive_dir, sub_archive, filename)
                    shutil.move(filepath, dest)
                    archived_count += 1
            except Exception:
                pass
    return archived_count