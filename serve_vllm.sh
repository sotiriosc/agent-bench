#!/usr/bin/env bash
set -euo pipefail

# Env defaults (can be overridden from the shell)
: "${OPENAI_BASE:=http://127.0.0.1:8000/v1}"
: "${OPENAI_MODEL:=Qwen/Qwen2.5-7B-Instruct}"
PORT="${OPENAI_PORT:-8000}"

echo "Starting vLLM OpenAI server:"
echo "  MODEL = $OPENAI_MODEL"
echo "  PORT  = $PORT"
echo

python -m vllm.entrypoints.openai.api_server \
  --model "$OPENAI_MODEL" \
  --host 0.0.0.0 \
  --port "$PORT" \
  --dtype auto \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.90
