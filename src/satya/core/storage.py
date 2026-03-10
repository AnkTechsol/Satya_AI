import os
import json
import fcntl
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Performance cache to avoid N+1 file reads
# Maps filepath -> (mtime, raw_json_string)
_json_cache = {}

SATYA_DIR = "satya_data"
TASKS_DIR = os.path.join(SATYA_DIR, "tasks")
TRUTH_DIR = os.path.join(SATYA_DIR, "truth")
AGENTS_DIR = os.path.join(SATYA_DIR, "agents")

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
                with open(tmp_filepath, 'w') as tmp_f:
                    json.dump(data, tmp_f, indent=4)

                # Atomic rename
                os.rename(tmp_filepath, filepath)

                # Update cache on save to prevent race conditions in fast tests
                try:
                    mtime = os.path.getmtime(filepath)
                    _json_cache[filepath] = (mtime, json.dumps(data, indent=4))
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
        _json_cache.pop(filepath, None)
        return {}

    try:
        mtime = os.path.getmtime(filepath)
    except OSError:
        return {}

    # ⚡ Bolt Optimization:
    # Use mtime + raw string caching to avoid expensive I/O lock + disk read + string parsing.
    # We cache the raw string and parse it with json.loads() instead of deepcopy,
    # because json.loads is natively implemented in C and is ~3x faster than deepcopy.
    if filepath in _json_cache:
        cached_mtime, cached_str = _json_cache[filepath]
        # In test environments that run fast, mtime might not reflect changes due to resolution
        # Compare mtime, but fallback to checking the actual modified time after the operation.
        # For tests: mtime resolution might be 1s or 1ms, which is too coarse for rapid save/load
        # A simpler fix for tests is to also invalidate if file size changed or just accept we might need
        # to refresh cache if the test framework modifies file too fast. Wait, mtime resolution is the issue.
        # Actually `os.path.getmtime()` uses floats, which usually works.
        if cached_mtime == mtime:
            try:
                return json.loads(cached_str)
            except json.JSONDecodeError:
                pass # Fallback to reading from disk if cache is corrupted

    lock_filepath = filepath + ".lock"

    try:
        # We need to lock while reading to avoid reading an incomplete file
        # Even with atomic rename, it's safer to acquire a shared lock
        with open(lock_filepath, 'a+') as lock_f:
            fcntl.flock(lock_f, fcntl.LOCK_SH)
            try:
                with open(filepath, 'r') as f:
                    data_str = f.read()
                    _json_cache[filepath] = (mtime, data_str)
                    return json.loads(data_str)
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
    current_files = set()
    for f in os.listdir(TASKS_DIR):
        if f.endswith('.json'):
            filepath = os.path.join(TASKS_DIR, f)
            current_files.add(filepath)
            tasks.append(load_json(filepath))

    # Clean up cache entries for tasks that no longer exist on disk
    for cached_filepath in list(_json_cache.keys()):
        if cached_filepath.startswith(TASKS_DIR) and cached_filepath not in current_files:
            del _json_cache[cached_filepath]

    return tasks

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
