from datetime import datetime, timezone


def build_summary(entries: list, process_name: str, pid: int) -> dict:
    """
    Compiles a session summary from log entries.
    Called on process exit.
    """
    spawn_time = None
    exit_time = None
    stdout_lines = []
    silence_events = []
    injections = []
    errors = []

    for entry in entries:
        etype = entry.get("type")

        if etype == "SPAWN":
            spawn_time = entry["timestamp"]

        elif etype == "EXIT":
            exit_time = entry["timestamp"]

        elif etype == "STDOUT":
            line = entry.get("line", "")
            stdout_lines.append(line)
            # Detect errors in stdout
            if any(kw in line.lower() for kw in ["error", "exception", "traceback", "failed"]):
                errors.append(line)

        elif etype == "SILENCE_DETECTED":
            silence_events.append(entry["timestamp"])

        elif etype == "INJECTION":
            injections.append({
                "response": entry["data"]["response"],
                "mode": entry["data"]["mode"],
                "timestamp": entry["timestamp"]
            })

    # Compute duration
    duration_seconds = None
    if spawn_time and exit_time:
        fmt = "%Y-%m-%dT%H:%M:%S.%f+00:00"
        try:
            t0 = datetime.fromisoformat(spawn_time)
            t1 = datetime.fromisoformat(exit_time)
            duration_seconds = round((t1 - t0).total_seconds(), 2)
        except Exception:
            duration_seconds = None

    return {
        "process_name": process_name,
        "pid": pid,
        "spawn_time": spawn_time,
        "exit_time": exit_time,
        "duration_seconds": duration_seconds,
        "total_stdout_lines": len(stdout_lines),
        "silence_events": len(silence_events),
        "injections": injections,
        "errors_detected": errors,
        "summary_generated_at": datetime.now(timezone.utc).isoformat()
    }