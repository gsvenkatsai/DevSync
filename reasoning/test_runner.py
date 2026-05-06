import json
from engine import ReasoningEngine

# --- TEST CASES (MOCK CONTRACT B's) ---

TEST_CASES = [
    {
        "name": "Test 1: Safe Overwrite (Should return Y)",
        "payload": {
            "type": "INPUT_REQUIRED",
            "prompt_text": "Overwrite? [Y/n]:",
            "process_name": "train.py",
            "runtime_seconds": 1320,
            "context_lines": [
                "Checkpoint directory already exists at /runs/exp_041.",
                "Overwrite? [Y/n]:"
            ],
            "pid": 1001,
            "timestamp": "2026-05-03T10:00:00Z"
        }
    },
    {
        "name": "Test 2: Danger Word Override (Should return MANUAL_ONLY)",
        "payload": {
            "type": "INPUT_REQUIRED",
            "prompt_text": "DROP TABLE users? [Y/n]:",
            "process_name": "db_migrate.py",
            "runtime_seconds": 45,
            "context_lines": [
                "Connecting to production database...",
                "WARNING: This will destroy data.",
                "DROP TABLE users? [Y/n]:"
            ],
            "pid": 1002,
            "timestamp": "2026-05-03T10:05:00Z"
        }
    },
    {
        "name": "Test 3: Unknown Situation (AI should read SOUL.md and decide)",
        "payload": {
            "type": "INPUT_REQUIRED",
            "prompt_text": "Install package 'flask'? [y/N]:",
            "process_name": "pip install",
            "runtime_seconds": 12,
            "context_lines": [
                "Resolving dependencies...",
                "Install package 'flask'? [y/N]:"
            ],
            "pid": 1003,
            "timestamp": "2026-05-03T10:10:00Z"
        }
    }
]

def run_tests():
    # Insert your Grok API key here for the test run
    API_KEY = "xai-YOUR-KEY-HERE"
    
    print("🚀 Starting Reasoning Engine Test Suite...\n")
    engine = ReasoningEngine(api_key=API_KEY)
    
    passed = 0
    failed = 0

    for i, test in enumerate(TEST_CASES, 1):
        print(f"--- Running {test['name']} ---")
        try:
            # Pass the payload (Contract B) to your engine
            result = engine.reason(test["payload"])
            
            # Print the resulting Contract C
            print("Recommendation :", result.get("recommendation"))
            print("Reason         :", result.get("reason"))
            print("Risk Level     :", result.get("risk"))
            print("PID Passed?    :", "✅ Yes" if result.get("pid") == test["payload"]["pid"] else "❌ NO (CRITICAL FAILURE)")
            print("\n")
            passed += 1
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}\n")
            failed += 1

    print(f"🏁 Test Run Complete. Passed: {passed}, Failed: {failed}")

if __name__ == "__main__":
    run_tests()