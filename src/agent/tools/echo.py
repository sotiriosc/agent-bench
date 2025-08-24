import os, re, json, ast
from typing import Any, Dict, Optional

DEBUG = os.getenv("AGENT_DEBUG") == "1"
def _dbg(*a):
    if DEBUG: print("[DEBUG echo]", *a)

TRIGGERS = [
    r"\[\[\s*echo\s*:\s*(?P<text>.+?)\s*\]\]",   # [[echo: hello]]
    r"^echo\s*:\s*(?P<text>.+)$",                # echo: hello
    r"\becho\(\s*(?P<text>[^)]+)\s*\)",         # echo(hello)
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
    s = text if isinstance(text, str) else str(text)
    if isinstance(text, str):
        t = text.strip()
        if t.startswith("-") and not any(ch.isalnum() for ch in t):
            _dbg("ignoring flag-like input:", t)
            raise ValueError("no match")

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
