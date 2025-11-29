import json
import os
from datetime import datetime
from threading import Lock

LOG_FILE = os.path.join(os.getcwd(), "logs/data.json")

_log_lock = Lock()
MAX_LOG_COUNT = 100


def _read_logs():
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def _write_logs(logs):
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)


def add_log(level: str, source: str, message: str):
    """
    level   : "INFO" | "WARNING" | "ERROR"
    source  : e.g., "Camera", "System", "YOLO", "Serial"
    message : log message text
    """
    with _log_lock:
        logs = _read_logs()

        log_item = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "level": str(level),
            "source": str(source),
            "message": message,
        }

        logs.append(log_item)

        print(log_item)

        if len(logs) > MAX_LOG_COUNT:
            logs = logs[-MAX_LOG_COUNT:]

        _write_logs(logs)


def get_logs():
    """Return all logs as a list"""
    return _read_logs()
