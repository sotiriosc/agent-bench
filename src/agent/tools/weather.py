import os, re, json, datetime
from typing import Any, Dict, Optional

DEBUG = os.getenv("AGENT_DEBUG") == "1"
def _dbg(*a):
    if DEBUG: print("[DEBUG weather]", *a)

TRIGGERS = [
    r"\[\[\s*weather\s*:\s*(?P<city>.+?)\s*\]\]",     # [[weather: Toronto]]
    r"\bweather\s*:\s*(?P<city>.+)$",                 # weather: Toronto
]

def _maybe_json(text: str) -> Optional[Dict[str, Any]]:
    t = text.strip()
    if t.startswith("{") and t.endswith("}"):
        try:
            return json.loads(t)
        except Exception as e:
            _dbg("JSON parse error:", e)
    return None

def _fake_report(city: str) -> str:
    day = datetime.datetime.now().strftime("%Y-%m-%d")
    return f"{day} | {city.strip()} | 22°C | Clear | wind 8 km/h"

def execute(text: Any) -> str:
    s = text if isinstance(text, str) else str(text)

    # JSON-style: {"tool":"weather","args":{"city":"Toronto"}}
    j = _maybe_json(s)
    if j and j.get("tool") in {"weather"}:
        city = (j.get("args") or {}).get("city")
        if not city:
            raise ValueError("weather: missing 'city'")
        return _fake_report(city)

    # Trigger-style
    for pat in TRIGGERS:
        m = re.search(pat, s, re.IGNORECASE)
        if m:
            return _fake_report(m.groupdict()["city"])

    raise ValueError("No weather trigger matched")
