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
```

## Tests

`.venv/bin/python -m cockpit test` runs every question in `tests/questions.json` (expected status, required/forbidden text, required citations, confidence)
plus structural checks (every claim has evidence that exists; every invented persona fact is in ASSUMPTIONS.md; exactly 14 agents).
At least 5 questions test refusal / "I don't know" / disagreement handling.

## Status: Day 1 of 5

Loaded: Day 1 folder (T1, T2, brief, README, Employee Master, GL Apr-Sep, payroll Jan-Mar, two board updates, three e-mails).
Later folders are added on their release day (see git history). See ARCHITECTURE.md, DECISIONS.md, ASSUMPTIONS.md, TRANSCRIPT_NOTES.md, AI_LOG.md.

Veloxa and everything in `data/raw` is fictional and provided by the hackathon organisers.
