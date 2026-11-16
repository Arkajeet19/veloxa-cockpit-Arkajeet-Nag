# ARCHITECTURE

Version 2, Mon 16 Nov 2026 (Day 1). Updated as the design changes; see git history and DECISIONS.md.
Data snapshot: exports taken 31 Oct 2026.

## 1. Objective
An evidence-grounded cockpit where the CEO asks one question and gets a short answer that cites the records behind it, states a confidence level, and says "I don't know" or "the sources disagree" when that is the honest answer, plus a ranked "what should I worry about" view.
It is not a generic chatbot. It is decision support over imperfect, evolving data, so correctness and honesty matter more than coverage.

**Status legend.** *Built* = in the repo and tested today. *Planned* = intended, not built. Nothing in this document is described as built unless it is.

## 2. Components and data flow

```
data/raw/DayN_*/            added on release day N, never edited
   |  cockpit/ingest.py     xlsx / csv / docx / pdf / eml -> one `record` per row, page, paragraph or e-mail        [built]
   v
SQLite build/veloxa.db  (rebuilt from scratch on every run)                                                        [built]
   sources(known_at = release time of the day folder)
   records(rec_id = source:locator, text, payload)
   people (Keka), aliases (entity resolution)
   topics, claims, claim_evidence (rec_id + verbatim quote)
   ^
   |  knowledge/topics.json  hand-curated claims, role = answer | dissent | context                               [built]
   |  cockpit/derive.py       claims computed from exports (payroll totals, AWS trend, summit spend, Feb payroll)   [built]
   |  the build FAILS if a quoted string is not found in the cited record
   v
cockpit/ask.py     policy guard -> topic match -> release-date filter -> answer + dissent + citations + confidence     [built]
cockpit/worry.py   severity x confidence ranking from knowledge/risks.json                                          [built]
cockpit/agents.py  14 agent cards: Keka facts (grounded) + invented life tagged with an assumption id (A-P*)        [built: cards only]
tests/             34 questions + structural invariants, one command                                                [built]
```

Technology: Python 3.10+, standard-library `sqlite3`, `openpyxl`, `python-docx`, `pypdf`. No server, no LLM, no embeddings yet.

## 3. Data model
Relational store as the source of truth. Currently implemented tables: `sources`, `records`, `people`, `aliases`, `topics`, `claims`, `claim_evidence`.
Planned as later folders arrive: `activity` (evidence-backed work by person/team, from Jira/git/incidents), `project` (Atlas milestones, dependencies), `conflicts` as a first-class table if the topic-level `dispute` flag stops being enough.
The schema will change as packs arrive; changes are logged in DECISIONS.md.

## 4. Evidence and reconciliation
Every claim keeps provenance: the records it rests on and a verbatim quote. A claim is visible only when all its evidence has been released.

Vocabulary used in the docs, and how it maps to what the code does today:

| Label | Meaning | In the code |
|---|---|---|
| Verified | Backed by a system export | claim cites an export row; confidence High/Medium |
| Reported | Said in a transcript or e-mail, not confirmed | claim cites only transcripts; confidence Low/Medium |
| Inferred | Derived from several records | `derive.py` claims and reasoning text |
| Assumed | Invented or guessed, for simulation or gaps | ASSUMPTIONS.md; personas tagged A-P* |
| Conflicted | Sources disagree | `dissent` claims; status `sources_disagree` or `answered_with_conflict` |

These are conventions in the reasoning text and statuses, not a separate stored field. Making "verification status" a stored column is planned if it helps the cockpit.
Transcripts never override exports automatically, and exports are also checked (the Feb payroll error was found in an export). Uncertain entity matches are logged with a confidence and not silently merged (e.g. "Vicky", the two Sapphire vendors).

## 5. Time: release date and event date
Two dates exist for every fact: when it happened and when I learned it.
- **Release date (built).** Every source has `known_at` from the release schedule. `--as-of DATE` returns only what had been released by the end of that day IST. Later material cannot leak into earlier answers; tests cover this.
- **Event date (planned).** Filtering by when something happened, for questions like "what was the state of the company on 15 Sep". Not built; see Known limits.

## 6. Agents
14 agents: everyone in Engineering, Finance, People & Ops and Marketing in Keka (5+3+3+3), as the brief asks. Role, manager, join date and location come from Keka. Where the data mentions them (e.g. Fatima's wedding, Karthik's CFA), the card carries the quote. Invented private lives are labelled and logged as assumptions; a test fails if one is missing from ASSUMPTIONS.md.
Planned: conversational agents using an LLM that may only answer from that person's records and the as-of snapshot. Not built.

## 7. Cockpit behaviour
1. Policy guard: individual pay is refused (built).
2. Match the question to a topic and filter by release date (built).
3. Answer from believed claims, show conflicting sources and why they were not relied on, attach citations and confidence (built).
4. If the question asks for something the sources lack (new Atlas GA date) or a forecast, say so (built).
5. No topic matched: "I don't know" (built).

## 8. Privacy and safety
- Individual salaries are never shown to the CEO; only totals. Payroll errors use bucketed amounts (built, D-005).
- Planned for Day 2 data: do not expose small-team survey comments where individuals could be identified; do not rank individual employees by resignation likelihood; report aggregate retention indicators only. Each will get tests when the data arrives.
- Private communications are quoted only where needed as evidence.

## 9. Evaluation
`python -m cockpit test` runs 34 questions (status, required and forbidden text, required citations, confidence, as-of cases; 14 cover refusal, uncertainty or disagreement) plus structural checks (all claims have existing evidence, all invented persona facts are logged, exactly 14 agents). Target is to keep growing it each day.

## 10. Extension plan
- Day 2 (People): leave register, hiring tracker, pulse survey, resignation letter, e-mails, T3, T6a. Add claims; revisit the attrition claim; use `supersedes` so as-of answers stay correct.
- Day 3 (Engineering/Marketing): Jira, git, incidents, on-call, launch kit, invoice, T4/T5/T6b. Test the Priya key-person claim against commits; reconcile marketing vs finance spend.
- Day 4: voice notes T6c/T6d.
- Day 5: stretch (agents continuing after 31 Oct), hardening, freeze.

## 11. Known limits
- Question routing is keyword-based; unusual wording can miss or hit the wrong topic. It fails safe, but coverage is limited.
- Claims are curated by hand, so coverage is only as wide as what I have curated.
- No LLM and no semantic search yet. If added, they supplement, and never replace, the structured evidence store.
- Event-date time travel not built.
- Burn, ARR and runway do not reconcile; the cockpit reports this rather than hiding it.

## 12. Principles
Evidence before generation. Traceability for every claim. Uncertainty stated, never faked. Release-aware reasoning. Privacy by default. Modular enough for requirements that arrive over time. Reproducible setup from a fresh clone.