class ExportAdapter:
    def export_trace(self, trace_id: str, agent_name: str, event_type: str, payload: dict) -> None:
        pass
    def export_log(self, agent_name: str, message: str, task_id: str = None) -> None:
        pass
