import os, requests
from typing import Tuple, Dict, Any

BASE = os.getenv("OPENAI_BASE", "http://127.0.0.1:8000/v1")
MODEL = os.getenv("OPENAI_MODEL", "Qwen/Qwen2.5-7B-Instruct")
API_KEY = os.getenv("OPENAI_API_KEY", "sk-not-needed")

def chat(prompt: str,
         system: str = "You are helpful and concise.",
         temperature: float = 0.2,
         max_tokens: int = 256,
         timeout: int = 60) -> Tuple[str, Dict[str, Any]]:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}
    r = requests.post(f"{BASE}/chat/completions", json=payload, headers=headers, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    text = data["choices"][0]["message"]["content"].strip()
    usage = data.get("usage", {})
    return text, usage
