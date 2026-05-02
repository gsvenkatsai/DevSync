import psutil
from datetime import datetime, timezone


def get_health(pid: int) -> dict:
    """
    Returns CPU%, RAM usage in MB, and alive status for a given pid.
    Returns None if process doesn't exist.
    """
    try:
        proc = psutil.Process(pid)
        cpu = proc.cpu_percent(interval=0.1)
        mem = proc.memory_info().rss / (1024 * 1024)  # bytes → MB
        status = proc.status()
        return {
            "pid": pid,
            "alive": True,
            "status": status,
            "cpu_percent": round(cpu, 2),
            "ram_mb": round(mem, 2),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except psutil.NoSuchProcess:
        return {
            "pid": pid,
            "alive": False,
            "status": "dead",
            "cpu_percent": 0.0,
            "ram_mb": 0.0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except psutil.AccessDenied:
        return {
            "pid": pid,
            "alive": True,
            "status": "access_denied",
            "cpu_percent": -1,
            "ram_mb": -1,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }