import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load the hidden environment variables from the .env file
load_dotenv()

class ReasoningEngine:
    def __init__(self, api_key=None, soul_path="SOUL.md"):
        # Initialize the client pointing to Groq's insanely fast API
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        # Use "SOUL.md" for local testing. Change to "../SOUL.md" on Day 6 Integration.
        self.soul_path = soul_path

        # Layer 5: Danger detection words (Never auto-approve these)
        self.danger_words = ["DROP", "DELETE", "PURGE", "DESTROY"]

    def read_soul_md(self):
        """Layer 1: Read and structure project rules."""
        try:
            if os.path.exists(self.soul_path):
                with open(self.soul_path, 'r') as f:
                    return f.read()
            return "No specific project rules found."
        except Exception as e:
            return f"Error reading SOUL.md: {str(e)}"

    def reason(self, contract_b):
        """
        Main logic. Consumes Contract B, outputs Contract C using Groq (Llama 3).
        """
        prompt_text = contract_b.get("prompt_text", "").upper()
        
        # Layer 5: Hardcoded Danger Detection Override
        if any(danger_word in prompt_text for danger_word in self.danger_words):
            return self._build_contract_c(
                contract_b, 
                recommendation="MANUAL_ONLY", 
                reason="DANGER WORD DETECTED. Automatic override applied.", 
                risk="high"
            )

        # Layer 2: Context Builder
        soul_context = self.read_soul_md()
        context_lines = chr(10).join(contract_b.get('context_lines', []))

        # Layer 3: Groq API Call
        system_prompt = """
        You are DevSync, an intelligent terminal assistant. 
        A developer's process is paused for input. 
        Use the provided SOUL.md (Project Memory) and terminal context to recommend an action.
        
        CRITICAL: Output ONLY a valid JSON object. Do not include markdown formatting like ```json.
        JSON Structure:
        {
            "recommendation": "Y" or "N" or "CUSTOM",
            "reason": "One short sentence explaining why based specifically on SOUL.md if possible.",
            "confidence": "high", "medium", or "low",
            "risk": "low", "medium", or "high"
        }
        """

        user_content = f"""
        PROJECT RULES (SOUL.md):
        {soul_context}

        PROCESS NAME: {contract_b.get('process_name')}
        PROMPT DETECTED: {contract_b.get('prompt_text')}
        RUNTIME: {contract_b.get('runtime_seconds')} seconds
        
        LAST TERMINAL OUTPUT:
        {context_lines}
        """

        try:
            # Calling Groq via the OpenAI-compatible endpoint
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile", # Massive model, blistering fast, great at reasoning
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format={"type": "json_object"}, # Forces clean JSON
                temperature=0.1 # Keep it deterministic for reasoning
            )
            
            # Parse AI response
            ai_decision = json.loads(response.choices[0].message.content.strip())
            
            # Layer 4: Output Handler (Build Contract C)
            return self._build_contract_c(
                contract_b,
                recommendation=ai_decision.get("recommendation", "MANUAL"),
                reason=ai_decision.get("reason", "No reason provided."),
                risk=ai_decision.get("risk", "high")
            )

        except Exception as e:
            # Layer 6: Fallback if API fails
            print(f"API Error: {e}")
            return self._build_contract_c(
                contract_b, 
                recommendation="MANUAL", 
                reason="Groq API failed to generate a response.", 
                risk="high"
            )

    def _build_contract_c(self, contract_b, recommendation, reason, risk):
        """Helper to strictly enforce Contract C JSON structure."""
        return {
            "recommendation": recommendation,
            "reason": reason,
            "confidence": "high" if risk == "low" else "low",
            "risk": risk,
            "process_name": contract_b.get("process_name"),
            "prompt_text": contract_b.get("prompt_text"),
            "runtime_seconds": contract_b.get("runtime_seconds"),
            "pid": contract_b.get("pid"), # CRITICAL: Passing PID through for integration
            "timestamp": contract_b.get("timestamp")
        }


# --- TEST EXECUTION BLOCK ---
if __name__ == "__main__":
    
    # 2. Pull the key safely from the .env file
    API_KEY = os.getenv("GROQ_API_KEY") 
    
    # Safety check
    if not API_KEY:
        print("❌ Error: GROQ_API_KEY not found. Please check your .env file.")
        exit(1)
        
    # 3. Load the mock input file
    print("Loading Contract B from test_data/input.json...")
    with open("test_data/input.json", "r") as f:
        mock_input = json.load(f)
        
    # 4. Run the engine
    print("Asking Groq...")
    engine = ReasoningEngine(api_key=API_KEY)
    result = engine.reason(mock_input)
    
    # 5. Print Contract C
    print("\n=== FINAL OUTPUT (CONTRACT C) ===")
    print(json.dumps(result, indent=2))
    # 5. Print Contract C
    print("\n=== FINAL OUTPUT (CONTRACT C) ===")
    print(json.dumps(result, indent=2))
    
    # 6. Save the output to a physical file
    with open("test_data/output.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\n✅ Successfully saved to test_data/output.json!")