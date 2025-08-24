from ..tools.calculator import calc

class ReActPolicy:
    def decide(self, state):
        messages = state.get("messages", [])
        last = messages[-1] if messages else ""
        # naive: if math-like, use calculator
        if "calculator" in last.lower() or any(sym in last for sym in ["+", "-", "*", "/"]):
            expr = "".join(ch for ch in last if ch in "0123456789+-*/().% ")
            obs = calc(expr)
            return {"type": "finish", "content": f"{obs}"}
        return {"type": "finish", "content": "Demo policy: no tool needed. (Wire real LLM next.)"}
