import os, re, json, uuid
from typing import Any, Dict, Optional

DEBUG = os.getenv("AGENT_DEBUG") == "1"
def _dbg(*a):
    if DEBUG: print("[DEBUG uuid]", *a)

TRIGGERS = [
    r"\[\[\s*uuid\s*\]\]",    # [[uuid]]
    r"\buuid\(\s*\)\b",       # uuid()
    r"^\s*uuid\s*$",          # uuid
]

def _maybe_json(text: str) -> Optional[Dict[str, Any]]:
    t = text.strip()
    if t.startswith("{") and t.endswith("}"):
        try: return json.loads(t)
        except Exception as e: _dbg("JSON parse error:", e)
    return None

def execute(text: Any) -> str:
    s = text if isinstance(text, str) else str(text)

    # JSON-style: {"tool":"uuid"} or {"tool":"uuid","args":{"v":"4"}}
    j = _maybe_json(s)
    if j and j.get("tool") in {"uuid"}:
        v = str((j.get("args") or {}).get("v", "4")).strip()
        if v not in {"", "4"}:
            raise ValueError("uuid: only v4 supported")
        return str(uuid.uuid4())

    # Trigger-style
    for pat in TRIGGERS:
        if re.search(pat, s, re.IGNORECASE):
            return str(uuid.uuid4())

    raise ValueError("No uuid trigger matched")
