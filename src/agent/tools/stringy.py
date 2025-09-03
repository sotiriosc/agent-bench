TOOL_ALIASES = ["string", "stringy"]
import os, re, json
from typing import Any, Dict, Optional

DEBUG = os.getenv("AGENT_DEBUG") == "1"
def _dbg(*a):
    if DEBUG:
        print("[DEBUG stringy]", *a)

OPS = {"upper", "lower", "title", "slug"}

TRIGGERS = [
    r"\[\[\s*(?P<op>upper|lower|title|slug)\s*:\s*(?P<text>.+?)\s*\]\]",
    r"\b(?P<op>UPPER|LOWER|TITLE)\s*\(\s*(?P<text>[^)]+)\s*\)",
    r"^(?P<op>slug|upper|lower|title)\s*:\s*(?P<text>.+)$",
]

def _maybe_parse_json(text: str) -> Optional[Dict[str, Any]]:
    t = text.strip()
    if not t:
        return None
    if t.startswith("{") and t.endswith("}"):
        try:
            return json.loads(t)
        except Exception:
            return None
    return None

def execute(text: Any) -> str:
    """
    Apply string operations:
    - upper/lower/title
    - slug (lowercase, replace non-alphanum with '-')
    Trigger formats:
      [[upper: hello]]
      UPPER(hello)
      upper: hello
      {"tool":"stringy","args":{"op":"upper","text":"hello"}}
    """
    if not isinstance(text, str):
        text = str(text)
    _dbg("raw text:", text)

    # Try JSON first
    j = _maybe_parse_json(text)
    if j and j.get("tool") == "stringy":
        args = j.get("args", {})
        op, txt = args.get("op"), args.get("text")
        if op and txt:
            return _apply(op, txt)

    # Regex triggers
    for pat in TRIGGERS:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            op = m.group("op").lower()
            txt = m.group("text")
            return _apply(op, txt)

    raise ValueError("No stringy trigger matched")

def _apply(op: str, txt: str) -> str:
    if op not in OPS:
        raise ValueError(f"Unsupported op {op}")
    if op == "upper":
        return txt.upper()
    if op == "lower":
        return txt.lower()
    if op == "title":
        return txt.title()
    if op == "slug":
        return re.sub(r"[^a-z0-9]+", "-", txt.lower()).strip("-")
    raise ValueError(f"Unhandled op {op}")

