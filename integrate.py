import json
import os
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "classifier"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "reasoning"))

from classifier import classify_event
from engine import ReasoningEngine

API_KEY = os.getenv("GROQ_API_KEY")
engine = ReasoningEngine(api_key=API_KEY, soul_path="SOUL.md")

def process_contract_a(contract_a):
    contract_b = classify_event(contract_a)
    print(f"[integrate] Contract B: type={contract_b['type']}")

    if contract_b["type"] == "NOISE":
        print("[integrate] NOISE — skipping reasoning")
        return None

    contract_c = engine.reason(contract_b)
    print(f"[integrate] Contract C: recommendation={contract_c['recommendation']}")
    return contract_c
