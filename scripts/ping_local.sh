#!/usr/bin/env python
from openai import OpenAI
c = OpenAI(base_url="http://127.0.0.1:8000/v1", api_key="EMPTY")
print(c.models.list())  # quick sanity
r = c.chat.completions.create(
    model="Qwen/Qwen2.5-7B-Instruct",
    messages=[{"role":"user","content":"Say hi in one short sentence."}],
    max_tokens=50,
)
print(r.choices[0].message.content)
