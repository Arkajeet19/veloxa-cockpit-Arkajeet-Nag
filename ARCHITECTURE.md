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
14 agents: everyone in Engineering, Finance, People & Ops and Marketing in Keka (5+3+3+3), as the brief asks. Role, manager, join date and location come from Keka (the manager shown follows confirmed, effective-dated changes; see section 7). Where the data mentions them (e.g. Fatima's wedding, Karthik's CFA, Priya's 1 Sep e-mail to Vikram), the card carries the quote. Invented private lives are labelled and logged as assumptions; a test fails if one is missing from ASSUMPTIONS.md, and another fails if a "grounded" quote is not found in its source.
Not built: conversational agents using an LLM. The agents are cards plus the simulation below.

**Stretch: simulated activity after 31 Oct (`python -m cockpit simulate`).** Rule-based and seeded (same seed, same events). Each agent has a short plan of plausible activity (commits, Jira moves, payroll, hiring calls, on-call) and a few dated events that follow from facts in the data (Vikram asks HR for the notice terms after the T6d report; November payroll; the 15 Dec GA review). Every event names the claims it rests on (`based_on`). Output is labelled SIMULATED, goes to its own table, and is never read by `ask` or `worry`, so it can never become evidence or leak into an answer. Consistency rules are tested: nobody acts after their exit date (Siddharth: none), Priya does only handover work after the 19 Nov resignation report, nothing says Atlas shipped, working days only, based_on claims must exist.

## 7. Cockpit behaviour
Order of checks for each question:
1. Policy guards: individual pay (D-005), ranking or naming individuals by likelihood to leave (D-011), reading individuals' private messages (D-022). Refused with the reason and a safer alternative.
2. Match the question to a topic (keyword score) and keep only claims released by the as-of date.
3. Answer from the believed claims. Roles: `answer`, `resolution` (supplies a value an earlier claim said was missing), `context`, `dissent` (a conflicting source, shown with why it was not relied on). `supersedes` chains make the latest released claim win.
4. Status: `answered`, `answered_with_conflict` (I resolved it; reasoning shown), `sources_disagree` (I could not), `unknown` ("I don't know"), `refused`, `cannot_predict` (forecasts and "what does X do to Y" questions: facts so far, no prediction).
5. No topic matched: look up a person (Keka, with effective-dated manager and any reported event), else "I don't know".
Every answer carries citations (record id plus the verbatim quote, checked at build time) and a confidence level.

Worry view: score = severity (my judgement, D-007) x confidence weight of the weakest supporting claim (High 1.0, Medium 0.7, Low 0.4); ties by risk id. A risk appears only when all its claims are released by the as-of date. `updates` swap in richer text when later claims arrive; `cite_also` adds evidence without lowering the score. Default view is the top three (T6a).

Time-varying structure: `org_changes` (planned or confirmed reporting-line changes with effective dates; T6b) and `reported_events` (things the CEO reports before HR records them, such as Priya's resignation; shown as notes, never changing Keka's status; T6d).

## 8. Privacy and safety (all built)
- Individual salaries are never shown; only totals. Payroll errors use bucketed amounts (D-005).
- Survey comments are not shown for teams under 6 (small-team rule).
- No ranking or naming of individuals by likelihood to leave; team-level indicators instead (D-011).
- No reading of individuals' messages; no Slack or chat export exists (D-022).
- Workload concentration is reported as concentration of work, never as someone's intentions (D-019).
- Invented personal details about agents are labelled and logged in ASSUMPTIONS.md.

## 9. Evaluation
`python -m cockpit test` runs 82 questions (expected status, required and forbidden text, required citations, confidence, as-of leakage cases; 33 cover refusal, uncertainty, conflict or "I don't know") plus: structural checks (every claim has evidence that exists, every invented persona fact is logged, every grounded persona quote is in its source, exactly 14 agents); a what-if scenario for T6b (hypothetical confirmed reporting-line moves applied to a copy of the database); Day 4 checks (reported resignation absent before 19 Nov, present after, Keka status untouched); and simulation checks (deterministic, consistent, never leaks into answers).

## 10. Build history
- Day 1: ingestion, provenance, claims with checked quotes, derived metrics, 14 agent cards, ask and worry views, as-of filtering.
- Day 2: People data; claim roles and `supersedes`; attrition and pulse checks; individual-risk refusal; top-three view; local page.
- Day 3: Jira, git, incidents, on-call, launch kit, invoice; `resolution` claims; computed concentration and Jira pace claims; effective-dated org changes (T6b).
- Day 4: voice notes only; message-surveillance guard; `reported_events` (T6c, T6d).
- Day 5: simulation (stretch), README and docs finalised, freeze.

## 11. Known limits
- Question routing is keyword-based; unusual wording can miss or hit the wrong topic. It fails safe (an "I don't know"), but coverage is limited. Several wrong routings were found and fixed during the week (see AI_LOG.md).
- Claims are curated by hand, so coverage is only as wide as what I curated. Every claim is checked against its source quote at build time, but a wrong judgement is still possible.
- No LLM and no semantic search. If added, they would supplement, and never replace, the structured evidence store.
- Event-date time travel (what was true on a date, as opposed to what was known) is not built; only the release-date axis is.
- Jira looks stale after mid-September while git does not, so Jira-based pace figures are warnings, not forecasts.
- Several people and names are resolved by judgement (two git identities for Priya, Sneha vs the contractor "Snehal"); each is logged with its confidence.
- The simulation is template-based: plausible, not predictive.
- Burn, ARR and runway do not reconcile across sources; the cockpit reports this rather than hiding it.

## 12. Principles
Evidence before generation. Traceability for every claim. Uncertainty stated, never faked. Release-aware reasoning. Privacy by default. Modular enough for requirements that arrive over time. Reproducible setup from a fresh clone.
