import os, re, json, ast
from typing import Any, Dict, Optional

DEBUG = os.getenv("AGENT_DEBUG") == "1"
def _dbg(*a):
    if DEBUG: print("[DEBUG echo]", *a)

TRIGGERS = [
    r"(?s)^\[\[\s*echo\s*:\s*(?P<msg>.+)\s*\]\]\s*$",  # [[echo: ...]] (capture until the final closing ]])
    r"^\s*echo\s*:\s*(?P<msg>.+)\s*$",                 # echo: ... (whole line)
]

def _maybe_json(text: str) -> Optional[Dict[str, Any]]:
    t = text.strip()
    if not t: return None
    if (t.startswith("{") and t.endswith("}")) or t.startswith("{'") or t.startswith('{"'):
        try:
            return json.loads(t)
        except json.JSONDecodeError:
            try:
                obj = ast.literal_eval(t)
                if isinstance(obj, dict): return obj
            except Exception:
                return None
    return None

def _extract_from_payload(payload: Dict[str, Any]) -> Optional[str]:
    # {"tool":"echo","args":{"text":"Hello"}}
    if payload.get("tool") == "echo":
        args = payload.get("args") or {}
        txt = args.get("text")
        if isinstance(txt, str): return txt
    # flat: {"text":"Hello"}
    txt = payload.get("text")
    if isinstance(txt, str): return txt
    return None

def execute(text: Any) -> str:
    # Normalize input to string
    s = text if isinstance(text, str) else str(text)

    # JSON trigger form
    j = _maybe_json(s)
    if j and j.get("tool") in {"echo"}:
        return str((j.get("args") or {}).get("text", ""))

    # Regex triggers
    for pat in TRIGGERS:
        m = re.search(pat, s, re.IGNORECASE)
        if m:
            return m.group("msg")

    # IMPORTANT: raise when no trigger matched
    raise ValueError("No echo trigger matched")


    # JSON
    payload = _maybe_json(s)
    if payload:
        got = _extract_from_payload(payload)
        if got is not None:
            return got

    # Triggers
    for pat in TRIGGERS:
        m = re.search(pat, s, flags=re.IGNORECASE)
        if m:
            return m.group("text")

    raise ValueError("No echo trigger matched")
