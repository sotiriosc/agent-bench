#!/usr/bin/env python3
import os, time, json, requests, statistics, concurrent.futures as cf

BASE = os.environ.get("VLLM_BASE", "http://127.0.0.1:8000/v1")
MODEL = os.environ.get("MODEL", "Qwen/Qwen2.5-7B-Instruct")

PROMPTS = [
    "Summarize: This framework benchmarks tool execution for agents.",
    "List 5 risks when letting an LLM run tools.",
    "Explain why safe evaluation is used in our calculator.",
    "Rewrite this in one sentence: Tool routing with auto-discovery and chaining.",
]

def ask(prompt: str, max_tokens=128):
    payload = {
        "model": MODEL,
        "messages": [{"role":"user","content":prompt}],
        "temperature": 0.2,
        "max_tokens": max_tokens,
    }
    t0 = time.time()
    r = requests.post(f"{BASE}/chat/completions", json=payload, timeout=120)
    t1 = time.time()
    r.raise_for_status()
    data = r.json()
    txt = data["choices"][0]["message"]["content"].strip()
    usage = data.get("usage", {})
    out_tokens = usage.get("completion_tokens")
    return (t1 - t0), out_tokens, txt

def run_serial():
    times, toks = [], []
    for p in PROMPTS:
        dt, tk, _ = ask(p)
        times.append(dt)
        if tk is not None: toks.append(tk)
    tps = (sum(toks)/sum(times)) if toks and sum(times) > 0 else None
    print("\n=== Serial ===")
    print(f"count={len(times)}  avg={statistics.mean(times):.3f}s  p95={statistics.quantiles(times, n=20)[18]:.3f}s")
    if tps: print(f"throughput ≈ {tps:.1f} tok/s")

def run_concurrent(workers=4):
    times, toks = [], []
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(ask, p) for p in PROMPTS * 2]  # 8 requests
        for f in cf.as_completed(futs):
            dt, tk, _ = f.result()
            times.append(dt)
            if tk is not None: toks.append(tk)
    tps = (sum(toks)/sum(times)) if toks and sum(times) > 0 else None
    print(f"\n=== Concurrent (workers={workers}) ===")
    print(f"count={len(times)}  avg={statistics.mean(times):.3f}s  p95={statistics.quantiles(times, n=20)[18]:.3f}s")
    if tps: print(f"throughput ≈ {tps:.1f} tok/s")

if __name__ == "__main__":
    run_serial()
    run_concurrent(workers=int(os.environ.get("WORKERS", "4")))
