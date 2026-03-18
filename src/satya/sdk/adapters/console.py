from .base import ExportAdapter
import datetime
import json

class ConsoleAdapter(ExportAdapter):
    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        print(f"[ConsoleAdapter] Trace {trace_id} | Agent: {agent_name} | Event: {event_type} | Data: {json.dumps(data)}")

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        task_str = f" | Task: {task_id}" if task_id else ""
        print(f"[ConsoleAdapter] Log | Agent: {agent_name}{task_str} | Message: {message}")
