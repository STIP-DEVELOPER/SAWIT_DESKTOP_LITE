import json
import os
from datetime import datetime
from threading import Lock

from utils.path import DATA_JSON


print(f"[Logger] Log file path: {DATA_JSON}")


_log_lock = Lock()
MAX_LOG_COUNT = 50


def _read_logs():
    if not os.path.exists(DATA_JSON):
        return []
    try:
        with open(DATA_JSON, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def _write_logs(logs):
    with open(DATA_JSON, "w") as f:
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
