GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def color_text(text: str, color_code: str) -> str:
    """
    Returns colorized text if the terminal supports it.
    """
    return f"{color_code}{text}{RESET}"
