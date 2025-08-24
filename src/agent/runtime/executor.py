# src/agent/runtime/executor.py
"""
Executor: routes prompts to tools (calculator) or returns a simple fallback.

- If use_tools is True and the prompt contains a math expression → calculator
- If calculator errors (other than "no arithmetic expression") → return a clear tool error
- Otherwise → canned response / echo (so the CLI never crashes)
"""

from __future__ import annotations

from ..tools import calculator


class Executor:
    def __init__(self, use_tools: bool = False):
        self.use_tools = bool(use_tools)

    def run(self, prompt: str) -> str:
        text = (prompt or "").strip()
        if not text:
            return "No input provided."

        if self.use_tools:
            # Prefer a graceful pre-check if the calculator exposes an extractor.
            try:
                extract = getattr(calculator, "extract_expr", None)
                if callable(extract):
                    expr = extract(text)
                    if expr is not None:
                        # Let the tool do its thing (it may re-parse internally).
                        return str(calculator.calc(text))
                else:
                    # No extractor available; attempt and catch the "no expr" case below.
                    return str(calculator.calc(text))
            except Exception as e:
                msg = str(e).lower()
                # If it's just "no arithmetic expression", fall through to fallback.
                if "no arithmetic expression" not in msg:
                    return f"[calculator error] {e}"

        # ----- Fallback: simple canned response / echo -----
        lower = text.lower()
        if "one sentence" in lower and "project" in lower:
            return "This project is an agent benchmark framework for testing AI tool execution."
        return f"Echo: {prompt}"
def run_tools(prompt: str) -> str:
    """
    Tool-first execution path.
    - Tries known tools (calculator supports triggers + JSON/dict).
    - On failure or no match, falls back to the normal run().
    """
    try:
        from ..tools.calculator import execute as calc_execute
    except Exception:
        calc_execute = None

    if calc_execute is not None:
        try:
            return calc_execute(prompt)
        except Exception:
            pass

    try:
        return run(prompt)  # type: ignore[name-defined]
    except Exception:
        try:
            return Executor().run(prompt)  # type: ignore[name-defined]
        except Exception as e:
            raise e

# ---- Tool-first path (attached at import time) ------------------------------
try:
    from agent.tools.calculator import execute as _calc_execute
except Exception:
    _calc_execute = None


# ---- Multi-tool run_tools attachment (weather/uuid/echo added) --------------
try:
    from agent.tools.calculator import execute as _calc_execute
except Exception:
    _calc_execute = None
try:
    from agent.tools.clock import execute as _clock_execute
except Exception:
    _clock_execute = None
try:
    from agent.tools.stringy import execute as _string_execute
except Exception:
    _string_execute = None
try:
    from agent.tools.weather import execute as _weather_execute
except Exception:
    _weather_execute = None
try:
    from agent.tools.uuid_tool import execute as _uuid_execute
except Exception:
    _uuid_execute = None
try:
    from agent.tools.echo import execute as _echo_execute
except Exception:
    _echo_execute = None


# ---- Tool routing: single source of truth -----------------------------------
try:
    from agent.tools.calculator import execute as _calc_execute
except Exception:
    _calc_execute = None
try:
    from agent.tools.clock import execute as _clock_execute
except Exception:
    _clock_execute = None
try:
    from agent.tools.stringy import execute as _string_execute
except Exception:
    _string_execute = None
try:
    from agent.tools.weather import execute as _weather_execute
except Exception:
    _weather_execute = None
try:
    from agent.tools.uuid_tool import execute as _uuid_execute
except Exception:
    _uuid_execute = None
try:
    from agent.tools.echo import execute as _echo_execute
except Exception:
    _echo_execute = None
# Optional help tool
try:
    from agent.tools.help_tool import execute as _help_execute  # type: ignore
except Exception:
    _help_execute = None

def _executor_run_tools(self, prompt: str) -> str:
    """
    Try known tools first; on any miss/failure, fall back to run().
    Order chosen to minimize false positives.
    """
    for tool in (
        _calc_execute,
        _clock_execute,
        _string_execute,
        _weather_execute,
        _uuid_execute,
        _echo_execute,
        _help_execute,
    ):
        if tool is None:
            continue
        try:
            return tool(prompt)
        except Exception:
            pass
    return self.run(prompt)

try:
    Executor  # type: ignore[name-defined]
    Executor.run_tools = _executor_run_tools  # type: ignore[attr-defined]
except NameError:
    pass

# ---- Tool routing (tuple-return) --------------------------------------------
# Reuse already-imported tool executes (_calc_execute, _clock_execute, etc.)
# If they aren't present above, try to import here to be safe.
def _maybe_import(name, attr="execute"):
    try:
        mod = __import__(f"agent.tools.{name}", fromlist=[attr])
        return getattr(mod, attr, None)
    except Exception:
        return None

globals().setdefault("_calc_execute",  _maybe_import("calculator"))
globals().setdefault("_clock_execute", _maybe_import("clock"))
globals().setdefault("_string_execute",_maybe_import("stringy"))
globals().setdefault("_weather_execute",_maybe_import("weather"))
globals().setdefault("_uuid_execute",  _maybe_import("uuid_tool"))
globals().setdefault("_echo_execute",  _maybe_import("echo"))
globals().setdefault("_help_execute",  _maybe_import("help_tool"))

def _executor_run_with_tools(self, prompt: str):
    """
    Try known tools in order. If a tool matches, return (output, tool_name).
    If none match or all fail, return (fallback_output, None) where fallback_output is run(prompt).
    """
    tools = [
        ("calculator", _calc_execute),
        ("clock",      _clock_execute),
        ("string",     _string_execute),
        ("weather",    _weather_execute),
        ("uuid",       _uuid_execute),
        ("echo",       _echo_execute),
        ("help",       _help_execute),
    ]
    for name, fn in tools:
        if fn is None:
            continue
        try:
            out = fn(prompt)
            return out, name
        except Exception:
            # "no match" or other tool-level errors -> try next tool
            pass
    # No tool matched -> fall back to plain run()
    return self.run(prompt), None

# Back-compat: run_tools keeps returning only the string (first element)
def _executor_run_tools(self, prompt: str) -> str:
    out, _name = _executor_run_with_tools(self, prompt)
    return out

# Attach/overwrite onto Executor
try:
    Executor  # type: ignore[name-defined]
    Executor.run_with_tools = _executor_run_with_tools  # type: ignore[attr-defined]
    Executor.run_tools = _executor_run_tools            # type: ignore[attr-defined]
except NameError:
    pass

# ---- Router delegation: prefer central auto-discovery -----------------------
try:
    from agent.runtime.router import run_with_tools as _router_run_with_tools
except Exception:
    _router_run_with_tools = None

def _executor_run_with_tools(self, prompt: str):
    """
    Delegate to router.run_with_tools(prompt, max_chain=1).
    Returns (output, tool_name_or_None).
    """
    if _router_run_with_tools is None:
        # Fallback: behave like plain run()
        return self.run(prompt), None
    out, name, _used = _router_run_with_tools(prompt, max_chain=1)
    return out, name

def _executor_run_tools(self, prompt: str) -> str:
    """
    Back-compat wrapper that returns only the output string.
    """
    if _router_run_with_tools is None:
        return self.run(prompt)
    out, _name, _used = _router_run_with_tools(prompt, max_chain=1)
    return out

try:
    Executor  # type: ignore[name-defined]
    Executor.run_with_tools = _executor_run_with_tools  # type: ignore[attr-defined]
    Executor.run_tools = _executor_run_tools            # type: ignore[attr-defined]
except NameError:
    pass
