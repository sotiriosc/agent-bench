#!/usr/bin/env bash
set -e
python -m src.evals.run_lm_eval --task gsm8k_toy
# Example real harness (after wiring model):
# lm_eval --model openai-chat --tasks mmlu --model_args model=gpt-4o-mini --num_fewshot 5 --apply_chat_template
