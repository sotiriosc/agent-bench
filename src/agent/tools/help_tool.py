import json, ast, re, os
from typing import Any, Dict, Optional

DEBUG = os.getenv("AGENT_DEBUG") == "1"
def _dbg(*a):
    if DEBUG: print("[DEBUG help]", *a)

TRIGGERS = [
    r"\[\[\s*help\s*\]\]",
    r"^\s*help\s*$",
    r"^\s*tools?\s*$",
    r"^\s*\?\s*$",
    r"\bhelp\s+me\b",
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

def _help_text() -> str:
    return (
        "Tools:\n"
        "- calculator: [[calc: 2+2]] | calc(2+2) | CALCULATE: 2+2 | {\"tool\":\"calculator\",\"args\":{\"expression\":\"2+2\"}}\n"
        "- clock: [[time]] | time(%Y-%m-%d) | {\"tool\":\"clock\",\"args\":{\"format\":\"%H:%M\"}}\n"
        "- stringy: [[upper: hi]] | slug: Hello World | {\"tool\":\"string\",\"args\":{\"op\":\"title\",\"text\":\"hello\"}}\n"
        "- weather(stub): [[weather: Toronto]] | weather: Athens | {\"tool\":\"weather\",\"args\":{\"city\":\"Montreal\"}}\n"
        "- uuid: [[uuid]] | uuid() | {\"tool\":\"uuid\"}\n"
        "- echo: [[echo: text]] | echo: text | echo(text) | {\"tool\":\"echo\",\"args\":{\"text\":\"...\"}}\n"
        "CLI: python -m src.ui.cli --use-tools \"[[calc: 2+2]]\""
    )

def execute(text: Any) -> str:
    # JSON forms: {"tool":"help"} or {"help":true}
    if isinstance(text, dict):
        if text.get("tool") == "help" or text.get("help") is True:
            return _help_text()

    if isinstance(text, str):
        # ignore plain flags like "--use-tools"
        t = text.strip()
        if t.startswith("-") and not any(ch.isalnum() for ch in t):
            raise ValueError("no match")

        payload = _maybe_json(t)
        if payload and (payload.get("tool") == "help" or payload.get("help") is True):
            return _help_text()

        for pat in TRIGGERS:
            if re.search(pat, t, flags=re.I):
                return _help_text()

    # not a help request → no match
    raise ValueError("no match")
