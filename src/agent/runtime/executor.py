from ..tools.calculator import calc
from ..llm.openai_llm import chat_once

class Executor:
    def run(self, prompt: str):
        # If it looks like math, use the calculator tool (deterministic)
        if any(sym in prompt for sym in ["+", "-", "*", "/", "×", "÷"]):
            return calc(prompt)
        # Otherwise, use the LLM via the Responses API
        return chat_once(prompt)
