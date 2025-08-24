import re

def _normalize(s: str) -> str:
    # normalize common unicode math symbols to ASCII
    return (s.replace("×", "*")
             .replace("−", "-")
             .replace("—", "-")
             .replace("–", "-")
             .replace("÷", "/"))

def calc(text: str) -> str:
    try:
        text = _normalize(text)

        # Find ALL candidate arithmetic substrings, then pick the longest that has at least one operator and a digit
        candidates = re.findall(r"[0-9][0-9\.\s\+\-\*\/\%\(\)]*[0-9]", text)
        if not candidates:
            return "ERROR: no arithmetic expression found"

        # Choose the longest candidate (more likely to be the intended expression)
        expr = max(candidates, key=len).strip()

        # Trim any trailing dots/spaces that sneak in from sentences
        expr = expr.rstrip(". ").lstrip(". ")

        if not expr:
            return "ERROR: empty expression"

        # Safety check: only allow these characters
        allowed = set("0123456789+-*/().% ")
        if any(ch not in allowed for ch in expr):
            return "ERROR: disallowed characters"

        return str(eval(expr, {"__builtins__": {}}))
    except Exception as e:
        return f"ERROR: {e}"
