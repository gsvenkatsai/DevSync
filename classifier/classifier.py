import os
import json
from groq import Groq
from patterns import check_regex, PROMPT_PATTERNS, ERROR_PATTERNS

# Safely grab the key from your computer's environment variables
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def ask_groq_fallback(context_lines):
    """
    Layer 3: The LLM Fallback using Groq API.
    If the terminal hangs without a regex match, we ask Groq if it's a prompt.
    """
    if not GROQ_API_KEY:
        print("[Classifier] Warning: GROQ_API_KEY not set. Skipping LLM fallback.")
        return False, ""

    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        print(f"[Classifier] Failed to initialize Groq client: {e}")
        return False, ""

    # Join the last 20 lines into a single block of text
    terminal_context = "\n".join(context_lines[-20:])
    
    system_prompt = """
    You are an AI analyzing a terminal stdout stream. 
    The stream has paused. Is the process waiting for user input?
    Return strictly a JSON object, nothing else:
    {"is_waiting": true/false, "prompt_text": "the exact text of the prompt if waiting, or empty string"}
    """
    
    try:
        # Call the fast Llama 3 70B model via Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Terminal Output:\n{terminal_context}"}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1, # Keep it deterministic
            response_format={"type": "json_object"} # Force valid JSON
        )
        
        # Parse Groq's response
        result_text = chat_completion.choices[0].message.content
        result = json.loads(result_text)
        
        return result.get("is_waiting", False), result.get("prompt_text", "")
        
    except Exception as e:
        print(f"[Classifier] Groq API Error: {e}")
        # If the API fails, fail safely by assuming it's not a prompt
        return False, ""

def classify_event(contract_a):
    """
    Intakes Contract A (from Wrapper), outputs Contract B (to Reasoning Engine).
    """
    lines = contract_a.get("lines", [])
    last_line = lines[-1] if lines else ""
    silence_duration = contract_a.get("silence_duration", 0)
    
    event_type = "NOISE"
    prompt_text = ""

    # 1. Fast Regex Check (Input Required)
    if check_regex(last_line, PROMPT_PATTERNS):
        event_type = "INPUT_REQUIRED"
        prompt_text = last_line
        
    # 2. Fast Regex Check (Errors)
    elif check_regex(last_line, ERROR_PATTERNS):
        event_type = "ERROR"
        prompt_text = last_line

    # 3. LLM Fallback (Silence > 10s and no regex match)
    elif silence_duration >= 10:
        is_waiting, extracted_prompt = ask_groq_fallback(lines)
        if is_waiting:
            event_type = "INPUT_REQUIRED"
            prompt_text = extracted_prompt
            
    # 4. Fulfill Contract B
    contract_b = {
        "type": event_type,
        "prompt_text": prompt_text,
        "process_name": contract_a.get("process_name"),
        "runtime_seconds": contract_a.get("runtime_seconds"),
        "context_lines": lines[-30:], 
        "pid": contract_a.get("pid"),
        "timestamp": contract_a.get("timestamp")
    }
    
    return contract_b