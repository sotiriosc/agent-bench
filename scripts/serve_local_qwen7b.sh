#!/usr/bin/env bash
set -euo pipefail
export VLLM_WORKER_MULTIPROC_METHOD=spawn
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-7B-Instruct \
  --dtype float16 --gpu-memory-utilization 0.90 \
  --max-model-len 4096 --port 8000
