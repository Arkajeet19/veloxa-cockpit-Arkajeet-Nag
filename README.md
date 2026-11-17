# veloxa-cockpit

A CXO cockpit for the fictional company Veloxa Technologies (Hiyaku Systems hackathon, 16-20 Nov 2026).
The CEO asks one question and gets a short answer that cites the exact records behind it, states a confidence level, and says
"I don't know" or "the sources disagree" when that is the honest answer. A second view ranks what she should worry about.
14 colleagues exist as grounded agent cards. Everything is point-in-time aware: later material never leaks into earlier answers.

## Run (one command, fresh clone)

```bash
./run.sh
```

Needs Python 3.10+ and internet for `pip install` (openpyxl, python-docx, pypdf). It builds the database, runs the test set, and prints the worry list and a sample answer.

## Use

```bash
.venv/bin/python -m cockpit ask "How many people work at Veloxa?"
.venv/bin/python -m cockpit ask "What is our ARR?" --as-of 2026-11-15   # nothing released yet -> "I don't know"
.venv/bin/python -m cockpit worry
.venv/bin/python -m cockpit agent "Fatima"        # or no name for all 14
./run.sh repl                                      # interactive
python -m cockpit              # no arguments: the top three things to worry about
python -m cockpit serve        # local page at http://127.0.0.1:8000: top three, then an ask box
python -m cockpit ask "Is attrition high?" --as-of 2026-11-16   # the same question as it stood on Day 1
```

## Tests

`.venv/bin/python -m cockpit test` runs every question in `tests/questions.json` (expected status, required/forbidden text, required citations, confidence)
plus structural checks (every claim has evidence that exists; every invented persona fact is in ASSUMPTIONS.md; exactly 14 agents).
At least 5 questions test refusal / "I don't know" / disagreement handling.

## Status: Day 2 of 5

Loaded: the Day 1 and Day 2 folders (Day 2 adds the Head of People call, the CEO voice note T6a, the leave register, hiring tracker, pulse survey, a resignation letter and four e-mails). Later folders are added on their release day; see the git history.
