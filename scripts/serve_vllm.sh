#!/usr/bin/env bash
set -euo pipefail
MODEL="${MODEL:-Qwen/Qwen2.5-7B-Instruct}"
PORT="${PORT:-8000}"
DTYPE="${DTYPE:-float16}"
GPU_UTIL="${GPU_UTIL:-0.90}"
MAXLEN="${MAXLEN:-4096}"

echo "Starting vLLM on :$PORT with model: $MODEL"
python -m vllm.entrypoints.openai.api_server \
  --model "$MODEL" \
  --dtype "$DTYPE" \
  --gpu-memory-utilization "$GPU_UTIL" \
  --max-model-len "$MAXLEN" \
  --port "$PORT" \
  ${TRUST_REMOTE_CODE:+--trust-remote-code}
