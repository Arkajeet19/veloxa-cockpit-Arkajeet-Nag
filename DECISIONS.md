# DECISIONS

Choices I could defend either way. Format: context, options, choice, why, revisit if.

**D-001 Storage: SQLite (stdlib), rebuilt from raw on every run.** Options: Postgres, a vector DB, flat JSON. Chose SQLite because the corpus is tiny (187 records), setup is zero, SQL gives exact provenance joins, and a rebuild makes "fresh clone == my machine". Revisit if I need semantic search over long transcripts.

**D-002 Data model: provenance first.** Every spreadsheet row, PDF page, e-mail and transcript paragraph is a `record` with a stable id (`source:locator`) and the `known_at` of its release day. Higher-level `claims` cite records plus a verbatim quote. The build fails if any quote is not found in its record, so no answer can cite something that is not there. Chose this over letting an LLM summarise records, because grading is about whether answers are true and cited.

**D-003 Cockpit answers come from curated, evidence-checked claims, not free generation.** Options: RAG + LLM; hand-curated claims; rule-based. Chose claims + deterministic routing for Day 1: reproducible tests, no hallucination, I can explain every line. Cost: coverage grows only as I curate. The LLM is optional later (agent dialogue, paraphrase), never the arbiter of truth, which the hackathon rules also forbid.

**D-004 Point-in-time semantics.** Two time axes exist: when something happened and when I learned it. "What did we know on date X" uses the second, as the brief says (release dates). A date-only X means end of that day IST. A claim becomes visible only when *all* of its evidence has been released. Event-date filtering is not implemented.

**D-005 Individual pay is never shown.** CFO (T2): salaries "must never show up in anything Ananya sees, only totals". The cockpit refuses per-person or ranked pay questions. Payroll errors are described with bucketed amounts ("under Rs 10,000") because an exact overpayment on a known day count would let anyone derive the salary. Agents follow the same rule. The one place salaries are read is the error check in `derive.py`, and they are not stored in claims.

**D-006 Which 14 agents.** The brief says 14 across engineering, finance, HR and marketing; Keka has exactly 5+3+3+3 = 14 in those departments. CEO, Sales and Support are not agents.

**D-007 "Worry" ranking = severity x confidence.** Severity (1-5) is my judgement written in `knowledge/risks.json`; confidence is the weakest supporting claim (High 1.0, Medium 0.7, Low 0.4). A risk is hidden until all its claims are released. I chose a transparent score over an opaque model so that I can change it live.

**D-008 What the cockpit refuses or hedges.** Refuses: individual or ranked pay. "I don't know": anything with no claim (competitors, weather, unreleased days), unclear referents (the board's "number"), unreported values (new Atlas GA date). Cannot predict: forecasts, with the facts so far. `sources_disagree`: ARR and burn. `answered_with_conflict`: headcount (conflict resolved with reasoning shown).

**D-009 Raw data in git, one folder per release day.** I commit each Day folder on its release day, which keeps history honest and the repo runnable from a fresh clone. The data is fictional per the brief. Revisit if the organisers object to the files being public.

**D-010 No LLM dependency on Day 1.** Setup needs only Python and three libraries (openpyxl, python-docx, pypdf) to read the exports.
