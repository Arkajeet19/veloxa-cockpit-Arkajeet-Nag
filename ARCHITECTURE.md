# ARCHITECTURE

Version 1, Mon 16 Nov 2026. Updated as the design changes (see git history).

## Goal and non-goals
Answer CEO questions that are *true against the data room, cited, confidence-rated, and honest about gaps*. Not a dashboard, not a free-form chatbot. Judgement over coverage: correctness of what it says matters more than how many questions it can answer.

## Data flow

```
data/raw/DayN_*/            (added on release day N, never edited)
   |  cockpit/ingest.py     xlsx/csv/docx/pdf/eml -> one `record` per row/page/paragraph/e-mail
   v
SQLite build/veloxa.db  (rebuilt from scratch every run)
   sources(known_at = release time of the day folder)
   records(rec_id = source:locator, text, payload)
   people(Keka), aliases(entity resolution)
   topics, claims, claim_evidence(rec_id + verbatim quote)
   ^
   |  knowledge/topics.json  hand-curated claims (role: answer | dissent | context), each with evidence quotes
   |  cockpit/derive.py       claims computed from exports (payroll totals, AWS trend, summit spend, Feb payroll check)
   |  build FAILS if a quote is not found in the cited source
   v
cockpit/ask.py   policy guard -> topic match -> point-in-time filter -> answer + dissent + citations + confidence
cockpit/worry.py severity x confidence ranking from knowledge/risks.json
cockpit/agents.py  14 persona cards = Keka facts (grounded) + invented life (logged as A-P*)
tests/             34 questions + structural invariants, one command
```

## Key ideas
1. **Provenance is the spine.** Every claim points to records and a quote. The cockpit cannot cite what it cannot find.
2. **Claims have roles.** `answer` (what I believe), `dissent` (a conflicting source, shown with why I did not rely on it), `context`.
   Topic-level `dispute` decides the status: `sources_disagree` (unresolved) vs `answered_with_conflict` (resolved, reasoning shown).
3. **Point-in-time.** `known_at` comes from the release schedule. A claim is visible only if every piece of its evidence is released by the as-of time. Risks and agents obey the same rule.
4. **Refusal is a feature.** Individual salaries (CFO instruction), unknown values (new Atlas GA date), unclear referents (board's "number"), forecasts.
5. **Agents are grounded.** Roles, managers, joining dates, locations come from Keka. Invented private lives are tagged with an assumption id, and a test fails if one is not logged.

## Extension plan
- Day 2 (People): leave register, hiring tracker, pulse survey, resignation letter, e-mails 06/07/10/11, T3, T6a. Add claims; revisit A-008/attrition; may *supersede* earlier claims (`supersedes` column) so as-of answers stay correct.
- Day 3 (Engineering/Marketing): Jira, git log, incidents, on-call, launch kit, invoice PIS-114, T4/T5/T6b, e-mails 04/05/08/09. Test the Priya key-person claim against commits; reconcile marketing vs finance spend.
- Day 4: voice notes T6c/T6d only.
- Day 5: stretch (agents continuing after 31 Oct), hardening, freeze.

## Known limits (honest)
- Question routing is keyword-based, so unusual phrasings can fall to "I don't know" or hit the wrong topic. It fails safe, but it is a coverage limit.
- Claims are curated by hand, so coverage is only as wide as what I have curated; derived claims cover numbers computed from exports.
- No LLM yet. Agent *dialogue* (talking to a persona) is not built; only cards and grounding. Planned for Day 3 with a strict "answer only from your records" prompt.
- Event-date time travel is not implemented, only release-date (D-004).
