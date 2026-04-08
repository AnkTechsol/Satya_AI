import os
import json
import fcntl
import logging
import threading
import copy
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# In-memory heartbeat cache to reduce I/O overhead
_heartbeat_cache = {}
_heartbeat_mtimes = {}
_heartbeat_lock = threading.Lock()

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

    lock_filepath = filepath + ".lock"

    try:
        # We need to lock while reading to avoid reading an incomplete file
        # Even with atomic rename, it's safer to acquire a shared lock
        with open(lock_filepath, 'a+') as lock_f:
            fcntl.flock(lock_f, fcntl.LOCK_SH)
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
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

    success = save_json(filepath, heartbeat_data)

    if success:
        # ⚡ Bolt Optimization:
        # To avoid blocking other threads during deepcopy, we copy outside the lock.
        # We also use the atomic mtime directly from the written file to avoid a
        # Time-of-Check to Time-of-Use (TOCTOU) race condition.
        try:
            new_mtime = os.path.getmtime(filepath)
            data_copy = copy.deepcopy(heartbeat_data)
            with _heartbeat_lock:
                _heartbeat_mtimes[safe_agent_name] = new_mtime
                _heartbeat_cache[safe_agent_name] = data_copy
        except OSError:
            # Invalidate if getmtime fails for any reason
            with _heartbeat_lock:
                _heartbeat_cache.pop(safe_agent_name, None)
                _heartbeat_mtimes.pop(safe_agent_name, None)

    return success

def get_heartbeats() -> Dict[str, Dict[str, Any]]:
    """
    ⚡ Bolt Optimization:
    Implements a thread-safe, mtime-based in-memory cache for heartbeats.
    Significantly reduces N+1 file reads when polled rapidly by orchestrators or UI.
    """
    if not os.path.exists(HEARTBEATS_DIR):
        return {}

    current_files = set()

    for f in os.listdir(HEARTBEATS_DIR):
        if not f.endswith('.json'):
            continue

        agent_name = f[:-5]
        filepath = os.path.join(HEARTBEATS_DIR, f)
        current_files.add(agent_name)

        try:
            current_mtime = os.path.getmtime(filepath)
        except OSError:
            continue

        with _heartbeat_lock:
            cached_mtime = _heartbeat_mtimes.get(agent_name)
            needs_update = cached_mtime is None or current_mtime > cached_mtime

        if needs_update:
            data = load_json(filepath)
            # ⚡ Bolt Optimization:
            # Execute the expensive deepcopy outside the lock block to minimize contention.
            data_copy = copy.deepcopy(data)
            with _heartbeat_lock:
                # Store a deepcopy to prevent caller mutations affecting the cache
                _heartbeat_cache[agent_name] = data_copy
                _heartbeat_mtimes[agent_name] = current_mtime

    with _heartbeat_lock:
        # Cleanup deleted heartbeats
        stale_agents = set(_heartbeat_cache.keys()) - current_files
        for agent in stale_agents:
            _heartbeat_cache.pop(agent, None)
            _heartbeat_mtimes.pop(agent, None)

        # ⚡ Bolt Optimization:
        # We hold the lock to get a reference, but we execute the expensive
        # deepcopy operation *outside* the lock block to reduce contention.
        cache_ref = _heartbeat_cache.copy()

    return copy.deepcopy(cache_ref)

def delete_task_file(task_id: str) -> bool:
    filepath = get_task_path(task_id)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

def delete_truth_file(filename: str) -> bool:
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(TRUTH_DIR, safe_filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False
