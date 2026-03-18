from abc import ABC, abstractmethod

class ExportAdapter(ABC):
    @abstractmethod
    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        """Export a trace event to the destination system."""
        pass

    @abstractmethod
    def export_log(self, agent_name: str, message: str, task_id: str = None):
        """Export a log entry to the destination system."""
        pass
