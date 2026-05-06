import json
import os
from datetime import datetime, timezone


class SessionLogger:
    def __init__(self, process_name: str, pid: int, log_dir: str = "logs"):
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        filename = f"{process_name}_{pid}_{timestamp}.json"
        self.log_path = os.path.join(log_dir, filename)
        self.entries = []
        self._write()  # create empty log immediately

    def _write(self):
        with open(self.log_path, "w") as f:
            json.dump(self.entries, f, indent=2)

    def log_stdout(self, line: str):
        self.entries.append({
            "type": "STDOUT",
            "line": line.strip(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self._write()

    def log_event(self, event_type: str, data: dict = None):
        entry = {
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        if data:
            entry["data"] = data
        self.entries.append(entry)
        self._write()

    def get_log_path(self) -> str:
        return self.log_path