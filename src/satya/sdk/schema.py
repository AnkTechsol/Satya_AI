from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
import json

@dataclass
class TraceEvent:
    trace_id: str
    agent_name: str
    event_type: str
    data: Dict[str, Any]

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict())

@dataclass
class LogEvent:
    agent_name: str
    message: str
    task_id: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict())
