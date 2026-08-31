import queue
import threading
import atexit
from .base import ExportAdapter
from src.satya.core.webhooks import dispatch

class WebhookAdapter(ExportAdapter):
    def __init__(self):
        self.queue = queue.Queue(maxsize=1000)
        self.worker = threading.Thread(target=self._run, daemon=True)
        self.worker.start()
        atexit.register(self.shutdown)

    def _run(self):
        while True:
            item = self.queue.get()
            if item is None:
                self.queue.task_done()
                break

            try:
                dispatch(item["event"], item["payload"])
            except Exception:
                pass
            finally:
                self.queue.task_done()

    def export_trace(self, trace_id, agent_name, event_type, data):
        payload = {"trace_id": trace_id, "agent": agent_name, "type": event_type, "data": data}
        try:
            self.queue.put_nowait({"event": "trace", "payload": payload})
        except queue.Full:
            pass

    def export_log(self, agent_name, message, task_id=None):
        payload = {"agent": agent_name, "message": message, "task_id": task_id}
        try:
            self.queue.put_nowait({"event": "log", "payload": payload})
        except queue.Full:
            pass

    def shutdown(self):
        if not self.worker.is_alive():
            return

        try:
            self.queue.put_nowait(None)
        except queue.Full:
            try:
                while True:
                    self.queue.get_nowait()
                    self.queue.task_done()
            except queue.Empty:
                pass
            self.queue.put_nowait(None)

        self.queue.join()
        self.worker.join(timeout=2)
