import os
import json

ROOT_DIR = "."
SATYA_DIR = "satya_data"
TASKS_DIR = os.path.join(SATYA_DIR, "tasks")
TRUTH_DIR = os.path.join(SATYA_DIR, "truth")
AGENTS_DIR = os.path.join(SATYA_DIR, "agents")

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

def save_json(filepath, data):
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving JSON to {filepath}: {e}")
        return False

def load_json(filepath):
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON from {filepath}: {e}")
        return {}

def save_markdown(filename, content):
    filepath = os.path.join(TRUTH_DIR, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath
    except Exception as e:
        print(f"Error saving markdown to {filepath}: {e}")
        return None

def list_truth_files():
    if not os.path.exists(TRUTH_DIR):
        return []
    return [f for f in os.listdir(TRUTH_DIR) if f.endswith('.md')]

def get_task_path(task_id):
    return os.path.join(TASKS_DIR, f"{task_id}.json")

def list_tasks():
    if not os.path.exists(TASKS_DIR):
        return []
    tasks = []
    for f in os.listdir(TASKS_DIR):
        if f.endswith('.json'):
            tasks.append(load_json(os.path.join(TASKS_DIR, f)))
    return tasks

def delete_task_file(task_id):
    filepath = get_task_path(task_id)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

def delete_truth_file(filename):
    filepath = os.path.join(TRUTH_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False
