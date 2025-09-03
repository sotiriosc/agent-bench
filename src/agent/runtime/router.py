import os, sys, importlib.util, glob, inspect, types
from typing import Callable, Dict, Optional, Tuple

DEBUG = os.getenv("AGENT_DEBUG") == "1"
def _dbg(*a):
    if DEBUG: print("[DEBUG router]", *a)

TOOLS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools")

class Tool:
    def __init__(self, name: str, module: types.ModuleType, execute: Callable):
        self.name = name
        self.module = module
        self.execute = execute
        self.aliases = set()
        # Optional aliases from module
        for attr in ("TOOL_NAME", "TOOL_ALIAS", "TOOL_ALIASES"):
            if hasattr(module, attr):
                val = getattr(module, attr)
                if isinstance(val, str):
                    self.aliases.add(val)
                elif isinstance(val, (list, tuple, set)):
                    self.aliases |= set(map(str, val))
        self.aliases.add(name)

def _import_module_from_path(path: str) -> Optional[types.ModuleType]:
    spec = importlib.util.spec_from_file_location(
        f"agent.tools.{os.path.splitext(os.path.basename(path))[0]}", path
    )
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        _dbg("Failed importing", path, "->", e)
        return None

def discover_tools() -> Dict[str, Tool]:
    tools: Dict[str, Tool] = {}
    for path in glob.glob(os.path.join(TOOLS_DIR, "*.py")):
        base = os.path.basename(path)
        if base.startswith("_") or base == "__init__.py":
            continue
        mod = _import_module_from_path(path)
        if not mod:
            continue
        exec_fn = getattr(mod, "execute", None)
        if not callable(exec_fn):
            _dbg("Skip", base, "no execute()")
            continue
        name = getattr(mod, "TOOL_NAME", os.path.splitext(base)[0])  # prefer module TOOL_NAME
        tool = Tool(name=name, module=mod, execute=exec_fn)
        # Register primary and aliases (lowercased)
        for key in tool.aliases:
            tools[str(key).lower()] = tool
        _dbg("Loaded tool:", name, "aliases:", sorted(tool.aliases))
    return tools

# Cache so we don’t re-import on every call
_TOOLS_CACHE: Optional[Dict[str, Tool]] = None
def get_tools() -> Dict[str, Tool]:
    global _TOOLS_CACHE
    if _TOOLS_CACHE is None:
        _TOOLS_CACHE = discover_tools()
    return _TOOLS_CACHE

def run_once_with_tools(message: str) -> Tuple[str, Optional[str]]:
    """
    Try each tool exactly once. Each tool should raise on no-match.
    Returns (output, tool_name_or_None). If no tool matched, echo the input.
    """
    tools = get_tools()
    # De-duplicate by module (some names may point to same Tool via aliases)
    seen = set()
    for key, tool in tools.items():
        if id(tool) in seen:
            continue
        seen.add(id(tool))
        try:
            out = tool.execute(message)
            # If no exception, this tool matched.
            return str(out), tool.name
        except Exception:
            continue
    # No tool matched → plain echo (or pass to LLM in a real app)
    return message, None

def run_with_tools(message: str, max_chain: int = 1) -> Tuple[str, Optional[str], int]:
    """
    Run tools, then (optionally) chain if the output still looks like it might contain triggers.
    max_chain=1: one pass (no chaining).
    max_chain>1: up to that many total passes. Stops if a pass returns None tool.
    """
    out, name = run_once_with_tools(message)
    used = 0
    last_used = name
    if name: used = 1

    passes = 1
    while passes < max_chain:
        nxt, nxt_name = run_once_with_tools(out)
        if not nxt_name:
            break
        out = nxt
        last_used = nxt_name
        used += 1
        passes += 1

    return out, last_used, used
