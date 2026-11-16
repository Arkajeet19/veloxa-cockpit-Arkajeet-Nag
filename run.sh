#!/usr/bin/env bash
# One command from a fresh clone: ./run.sh
# Creates .venv, installs 3 libraries, builds the DB from data/raw, runs the test set,
# then prints a sample answer and the ranked worry list. Add `repl` to chat: ./run.sh repl
set -euo pipefail
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
if [ "${1:-}" = "repl" ]; then exec .venv/bin/python -m cockpit repl; fi
.venv/bin/python -m cockpit build
.venv/bin/python -m cockpit test
echo; echo "=== What should I worry about? ==="; .venv/bin/python -m cockpit worry
echo; echo "=== Sample question ==="; .venv/bin/python -m cockpit ask "What is our ARR?"
