import os
import json
import fcntl
import logging
import collections
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

SATYA_DIR = "satya_data"
TASKS_DIR = os.path.join(SATYA_DIR, "tasks")
TRUTH_DIR = os.path.join(SATYA_DIR, "truth")
AGENTS_DIR = os.path.join(SATYA_DIR, "agents")

# ⚡ Bolt Optimization:
# LRU cache to prevent severe N+1 I/O bottlenecks when listing tasks.
# We cache the raw JSON string instead of parsed dicts because:
# 1. Native C JSON parsing is much faster than `copy.deepcopy()`
# 2. It inherently protects against accidental in-memory mutations
_json_cache_max_size = 1000
_json_cache = collections.OrderedDict()

def _update_cache(filepath: str, raw_string: str, mtime: float):
    """Safely updates the bounded LRU cache."""
    _json_cache.pop(filepath, None)
    _json_cache[filepath] = {"mtime": mtime, "raw_string": raw_string}
    if len(_json_cache) > _json_cache_max_size:
        _json_cache.popitem(last=False)

def ensure_satya_dirs() -> None:
    os.makedirs(TASKS_DIR, exist_ok=True)
    os.makedirs(TRUTH_DIR, exist_ok=True)
    os.makedirs(AGENTS_DIR, exist_ok=True)

def save_json(filepath: str, data: Any) -> bool:
    tmp_filepath = filepath + ".tmp"
    lock_filepath = filepath + ".lock"

    try:
        # Create a separate lock file
        with open(lock_filepath, 'w') as lock_f:
            # Acquire exclusive lock
            fcntl.flock(lock_f, fcntl.LOCK_EX)
            try:
                # Write to temp file
                raw_string = json.dumps(data, indent=4)
                with open(tmp_filepath, 'w') as tmp_f:
                    tmp_f.write(raw_string)

                # Atomic rename
                os.rename(tmp_filepath, filepath)

                # ⚡ Bolt Optimization:
                # Manually update the cache after save to avoid race conditions.
                # Test framework execution speeds can exceed `mtime` resolution.
                try:
                    mtime = os.path.getmtime(filepath)
                    _update_cache(filepath, raw_string, mtime)
                except Exception:
                    pass

                return True
            finally:
                # Release lock
                fcntl.flock(lock_f, fcntl.LOCK_UN)
    except Exception as e:
        logger.error(f"Error saving JSON to {filepath}: {e}")
        # Clean up tmp file if rename failed
        if os.path.exists(tmp_filepath):
            try:
                os.remove(tmp_filepath)
            except Exception:
                pass
        return False

def load_json(filepath: str) -> Dict[str, Any]:
    if not os.path.exists(filepath):
        return {}

    try:
        mtime = os.path.getmtime(filepath)
    except Exception:
        return {}

    cached = _json_cache.get(filepath)
    # Important: >= instead of == for mtime because manual cache updates
    # during save_json might happen in the same mtime window as a subsequent read.
    if cached and cached["mtime"] >= mtime:
        try:
            return json.loads(cached["raw_string"])
        except Exception:
            pass

    lock_filepath = filepath + ".lock"

    try:
        # We need to lock while reading to avoid reading an incomplete file
        # Even with atomic rename, it's safer to acquire a shared lock
        with open(lock_filepath, 'a+') as lock_f:
            fcntl.flock(lock_f, fcntl.LOCK_SH)
            try:
                with open(filepath, 'r') as f:
                    raw_string = f.read()
                    _update_cache(filepath, raw_string, mtime)
                    return json.loads(raw_string)
            finally:
                fcntl.flock(lock_f, fcntl.LOCK_UN)
    except Exception as e:
        logger.error(f"Error loading JSON from {filepath}: {e}")
        return {}

def save_markdown(filename: str, content: str) -> Optional[str]:
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(TRUTH_DIR, safe_filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath
    except Exception as e:
        logger.error(f"Error saving markdown to {filepath}: {e}")
        return None

def list_truth_files() -> List[str]:
    if not os.path.exists(TRUTH_DIR):
        return []
    return [f for f in os.listdir(TRUTH_DIR) if f.endswith('.md')]

def get_task_path(task_id: str) -> str:
    safe_task_id = os.path.basename(task_id)
    return os.path.join(TASKS_DIR, f"{safe_task_id}.json")

def list_tasks() -> List[Dict[str, Any]]:
    if not os.path.exists(TASKS_DIR):
        return []
    tasks = []
    for f in os.listdir(TASKS_DIR):
        if f.endswith('.json'):
            tasks.append(load_json(os.path.join(TASKS_DIR, f)))
    return tasks

def delete_task_file(task_id: str) -> bool:
    filepath = get_task_path(task_id)
    if os.path.exists(filepath):
        os.remove(filepath)
        _json_cache.pop(filepath, None)
        return True
    return False

def delete_truth_file(filename: str) -> bool:
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(TRUTH_DIR, safe_filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False
