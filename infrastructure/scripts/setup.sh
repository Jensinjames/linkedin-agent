#!/usr/bin/env bash
set -e

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt