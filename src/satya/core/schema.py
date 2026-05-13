import dataclasses
from typing import Dict, Any, Optional
import datetime

@dataclasses.dataclass
class TraceEvent:
    trace_id: str
    event_type: str
    agent_name: str
    data: Dict[str, Any]
    timestamp: str = dataclasses.field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"))

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)
