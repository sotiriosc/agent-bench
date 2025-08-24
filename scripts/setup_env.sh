#!/usr/bin/env bash
set -e
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Env ready. Activate with: source .venv/bin/activate"
