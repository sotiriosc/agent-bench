import os, time, requests

BASE  = os.environ.get("OPENAI_BASE",  "http://127.0.0.1:8000/v1")
MODEL = os.environ.get("OPENAI_MODEL", "Qwen/Qwen2.5-7B-Instruct")

SESSION_SYSTEM = (
    "You are an expert on THIS repository:\n"
    "- Name: agent-bench\n"
    "- Purpose: an agent benchmark framework for testing AI tool execution and routing.\n"
    "- Key pieces: calculator tool (safe AST), tool router, CLI, vLLM OpenAI-compatible server.\n"
    "Always answer about THIS project unless the question explicitly says otherwise. "
    "Be concise. If unsure, say: 'I don't know (project context missing)'."
)

def ask(prompt, max_tokens=128):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SESSION_SYSTEM},
            {"role": "user",   "content": prompt}
        ],
        "temperature": 0,
        "top_p": 1,
        "seed": 1,
        "max_tokens": max_tokens
    }
    t0 = time.time()
    r = requests.post(f"{BASE}/chat/completions", json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    dt = time.time() - t0
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return dt, usage, content

def run():
    tests = [
        ("One sentence only: give a concise summary of this project.", 64),
        ("List exactly three failure modes when auto-discovering and routing TOOLS in this codebase. Use terse bullets.", 96),
        ("In 2–3 sentences max: Why is safe AST evaluation better than eval() for OUR calculator tool?", 96),
    ]
    lat = []
    for q, mt in tests:
        print(f"\nQ: {q}")
        dt, usage, ans = ask(q, max_tokens=mt)
        lat.append(dt)
        print(f"T: {dt:.3f}s  usage={usage}")
        print("A:", ans)
    if lat:
        avg = sum(lat) / len(lat)
        print(f"\nAvg latency: {avg:.3f}s")

if __name__ == "__main__":
    run()
