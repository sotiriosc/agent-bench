# src/agent/tools/calculator.py
from __future__ import annotations

import ast
import operator as _op
import os
import re
from typing import Any, Optional, Union


# -----------------------------
# Debug helper
# -----------------------------
def _dbg(msg: str) -> None:
    if os.environ.get("AGENT_DEBUG"):
        print(f"[DEBUG calculator] {msg}")


# -----------------------------
# Normalization
# -----------------------------
UNICODE_MAP = {
    "−": "-",  # minus
    "–": "-",  # en dash
    "—": "-",  # em dash
    "×": "*",  # multiply
    "÷": "/",  # divide
}


def _normalize(s: str) -> str:
    # unify common unicode math glyphs
    for k, v in UNICODE_MAP.items():
        s = s.replace(k, v)
    # convert caret-power to Python's ** (common user expectation)
    s = s.replace("^", "**")
    # strip thousands separators when used as 1,234
    s = re.sub(r"(?<=\d),(?=\d{3}\b)", "", s)
    return s


# -----------------------------
# Limits / guards
# -----------------------------
MAX_EXP = 10  # max exponent magnitude
MAX_ABS = 10**12  # max base magnitude for exponentiation
MAX_EXPR_LEN = 512  # overall expression text length

# -----------------------------
# Expression extraction
# -----------------------------
# Triggers like:
#   [[calc: 23*17+88]]
#   calc(23*17+88)
#   CALCULATE: 23*17+88
TRIGGERS = [
    re.compile(r"\[\[\s*calc\s*:\s*([0-9.,+\-*/() \t^×÷]+)\]\]", re.I),
    re.compile(r"\bcalc\s*\(\s*([0-9.,+\-*/() \t^×÷]+)\s*\)", re.I),
    re.compile(r"\bcalculate\s*:\s*([0-9.,+\-*/() \t^×÷]+)", re.I),
]

# Generic arithmetic finder that tolerates spaces *between* tokens.
# We allow sequences of (number|op|paren) surrounded by optional whitespace.
GENERIC_EXPR = re.compile(
    r"(?P<expr>(?:\s*(?:\d[\d,]*\.?\d*|\.\d+|\(|\)|\*{1,2}|\/|\+|\-)\s*)+)",
    re.U,
)


def _longest_match(pattern: re.Pattern, text: str) -> Optional[str]:
    best = None
    best_len = -1
    for m in pattern.finditer(text):
        seg = m.group("expr")
        if seg and len(seg) > best_len:
            best = seg
            best_len = len(seg)
    return best


def extract_expr(text: str) -> Optional[str]:
    """
    Try to pull a math expression out of arbitrary text.
    Returns a normalized string or None if nothing plausible is found.
    """
    if not isinstance(text, str):
        return None
    raw = text
    text = _normalize(text)

    # Try explicit triggers first (against raw and normalized)
    for pat in TRIGGERS:
        m = pat.search(raw) or pat.search(text)
        if m:
            expr = _normalize(m.group(1)).strip()
            if expr:
                if len(expr) > MAX_EXPR_LEN:
                    raise ValueError("expression too long")
                return expr

    # Try generic expression finder: take the longest plausible span
    candidate = _longest_match(GENERIC_EXPR, text)
    if candidate:
        expr = candidate.strip()
        # Heuristic sanity: must contain a digit and at least one operator/paren
        if any(ch.isdigit() for ch in expr) and any(
            op in expr for op in ("+", "-", "*", "/", "(", ")")
        ):
            if len(expr) > MAX_EXPR_LEN:
                raise ValueError("expression too long")
            # If trailing operator snuck in (e.g., '23*17 +'), trim it
            expr = re.sub(r"[\+\-\*/\*]{1,2}\s*$", "", expr).strip()
            return expr or None

    return None


# -----------------------------
# Safe evaluation (AST)
# -----------------------------
_ALLOWED_BINOPS = {
    ast.Add: _op.add,
    ast.Sub: _op.sub,
    ast.Mult: _op.mul,
    ast.Div: _op.truediv,
    # exponent handled specially to enforce caps
}

_ALLOWED_UNARYOPS = {
    ast.UAdd: _op.pos,
    ast.USub: _op.neg,
}

Number = Union[int, float]


def _safe_eval(node: ast.AST) -> Number:
    # Numbers: Constant in py3.8+; Num for older ASTs
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("invalid constant")
    if isinstance(node, ast.Num):  # pragma: no cover (older versions)
        return node.n  # type: ignore[attr-defined]

    # Parentheses
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)

    # Unary +/-
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARYOPS:
        val = _safe_eval(node.operand)
        return _ALLOWED_UNARYOPS[type(node.op)](val)

    # Binary operations
    if isinstance(node, ast.BinOp):
        # Intercept exponent first to apply limits
        if isinstance(node.op, ast.Pow):
            base = _safe_eval(node.left)
            exp = _safe_eval(node.right)
            if not isinstance(base, (int, float)) or not isinstance(exp, (int, float)):
                raise ValueError("invalid power")
            if abs(exp) > MAX_EXP or abs(base) > MAX_ABS:
                raise ValueError("expression too large")
            return _op.pow(base, exp)

        # Allowed simple ops
        op_type = type(node.op)
        if op_type in _ALLOWED_BINOPS:
            left = _safe_eval(node.left)
            right = _safe_eval(node.right)
            return _ALLOWED_BINOPS[op_type](left, right)

        raise ValueError("operator not allowed")

    # Explicitly forbid everything else (names, calls, attrs, etc.)
    raise ValueError("invalid expression")


def evaluate(expr: str) -> Number:
    """
    Evaluate a normalized arithmetic expression safely.
    Raises ValueError with friendly messages.
    """
    if not isinstance(expr, str):
        raise ValueError("invalid input")

    expr = _normalize(expr).strip()
    if not expr:
        raise ValueError("no arithmetic expression found")
    if len(expr) > MAX_EXPR_LEN:
        raise ValueError("expression too long")

    try:
        tree = ast.parse(expr, mode="eval")
        result = _safe_eval(tree.body)  # evaluate expression body
    except ZeroDivisionError:
        raise ValueError("division by zero")
    except SyntaxError:
        raise ValueError("invalid syntax")

    # Prefer int if exact
    if isinstance(result, float) and result.is_integer():
        return int(result)
    return result


# -----------------------------
# Public API expected by executor / tests
# -----------------------------
def calc(text: Any) -> Number:
    """
    Main tool entry: parse out an expression from arbitrary text and evaluate it.
    Raises ValueError('no arithmetic expression found') if none present.
    """
    _dbg(f"type(text) = {type(text)}")
    if isinstance(text, str):
        _dbg(f"raw text (trunc): {repr(text[:80])}")

    # If dict/json payloads are passed, extract the expression
    if isinstance(text, dict):
        if "expression" in text:
            expr = text["expression"]
        elif "args" in text and isinstance(text["args"], dict) and "expression" in text["args"]:
            expr = text["args"]["expression"]
        else:
            raise ValueError("no arithmetic expression found")
        if not isinstance(expr, str):
            raise ValueError("invalid input")
        expr = _normalize(expr).strip()
        if not expr:
            raise ValueError("no arithmetic expression found")
        if len(expr) > MAX_EXPR_LEN:
            raise ValueError("expression too long")
        _dbg(f"extracted expr: {expr!s}")
        _dbg(f"final expr: {expr}")
        return evaluate(expr)

    # Otherwise treat as free-form text
    expr = extract_expr(text if isinstance(text, str) else str(text))
    _dbg(f"extracted expr: {expr!s}")

    if expr is None:
        raise ValueError("no arithmetic expression found")

    expr = _normalize(expr)
    _dbg(f"final expr: {expr}")

    return evaluate(expr)


# Legacy/expected public name from tests/CLI: return **string** here.
def execute(text: Any) -> str:
    """
    Compatibility wrapper: behaves like calc but returns a STRING result.
    Supports dict payloads with {"expression": "..."}.
    """
    result = calc(text)
    return str(result)


__all__ = ["extract_expr", "evaluate", "calc", "execute"]
