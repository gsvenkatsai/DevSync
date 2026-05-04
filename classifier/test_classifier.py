import json
from classifier import classify_event

def run_tests():
    # TEST SCENARIO 1: The obvious Regex match [Y/n]
    contract_a_1 = {
        "lines": [
            "Epoch 42/100 Loss: 0.2371",
            "Saving checkpoint...",
            "File exists. Overwrite? [y/n]: "
        ],
        "silence_duration": 2,
        "process_name": "train.py",
        "runtime_seconds": 1320,
        "pid": 12345,
        "timestamp": "2026-05-04T18:10:00"
    }

    # TEST SCENARIO 2: Noisy terminal (Should be ignored)
    contract_a_2 = {
        "lines": [
            "npm WARN deprecated inflight@1.0.6",
            "added 412 packages in 2s"
        ],
        "silence_duration": 1,
        "process_name": "npm install",
        "runtime_seconds": 2,
        "pid": 12346,
        "timestamp": "2026-05-04T18:11:00"
    }

    # TEST SCENARIO 3: Hung process (Triggers LLM Fallback)
    '''contract_a_3 = {
        "lines": [
            "Connecting to database...",
            "Waiting for response..."
        ],
        "silence_duration": 15, # > 10 seconds triggers the fallback
        "process_name": "db_migrate.py",
        "runtime_seconds": 45,
        "pid": 12347,
        "timestamp": "2026-05-04T18:12:00"
    }'''

    contract_a_3 = {
        "lines": [
            "Initializing setup wizard...",
            "Please provide the absolute path to your configuration directory:",
        ],
        "silence_duration": 15, # > 10 seconds triggers the fallback
        "process_name": "setup.py",
        "runtime_seconds": 45,
        "pid": 12347,
        "timestamp": "2026-05-04T18:12:00"
    }

    print("--- Running Test 1 (Regex Match) ---")
    result_1 = classify_event(contract_a_1)
    print(json.dumps(result_1, indent=2))
    
    print("\n--- Running Test 2 (Noise) ---")
    result_2 = classify_event(contract_a_2)
    print(json.dumps(result_2, indent=2))
    
    print("\n--- Running Test 3 (LLM Fallback Trigger) ---")
    result_3 = classify_event(contract_a_3)
    print(json.dumps(result_3, indent=2))

if __name__ == "__main__":
    run_tests()