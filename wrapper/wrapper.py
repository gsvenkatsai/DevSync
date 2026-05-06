import pty
import os
import sys
import select
import time
import json
from datetime import datetime, timezone
import threading
import websocket

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrate import process_contract_a
from health import get_health
from logger import SessionLogger
from summary import build_summary
contract_d_store = {}
ws_client = None

def connect_to_gateway(pid):
    global ws_client

    def on_message(ws, message):
        data = json.loads(message)
        print(f"[devsync] Contract D received from gateway: {json.dumps(data, indent=2)}")
        contract_d_store[data["pid"]] = data

    def on_open(ws):
        register_msg = json.dumps({"type": "REGISTER", "pid": pid})
        ws.send(register_msg)
        print(f"[devsync] registered with gateway for pid={pid}")

    GATEWAY_URL = os.environ.get("GATEWAY_URL", "ws://localhost:8765")
    ws_client = websocket.WebSocketApp(
        GATEWAY_URL,
        on_message=on_message,
        on_open=on_open
    )

    def run_with_retry():
        for attempt in range(5):
            try:
                ws_client.run_forever()
                break
            except Exception as e:
                print(f"[devsync] gateway connection failed (attempt {attempt+1}): {e}")
                time.sleep(2)

    thread = threading.Thread(target=run_with_retry, daemon=True)
    thread.start()

SILENCE_THRESHOLD = 10
HEALTH_CHECK_INTERVAL = 5

def build_contract_a(lines, silence_duration, process_name, runtime_seconds, pid):
    return {
        "lines": lines,
        "silence_duration": round(silence_duration, 2),
        "process_name": process_name,
        "runtime_seconds": round(runtime_seconds, 2),
        "pid": pid,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def get_contract_d_real(pid, timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        if pid in contract_d_store:
            return contract_d_store.pop(pid)
        time.sleep(0.5)
    print("[devsync] timeout waiting for Contract D — using fallback")
    return {
        "response": "N",
        "mode": "timeout",
        "process_name": "unknown",
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
        connect_to_gateway(pid)
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

                        from integrate import process_contract_a
                        contract_c = process_contract_a(contract_a)

                        if contract_c:
                            ws_client.send(json.dumps(contract_c))
                            print(f"[devsync] Contract C sent to gateway")
                            contract_d = get_contract_d_real(pid)
                        else:
                            print("[devsync] NOISE — no injection needed")
                            silence_triggered = True
                            continue

                        inject_response(master_fd, contract_d)
                        logger.log_event("INJECTION", contract_d)
                        silence_triggered = True

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

        summary = build_summary(logger.entries, process_name, pid)
        print(f"\n[devsync] SESSION SUMMARY:")
        print(json.dumps(summary, indent=2))

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