import re

def is_valid_email(email: str) -> bool:
    """
    Verify if a string is a valid email format.
    Returns True if valid, False otherwise.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None



def check_password_requirements(s: str) -> list:
    """
    Checks a string against the following requirements:
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special symbol (@#$%^&+=! etc.)
    - Minimum length of 8 characters

    Returns a list of missing requirements.
    If list is empty => string meets all conditions.
    """
    missing = []

    if not re.search(r'[A-Z]', s):
        missing.append("Missing uppercase letter")
    if not re.search(r'[a-z]', s):
        missing.append("Missing lowercase letter")
    if not re.search(r'\d', s):
        missing.append("Missing digit")
    if not re.search(r'[@#$%^&+=!]', s):
        missing.append("Missing special symbol (@ # $ % ^ & + = !)")
    if len(s) < 8:
        missing.append("Must be at least 8 characters long")

    return missing