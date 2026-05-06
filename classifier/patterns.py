import re

# Layer 1: The "Hit List" of common terminal prompts
PROMPT_PATTERNS = [
    # Standard Confirmations
    r'\[Y/n\]', r'\[y/N\]', r'\(y/n\)', r'\(Y/n\)', r'\[yes/no\]',
    
    # Destructive / File Conflicts (High Risk)
    r'Overwrite.*?\?', r'already exists.*?confirm', r'replace.*?\?',
    
    # Pauses / Paging
    r'Press Enter to continue', r'Press any key', r'--More--',
    
    # Security / Auth
    r'Password:', r'passphrase:', r'Token:', r'Enter PIN:',
    
    # Package Managers (npm, pip, apt)
    r'Do you want to continue\?', r'Proceed\?', r'Is this ok\?',
    
    # Database / Migrations
    r'Are you sure you want to (drop|delete|remove)',
]

# Layer 5: Error Detection Signatures
ERROR_PATTERNS = [
    r'Traceback \(most recent call last\):',
    r'Error:', r'Exception:', r'FATAL:',
    r'Command .*? failed with exit code',
]

def check_regex(line, pattern_list):
    """Returns True if the line matches any pattern in the provided list."""
    for pattern in pattern_list:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    return False