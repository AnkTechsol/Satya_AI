import os
import json

TASKS_DIR = "satya_data/tasks"

status_map = {
    "To Do": "queued",
    "In Progress": "in_progress",
    "Done": "done",
    "Failed": "failed"
}

if os.path.exists(TASKS_DIR):
    for filename in os.listdir(TASKS_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(TASKS_DIR, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)

            old_status = data.get("status")
            if old_status in status_map:
                data["status"] = status_map[old_status]
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=4)
                print(f"Migrated {filename}: {old_status} -> {data['status']}")
