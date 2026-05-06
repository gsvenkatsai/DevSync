import pty
import os
import sys
import select
import time
import json
from datetime import datetime, timezone
from health import get_health
from logger import SessionLogger
from summary import build_summary

SILENCE_THRESHOLD = 10  # seconds
HEALTH_CHECK_INTERVAL = 5  # seconds

def build_contract_a(lines, silence_duration, process_name, runtime_seconds, pid):
    return {
        "lines": lines,
        "silence_duration": round(silence_duration, 2),
        "process_name": process_name,
        "runtime_seconds": round(runtime_seconds, 2),
        "pid": pid,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def get_contract_d_mock(process_name: str, pid: int) -> dict:
    # MOCK — replace with real gateway response on integration day
    return {
        "response": "Y",
        "mode": "manual",
        "process_name": process_name,
        "pid": pid,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def inject_response(master_fd: int, contract_d: dict):
    response = contract_d["response"] + "\n"
    os.write(master_fd, response.encode())
    print(f"[devsync] injected response: {repr(response)} (mode={contract_d['mode']})")

def trigger_classifier(contract_a: dict):
    print(f"\n[devsync] SILENCE DETECTED — emitting Contract A:")
    print(json.dumps(contract_a, indent=2))

def spawn(command: list[str]):
    pid, master_fd = pty.fork()

    if pid == 0:
        os.execvp(command[0], command)
    else:
        process_name = command[0]
        start_time = time.time()
        last_output_time = time.time()
        last_health_check = time.time()
        lines_buffer = []
        silence_triggered = False

        logger = SessionLogger(process_name=process_name, pid=pid)
        print(f"[devsync] spawned '{' '.join(command)}' with pid={pid}")
        print(f"[devsync] logging session to {logger.get_log_path()}")
        logger.log_event("SPAWN", {"command": command, "pid": pid})

        while True:
            try:
                r, _, _ = select.select([master_fd], [], [], 1.0)
                if r:
                    data = os.read(master_fd, 1024)
                    if not data:
                        break
                    line = data.decode(errors="replace")
                    print(line, end="", flush=True)

                    lines_buffer.append(line.strip())
                    logger.log_stdout(line)
                    last_output_time = time.time()
                    silence_triggered = False

                else:
                    # Silence check
                    silence_duration = time.time() - last_output_time
                    if silence_duration >= SILENCE_THRESHOLD and not silence_triggered:
                        runtime = time.time() - start_time
                        contract_a = build_contract_a(
                            lines=lines_buffer.copy(),
                            silence_duration=silence_duration,
                            process_name=process_name,
                            runtime_seconds=runtime,
                            pid=pid
                        )
                        trigger_classifier(contract_a)
                        logger.log_event("SILENCE_DETECTED", contract_a)

                        contract_d = get_contract_d_mock(process_name, pid)
                        print(f"\n[devsync] Contract D received: {json.dumps(contract_d, indent=2)}")
                        inject_response(master_fd, contract_d)
                        logger.log_event("INJECTION", contract_d)

                        silence_triggered = True

                    # Health check every 5s
                    if time.time() - last_health_check >= HEALTH_CHECK_INTERVAL:
                        health = get_health(pid)
                        print(f"[devsync:health] alive={health['alive']} status={health['status']} cpu={health['cpu_percent']}% ram={health['ram_mb']}MB")
                        logger.log_event("HEALTH_CHECK", health)
                        last_health_check = time.time()

                        if not health["alive"]:
                            print(f"[devsync] process {pid} is dead — exiting loop")
                            break

            except OSError:
                break

        os.waitpid(pid, 0)
        logger.log_event("EXIT", {"pid": pid, "process_name": process_name})

        # Layer 6 — build and print session summary
        summary = build_summary(logger.entries, process_name, pid)
        print(f"\n[devsync] SESSION SUMMARY:")
        print(json.dumps(summary, indent=2))

        # Save summary alongside the session log
        summary_path = logger.get_log_path().replace(".json", "_summary.json")
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"[devsync] summary saved to {summary_path}")

        print(f"[devsync] process '{process_name}' exited")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python wrapper.py <command> [args...]")
        sys.exit(1)

    spawn(sys.argv[1:])