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
