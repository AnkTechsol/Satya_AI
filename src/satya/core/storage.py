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

# ⚡ Bolt Optimization: In-memory JSON Cache
# To prevent excessive disk I/O when fetching tasks, we cache the raw JSON string.
# We parse it with `json.loads(cached_str)` on demand instead of `copy.deepcopy()`,
# as native C JSON parsing is significantly faster.
# Format: { filepath: {"mtime": float, "raw": str} }
_json_cache = {}

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
                raw_json = json.dumps(data, indent=4)
                with open(tmp_filepath, 'w') as tmp_f:
                    tmp_f.write(raw_json)

                # Atomic rename
                os.rename(tmp_filepath, filepath)

                # Update cache immediately to prevent mtime race conditions in fast test suites
                try:
                    mtime = os.path.getmtime(filepath)
                    _json_cache[filepath] = {"mtime": mtime, "raw": raw_json}
                except Exception as e:
                    logger.warning(f"Failed to update cache for {filepath}: {e}")

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
        # Clean up cache if file was deleted externally
        if filepath in _json_cache:
            del _json_cache[filepath]
        return {}

    try:
        current_mtime = os.path.getmtime(filepath)
    except Exception:
        current_mtime = 0

    # ⚡ Bolt Optimization: Return parsed cached string if file hasn't changed
    cached_entry = _json_cache.get(filepath)
    if cached_entry and cached_entry["mtime"] >= current_mtime:
        try:
            return json.loads(cached_entry["raw"])
        except json.JSONDecodeError:
            pass # Fallback to reading file if cache is somehow corrupted

    lock_filepath = filepath + ".lock"

    try:
        # We need to lock while reading to avoid reading an incomplete file
        # Even with atomic rename, it's safer to acquire a shared lock
        with open(lock_filepath, 'a+') as lock_f:
            fcntl.flock(lock_f, fcntl.LOCK_SH)
            try:
                with open(filepath, 'r') as f:
                    raw_json = f.read()

                # Update cache
                _json_cache[filepath] = {"mtime": current_mtime, "raw": raw_json}

                return json.loads(raw_json)
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
        # ⚡ Bolt Optimization: Remove from cache
        if filepath in _json_cache:
            del _json_cache[filepath]
        return True
    return False

def delete_truth_file(filename: str) -> bool:
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(TRUTH_DIR, safe_filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False
