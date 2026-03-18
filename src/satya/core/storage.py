import os
import json
import fcntl
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

SATYA_DIR = "satya_data"
TASKS_DIR = os.path.join(SATYA_DIR, "tasks")
TRUTH_DIR = os.path.join(SATYA_DIR, "truth")
AGENTS_DIR = os.path.join(SATYA_DIR, "agents")
HEARTBEATS_DIR = os.path.join(SATYA_DIR, "heartbeats")

_json_cache = {}
_MAX_CACHE_SIZE = 1000

def _update_cache(filepath: str, data: Any, mtime: float = None) -> None:
    if mtime is None and os.path.exists(filepath):
        mtime = os.path.getmtime(filepath)
    _json_cache[filepath] = {"data": json.dumps(data), "mtime": mtime}
    if len(_json_cache) > _MAX_CACHE_SIZE:
        oldest_key = next(iter(_json_cache))
        _json_cache.pop(oldest_key, None)

def _remove_from_cache(filepath: str) -> None:
    _json_cache.pop(filepath, None)

def ensure_satya_dirs() -> None:
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
                _update_cache(filepath, data)
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
    except FileNotFoundError:
        return {}

    cached_obj = _json_cache.get(filepath)

    if cached_obj is not None and cached_obj.get("mtime") == current_mtime:
        return json.loads(cached_obj["data"])

    lock_filepath = filepath + ".lock"

    try:
        # We need to lock while reading to avoid reading an incomplete file
        # Even with atomic rename, it's safer to acquire a shared lock
        with open(lock_filepath, 'a+') as lock_f:
            fcntl.flock(lock_f, fcntl.LOCK_SH)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    _update_cache(filepath, data, mtime=os.path.getmtime(filepath))
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
        _remove_from_cache(filepath)
        return True
    return False

def delete_truth_file(filename: str) -> bool:
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(TRUTH_DIR, safe_filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False
