class ExportAdapter:
    """Base adapter for exporting Satya events."""
    def on_task_created(self, task: dict):
        pass

    def on_task_updated(self, task: dict):
        pass

    def on_log(self, task_id: str, message: str):
        pass
