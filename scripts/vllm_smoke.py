#!/usr/bin/env python3
import os, json, time, requests

BASE = os.environ.get("VLLM_BASE", "http://127.0.0.1:8000/v1")
MODEL = os.environ.get("MODEL", "Qwen/Qwen2.5-7B-Instruct")

def main():
    # models endpoint
    r = requests.get(f"{BASE}/models", timeout=10)
    r.raise_for_status()
    print("Models:", [m["id"] for m in r.json().get("data", [])])

    # chat completion
    payload = {
        "model": MODEL,
        "messages": [
            {"role":"system","content":"You are concise."},
            {"role":"user","content":"Give me one sentence about this project."}
        ],
        "temperature": 0.2,
        "max_tokens": 128,
    }
    t0 = time.time()
    r = requests.post(f"{BASE}/chat/completions", json=payload, timeout=60)
    dt = (time.time() - t0)
    r.raise_for_status()
    data = r.json()
    text = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    print(f"\nLatency: {dt:.3f}s")
    print("Usage:", usage)
    print("\nReply:", text.strip())

if __name__ == "__main__":
    main()
