import os
import json
import datetime
import urllib.request
import urllib.error

class ConsoleAdapter:
    def export_trace(self, trace_id: str, agent_name: str, action: str, payload: dict):
        print(f"[ConsoleAdapter] Trace {trace_id} | Agent: {agent_name} | Action: {action} | Payload: {json.dumps(payload)}")

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        task_str = f" | Task: {task_id}" if task_id else ""
        print(f"[ConsoleAdapter] Log | Agent: {agent_name}{task_str} | Message: {message}")


class OTLPAdapter:
    def __init__(self, endpoint=None):
        self.endpoint = endpoint or os.environ.get("OTLP_ENDPOINT", "http://localhost:4318/v1/traces")

    def export_trace(self, trace_id: str, agent_name: str, action: str, payload: dict):
        timestamp_ns = int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1e9)

        otlp_payload = {
            "resourceSpans": [{
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": f"satya-agent-{agent_name}"}}
                    ]
                },
                "scopeSpans": [{
                    "scope": {"name": "satya.sdk"},
                    "spans": [{
                        "traceId": trace_id.ljust(32, '0')[:32],
                        "spanId": os.urandom(8).hex(),
                        "name": action,
                        "kind": 1,
                        "startTimeUnixNano": timestamp_ns,
                        "endTimeUnixNano": timestamp_ns,
                        "attributes": [
                            {"key": k, "value": {"stringValue": str(v)}} for k, v in payload.items()
                        ]
                    }]
                }]
            }]
        }

        try:
            req = urllib.request.Request(
                self.endpoint,
                data=json.dumps(otlp_payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=2) as response:
                pass
        except Exception:
            # Silently fail if OTLP endpoint is unavailable
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        # We could implement OTLP Logs here in the future
        pass
