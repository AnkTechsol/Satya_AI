import os
import uuid
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

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
    # ⚡ Bolt Optimization: Lock-free atomic writes
    tmp_filepath = f"{filepath}.{uuid.uuid4().hex}.tmp"

    try:
        with open(tmp_filepath, 'w') as tmp_f:
            json.dump(data, tmp_f, indent=4)

        # Atomic rename
        os.rename(tmp_filepath, filepath)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {filepath}: {e}")
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
        # ⚡ Bolt Optimization: Lock-free atomic reads
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {filepath}: {e}")
        return {}

def save_markdown(filename: str, content: str) -> Optional[str]:
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(TRUTH_DIR, safe_filename)
    # ⚡ Bolt Optimization: Lock-free atomic writes for markdown
    tmp_filepath = f"{filepath}.{uuid.uuid4().hex}.tmp"
    try:
        with open(tmp_filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        os.rename(tmp_filepath, filepath)
        return filepath
    except Exception as e:
        logger.error(f"Error saving markdown to {filepath}: {e}")
        if os.path.exists(tmp_filepath):
            try:
                os.remove(tmp_filepath)
            except Exception:
                pass
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
        return True
    return False

def delete_truth_file(filename: str) -> bool:
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(TRUTH_DIR, safe_filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False
