import csv
import json
import os
from .base import ExportAdapter

class FileExportAdapter(ExportAdapter):
    def __init__(self, export_dir: str = "satya_data/exports"):
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        csv_path = os.path.join(self.export_dir, "traces.csv")
        jsonl_path = os.path.join(self.export_dir, "traces.jsonl")

        file_exists = os.path.isfile(csv_path)
        with open(csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['trace_id', 'agent_name', 'event_type', 'data'])
            writer.writerow([trace_id, agent_name, event_type, json.dumps(data)])

        with open(jsonl_path, 'a') as f:
            f.write(json.dumps({'trace_id': trace_id, 'agent_name': agent_name, 'event_type': event_type, 'data': data}) + '\n')

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        csv_path = os.path.join(self.export_dir, "logs.csv")
        jsonl_path = os.path.join(self.export_dir, "logs.jsonl")

        file_exists = os.path.isfile(csv_path)
        with open(csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['agent_name', 'message', 'task_id'])
            writer.writerow([agent_name, message, task_id])

        with open(jsonl_path, 'a') as f:
            f.write(json.dumps({'agent_name': agent_name, 'message': message, 'task_id': task_id}) + '\n')
