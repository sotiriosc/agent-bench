# src/agent/tools/calculator.py
import ast
import json
import os
import re
import operator as _op
from typing import Any

# ===========
# Debug print
# ===========
def _dbg(*args):
    if os.getenv("AGENT_DEBUG"):
        print("[DEBUG calculator]", *args)

# =========================
# Safe arithmetic evaluator
# =========================
_ALLOWED_BIN_OPS = {
    ast.Add: _op.add,
    ast.Sub: _op.sub,
    ast.Mult: _op.mul,
    ast.Div: _op.truediv,
    ast.Mod: _op.mod,
    ast.Pow: _op.pow,
    ast.FloorDiv: _op.floordiv,
}
_ALLOWED_UNARY_OPS = {
    ast.UAdd: _op.pos,
    ast.USub: _op.neg,
}
class _SafeEval(ast.NodeVisitor):
    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)
        if op_type not in _ALLOWED_BIN_OPS:
            raise ValueError(f"disallowed operator: {op_type.__name__}")
        return _ALLOWED_BIN_OPS[op_type](left, right)

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op_type = type(node.op)
        if op_type not in _ALLOWED_UNARY_OPS:
            raise ValueError(f"disallowed unary operator: {op_type.__name__}")
        return _ALLOWED_UNARY_OPS[op_type](operand)

    def visit_Num(self, node):  # py<3.8
        return node.n

    def visit_Constant(self, node):  # py>=3.8
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("only numeric constants allowed")

    def generic_visit(self, node):
        if isinstance(node, ast.Load):
            return super().generic_visit(node)
        forbidden = (
            ast.Call, ast.Attribute, ast.Subscript, ast.Name, ast.List, ast.Tuple,
            ast.Dict, ast.Set, ast.Compare, ast.BoolOp, ast.IfExp, ast.Lambda,
            ast.JoinedStr, ast.FormattedValue,
        )
        if isinstance(node, forbidden):
            raise ValueError(f"disallowed syntax: {type(node).__name__}")
        return super().generic_visit(node)

def safe_eval(expr: str) -> float:
    tree = ast.parse(expr, mode="eval")
    return _SafeEval().visit(tree)

# =========================
# Expression extraction
# =========================
_ALLOWED_CHARS = set("0123456789.+-*/()% \t")

_TRIGGER_PATTERNS = [
    re.compile(r"\[\[\s*calc\s*:\s*(.+?)\s*\]\]", re.IGNORECASE | re.DOTALL),  # [[calc: ...]]
    re.compile(r"\bcalc\s*\(\s*(.+?)\s*\)\s*$", re.IGNORECASE | re.DOTALL),     # calc(...)
    re.compile(r"\bcalculate\s*:\s*(.+)$", re.IGNORECASE | re.DOTALL),          # CALCULATE: ...
]

def _looks_like_flag(s: str) -> bool:
    s = s.strip()
    return s.startswith("-") and not any(ch.isdigit() for ch in s)

def _extract_from_triggers(s: str) -> str | None:
    for pat in _TRIGGER_PATTERNS:
        m = pat.search(s)
        if m:
            return m.group(1).strip()
    return None

def _extract_expr_from_text(text: str) -> str | None:
    s = text.strip()

    # use triggers if present
    t = _extract_from_triggers(s)
    if t:
        s = t

    # already arithmetic?
    if s and all(ch in _ALLOWED_CHARS for ch in s) and any(ch.isdigit() for ch in s):
        return s

    # clean to arithmetic-only
    cleaned = "".join(ch for ch in s if ch in _ALLOWED_CHARS).strip()

    # special-case: lone double dash (extractors sometimes grab it)
    if cleaned == "--":
        return "--"

    # ignore true flags (let caller decide)
    if _looks_like_flag(s):
        return None

    # must contain a digit and an operator to proceed
    if cleaned and any(ch.isdigit() for ch in cleaned) and any(op in cleaned for op in "+-*/%"):
        return cleaned

    return None

def _maybe_parse_json_string(s: str) -> Any | None:
    s2 = s.strip()
    if not (s2.startswith("{") and s2.endswith("}")):
        return None
    try:
        return json.loads(s2)
    except Exception:
        return None

# =========================
# Public API
# =========================
def execute(text: Any) -> str:
    """
    Accepts:
      - simple math:           "23*17+88"
      - questions:             "What is 23*17 + 88?"
      - triggers:              [[calc: 23*17+88]], calc(23*17+88), "CALCULATE: 23*17+88"
      - JSON/dict payloads:    {"expression":"..."}, {"args":{"expression":"..."}}
    """
    _dbg("type(text) =", type(text))
    if isinstance(text, str):
        _dbg("raw text (trunc):", repr(text[:120]))

    expr = None

    if isinstance(text, dict):
        if "expression" in text:
            expr = text["expression"]
        elif "args" in text and isinstance(text["args"], dict) and "expression" in text["args"]:
            expr = text["args"]["expression"]

    elif isinstance(text, str):
        payload = _maybe_parse_json_string(text)
        if isinstance(payload, dict):
            if "expression" in payload:
                expr = payload["expression"]
            elif "args" in payload and isinstance(payload["args"], dict) and "expression" in payload["args"]:
                expr = payload["args"]["expression"]
        else:
            expr = _extract_expr_from_text(text)

    _dbg("extracted expr:", expr)

    # Friendly behavior for the extractor edge case "--"
    if expr == "--":
        return "--"

    if not expr:
        # Do NOT treat flags as math; surface a clear error so the router can skip us.
        raise ValueError("no arithmetic expression found")

    _dbg("final expr:", expr)
    try:
        result = safe_eval(expr)
    except SyntaxError as e:
        raise ValueError(f"invalid expression: {e}") from e
    return str(result)

def calc(text: Any) -> str:
    return execute(text)
