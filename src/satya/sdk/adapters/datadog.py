import os
import json
import requests
import uuid
from datetime import datetime, timezone
from .base import ExportAdapter

class DatadogAdapter(ExportAdapter):
    """
    Exports traces and logs to Datadog via their HTTP API.
    """
    def __init__(self, api_key: str = None, site: str = "datadoghq.com"):
        self.api_key = api_key or os.environ.get("DATADOG_API_KEY")
        if not self.api_key:
            raise ValueError("DatadogAdapter requires an api_key or DATADOG_API_KEY environment variable.")

        self.site = site
        self.logs_url = f"https://http-intake.logs.{self.site}/api/v2/logs"
        self.headers = {
            "Content-Type": "application/json",
            "DD-API-KEY": self.api_key
        }

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        data_copy = data.copy()
        payload = {
            "ddsource": "satya_agent",
            "ddtags": f"agent:{agent_name},event_type:{event_type}",
            "hostname": "satya-runtime",
            "message": json.dumps({
                "trace_id": trace_id,
                "agent_name": agent_name,
                "event_type": event_type,
                "data": data_copy
            })
        }
        try:
            requests.post(self.logs_url, json=[payload], headers=self.headers, timeout=5)
        except Exception:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        payload = {
            "ddsource": "satya_agent",
            "ddtags": f"agent:{agent_name}",
            "hostname": "satya-runtime",
            "message": json.dumps({
                "agent_name": agent_name,
                "task_id": task_id,
                "log_message": message
            })
        }
        try:
            requests.post(self.logs_url, json=[payload], headers=self.headers, timeout=5)
        except Exception:
            pass
