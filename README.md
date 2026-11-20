# veloxa-cockpit

A CXO cockpit for the fictional company Veloxa Technologies (Hiyaku Systems hackathon, 16-20 Nov 2026).
The CEO asks one question and gets a short answer that cites the exact records behind it, states a confidence level, and says
"I don't know" or "the sources disagree" when that is the honest answer. A second view ranks what she should worry about.
14 colleagues exist as grounded agent cards. Everything is point-in-time aware: later material never leaks into earlier answers.

## Run (one command, fresh clone)

```bash
python run.py
```

Use `python3 run.py` on macOS or Linux. Needs Python 3.10+ and internet for `pip install` (openpyxl, python-docx, pypdf).
It creates a `.venv`, builds the database from `data/raw`, runs the full test set, then prints the worry list and a sample answer.
(`./run.sh` does the same on macOS and Linux.)

## Use

After `python run.py` has created `.venv`, use its Python: `.venv\Scripts\python` on Windows, `.venv/bin/python` on macOS and Linux. Below, `python` means that one.

```bash
python -m cockpit                       # no arguments: the top three things to worry about
python -m cockpit ask "How many people work at Veloxa?"
python -m cockpit ask "What is our ARR?" --as-of 2026-11-15   # nothing released yet -> "I don't know"
python -m cockpit ask "Is attrition high?" --as-of 2026-11-16 # the same question as it stood on Day 1
python -m cockpit worry                 # the full ranked list, each item with evidence
python -m cockpit agent "Fatima"        # one agent card, or no name for all 14
python -m cockpit serve                 # local page at http://127.0.0.1:8000: top three, then an ask box
python run.py repl                      # interactive
```

## Tests

`python -m cockpit test` runs 82 questions from `tests/questions.json` (expected status, required and forbidden text, required citations, confidence, as-of leakage cases; 33 of them test refusal, "I don't know", conflicts or forecasts) plus:
- structural checks: every claim has evidence that exists; every invented persona fact is in ASSUMPTIONS.md; every grounded persona quote is in its source; exactly 14 agents;
- a what-if scenario for T6b (hypothetical, dated reporting-line moves applied to a copy of the database);
- Day 4 checks (a reported resignation appears only from 19 Nov and never changes Keka's status);
- simulation checks (deterministic, consistent with the data, never leaks into answers).

## Stretch: simulated activity after 31 Oct

```bash
python -m cockpit simulate                  # all 14 agents, to 15 Dec 2026
python -m cockpit simulate --who Priya      # one person
```

Rule-based and seeded. Every line is labelled SIMULATED and names the claims it rests on. It is never used as evidence: `ask` and `worry` do not read it (ARCHITECTURE.md section 6).

## Where to look

- `ARCHITECTURE.md` design; `DECISIONS.md` choices I could defend either way; `ASSUMPTIONS.md` everything invented or uncertain.
- `TRANSCRIPT_NOTES.md` mishearings and contradictions, with my reasoning on which source I believed.
- `VOICE_NOTES.md` my response to each CEO voice note (T6a to T6d). `AI_LOG.md` how I used AI and where it was wrong.

## Status: Day 5 of 5 (final)

All four day folders are loaded and reconciled. The full test set passes with one command.
