# src/agent/tools/clock.py
import os, re, json, datetime
from typing import Optional, Dict, Any

DEBUG = os.getenv("AGENT_DEBUG") == "1"
def _dbg(*a):
    if DEBUG: 
        print("[DEBUG clock]", *a)

TRIGGERS = [
    r"\[\[\s*time\s*\]\]",                    # [[time]]
    r"\btime\s*\(\s*(?P<fmt>[^)]+)\s*\)",     # time(%Y-%m-%d)
]

def _maybe_parse_json(text: str) -> Optional[Dict[str, Any]]:
    """Try to parse JSON payload safely, else return None."""
    t = text.strip()
    if t.startswith("{") and t.endswith("}"):
        try:
            return json.loads(t)
        except Exception as e:
            _dbg("JSON parse error:", e)
            return None
    return None

def execute(text: Any) -> str:
    if not isinstance(text, str):
        text = str(text)

    # JSON form: {"tool":"clock","args":{"format":"%H:%M"}}
    j = _maybe_parse_json(text)
    if j and j.get("tool") == "clock":
        fmt = j.get("args", {}).get("format", "%Y-%m-%d %H:%M:%S")
        _dbg("JSON trigger matched with fmt:", fmt)
        return datetime.datetime.now().strftime(fmt)

    # Regex triggers: [[time]] or time(%Y-%m-%d)
    for pat in TRIGGERS:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            fmt = m.groupdict().get("fmt") or "%Y-%m-%d %H:%M:%S"
            _dbg("Regex trigger matched with fmt:", fmt)
            return datetime.datetime.now().strftime(fmt)

    # No trigger matched → raise so router can try others
    raise ValueError("No clock trigger matched")
