import os
import json
import fcntl
import logging
import threading
import copy
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_json_cache = {}
_json_cache_lock = threading.Lock()

ROOT_DIR = "."
SATYA_DIR = "satya_data"
TASKS_DIR = os.path.join(SATYA_DIR, "tasks")
TRUTH_DIR = os.path.join(SATYA_DIR, "truth")
AGENTS_DIR = os.path.join(SATYA_DIR, "agents")
HEARTBEATS_DIR = os.path.join(SATYA_DIR, "heartbeats")

def set_root(path):
    global ROOT_DIR, SATYA_DIR, TASKS_DIR, TRUTH_DIR, AGENTS_DIR
    ROOT_DIR = path
    SATYA_DIR = os.path.join(ROOT_DIR, "satya_data")
    TASKS_DIR = os.path.join(SATYA_DIR, "tasks")
    TRUTH_DIR = os.path.join(SATYA_DIR, "truth")
    AGENTS_DIR = os.path.join(SATYA_DIR, "agents")
    ensure_satya_dirs()

def ensure_satya_dirs():
    os.makedirs(TASKS_DIR, exist_ok=True)
    os.makedirs(TRUTH_DIR, exist_ok=True)
    os.makedirs(AGENTS_DIR, exist_ok=True)
    os.makedirs(HEARTBEATS_DIR, exist_ok=True)

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
                with open(tmp_filepath, 'w') as tmp_f:
                    json.dump(data, tmp_f, indent=4)

                # Atomic rename
                os.rename(tmp_filepath, filepath)

                with _json_cache_lock:
                    _json_cache.pop(filepath, None)

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
    """
    Loads JSON from a file, utilizing an in-memory mtime-based cache to reduce disk I/O.
    """
    if not os.path.exists(filepath):
        return {}

    try:
        # Optimization: Use file modification time (mtime) to detect changes.
        mtime = os.path.getmtime(filepath)
    except OSError:
        return {}

    with _json_cache_lock:
        cache_entry = _json_cache.get(filepath)

    if cache_entry and cache_entry['mtime'] == mtime:
        return copy.deepcopy(cache_entry['data'])

    lock_filepath = filepath + ".lock"

    try:
        # We need to lock while reading to avoid reading an incomplete file
        # Even with atomic rename, it's safer to acquire a shared lock
        with open(lock_filepath, 'a+') as lock_f:
            fcntl.flock(lock_f, fcntl.LOCK_SH)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
            finally:
                fcntl.flock(lock_f, fcntl.LOCK_UN)
    except Exception as e:
        logger.error(f"Error loading JSON from {filepath}: {e}")
        return {}

    # Deepcopy outside the lock to prevent consumers from mutating the cached data
    cache_data = copy.deepcopy(data)

    with _json_cache_lock:
        # Store in cache with the current mtime
        _json_cache[filepath] = {
            'mtime': mtime,
            'data': cache_data
        }
        # Maintain cache size limit using FIFO eviction
        while len(_json_cache) > 1000:
            try:
                del _json_cache[next(iter(_json_cache))]
            except StopIteration:
                break

    return data

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

def save_heartbeat(agent_name: str, heartbeat_data: Dict[str, Any]) -> bool:
    safe_agent_name = os.path.basename(agent_name)
    filepath = os.path.join(HEARTBEATS_DIR, f"{safe_agent_name}.json")
    return save_json(filepath, heartbeat_data)

def get_heartbeats() -> Dict[str, Dict[str, Any]]:
    if not os.path.exists(HEARTBEATS_DIR):
        return {}
    heartbeats = {}
    for f in os.listdir(HEARTBEATS_DIR):
        if f.endswith('.json'):
            agent_name = f[:-5] # remove .json
            heartbeats[agent_name] = load_json(os.path.join(HEARTBEATS_DIR, f))
    return heartbeats

def delete_task_file(task_id: str) -> bool:
    filepath = get_task_path(task_id)
    if os.path.exists(filepath):
        os.remove(filepath)
        with _json_cache_lock:
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
