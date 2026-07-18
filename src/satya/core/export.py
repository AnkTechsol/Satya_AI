import os
import json
import csv
from src.satya.core import storage

def export_tasks_to_jsonl(output_filepath: str) -> int:
    """Exports all tasks from the flat-file storage to a single JSONL file."""
    if not os.path.exists(storage.TASKS_DIR):
        return 0

    parent_dir = os.path.dirname(output_filepath)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    count = 0
    with open(output_filepath, 'w', encoding='utf-8') as outfile:
        for filename in os.listdir(storage.TASKS_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(storage.TASKS_DIR, filename)
                task_data = storage.load_json(filepath)
                if task_data:
                    outfile.write(json.dumps(task_data) + "\n")
                    count += 1
    return count

def export_tasks_to_csv(output_filepath: str) -> int:
    """Exports all tasks from the flat-file storage to a single CSV file."""
    if not os.path.exists(storage.TASKS_DIR):
        return 0

    parent_dir = os.path.dirname(output_filepath)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    count = 0
    tasks = []
    headers = set()

    for filename in os.listdir(storage.TASKS_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(storage.TASKS_DIR, filename)
            task_data = storage.load_json(filepath)
            if task_data:
                tasks.append(task_data)
                headers.update(task_data.keys())
                count += 1

    if not tasks:
        return 0

    # Standardize header order, putting 'id' first if it exists
    header_list = sorted(list(headers))
    if 'id' in header_list:
        header_list.remove('id')
        header_list.insert(0, 'id')

    with open(output_filepath, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=header_list, extrasaction='ignore')
        writer.writeheader()

        # Serialize nested dictionaries/lists to JSON strings for CSV compatibility
        for task in tasks:
            row = {}
            for key, value in task.items():
                if isinstance(value, (dict, list)):
                    row[key] = json.dumps(value)
                else:
                    row[key] = value
            writer.writerow(row)

    return count
