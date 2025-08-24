class Planner:
    def plan(self, query: str):
        return [
            {"step": 1, "action": "think", "content": "Break down the problem."},
            {"step": 2, "action": "tool?", "content": "If numeric, use calculator."},
            {"step": 3, "action": "synthesize", "content": "Return final answer."},
        ]
