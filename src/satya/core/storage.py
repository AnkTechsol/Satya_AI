import os
import json
import fcntl
import logging
import threading
import copy
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

ROOT_DIR = "."
SATYA_DIR = "satya_data"
TASKS_DIR = os.path.join(SATYA_DIR, "tasks")
TRUTH_DIR = os.path.join(SATYA_DIR, "truth")
AGENTS_DIR = os.path.join(SATYA_DIR, "agents")
HEARTBEATS_DIR = os.path.join(SATYA_DIR, "heartbeats")

# In-memory cache to reduce file I/O overhead
MAX_CACHE_SIZE = 1000
_file_cache = {}
_file_mtime = {}
_cache_lock = threading.Lock()

def _evict_cache_if_needed():
    # Helper to enforce bounded cache size. Must be called with lock held.
    while len(_file_cache) > MAX_CACHE_SIZE:
        try:
            oldest_key = next(iter(_file_cache))
            del _file_cache[oldest_key]
            if oldest_key in _file_mtime:
                del _file_mtime[oldest_key]
        except StopIteration:
            break

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

                # Update cache
                data_copy = copy.deepcopy(data)
                try:
                    current_mtime = os.path.getmtime(filepath)
                    with _cache_lock:
                        _file_cache[filepath] = data_copy
                        _file_mtime[filepath] = current_mtime
                        _evict_cache_if_needed()
                except OSError:
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
        current_mtime = os.path.getmtime(filepath)
        cached_data = None
        with _cache_lock:
            if filepath in _file_cache and _file_mtime.get(filepath) == current_mtime:
                cached_data = _file_cache[filepath]
        if cached_data is not None:
            return copy.deepcopy(cached_data)
    except OSError:
        pass # File might have been deleted

    lock_filepath = filepath + ".lock"

    try:
        # We need to lock while reading to avoid reading an incomplete file
        # Even with atomic rename, it's safer to acquire a shared lock
        with open(lock_filepath, 'a+') as lock_f:
            fcntl.flock(lock_f, fcntl.LOCK_SH)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    data_copy = copy.deepcopy(data)
                    # Re-read mtime in case it changed during load
                    try:
                        current_mtime = os.path.getmtime(filepath)
                        with _cache_lock:
                            _file_mtime[filepath] = current_mtime
                            _file_cache[filepath] = data_copy
                            _evict_cache_if_needed()
                    except OSError:
                        pass
                    return data
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
        with _cache_lock:
            _file_cache.pop(filepath, None)
            _file_mtime.pop(filepath, None)
        return True
    return False

def delete_truth_file(filename: str) -> bool:
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(TRUTH_DIR, safe_filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        # Truth files might not be cached in JSON cache, but we can clean up just in case
        with _cache_lock:
            _file_cache.pop(filepath, None)
            _file_mtime.pop(filepath, None)
        return True
    return False
