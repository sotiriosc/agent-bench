# AI Agent Benchmark — Starter

Quickstart:
1) python -m venv .venv && source .venv/bin/activate
2) pip install -r requirements.txt
3) python -m src.ui.cli "What is 23*17? Use the calculator."
4) python -m src.evals.run_lm_eval --task gsm8k_toy

### Calculator Tool
- **Triggers:** `[[calc: ...]]`, `calc(...)`, `CALCULATE: ...`, or plain math in text (e.g., “What is 12/3 + 7*4?”).
- **JSON/dict payloads supported** (when calling the tool programmatically, not via CLI):
  - `{"expression": "23*17+88"}`
  - `{"tool":"calculator","args":{"expression":"23*17+88"}}`
- **Unicode normalization:** `× ÷ − — –` → `* / -`; thousands commas removed inside numbers (e.g., `1,234` → `1234`).
- **Safety:** limited operators (+ − × ÷ and power), exponent/base caps, expression length cap, guarded AST eval, friendly zero-division errors.
- **Debug:** `export AGENT_DEBUG=1` to see extractor/eval steps.

**CLI**
```bash
python -m src.ui.cli --use-tools "What is 12/3 + 7*4 - 2?"
# -> 30
