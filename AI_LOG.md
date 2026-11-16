# AI_LOG

Honest log of AI use. Entries that record AI mistakes matter most. **Owner action:** add your own entries for anything you ask AI to do outside this list, and tick each item below only if you have actually checked it.

## Day 1 (Mon 16 Nov)

| # | Task given to AI (Claude Code) | Where it was wrong or weak | What I changed |
|---|---|---|---|
| 1 | Read the Day 1 pack, propose a data model, ingestion, claim set, personas and docs | First draft of the risk list said "six consecutive monthly increases" for AWS; there are six bills, so five increases. Corrected to "every bill is higher than the previous". | Edited `risks.json` |
| 2 | Draft the Atlas risk text | First draft asserted that the PMM role owns Atlas launch messaging as if it were a fact. It is only an inference from a job title. | Rewrote as assumption A-008, Low confidence |
| 3 | Test routing for "Does Priya hold the routing engine together?" | Question was routed to the Atlas topic instead of key-person risk (keyword overlap on "routing"). Test caught it. | Added keywords; replaced the test question with a clearer one (a cockpit that depends on exact wording is a known weakness, see ARCHITECTURE "Known limits") |
| 4 | Resolve source conflicts (ARR, burn, headcount) | AI proposed conclusions and reasoning in TRANSCRIPT_NOTES. Rules say the owner must decide. All entries are marked DRAFT with a Reviewed box. | Owner must review and rewrite each in own words before relying on them |

Things I (owner) have not yet verified myself: see the unchecked boxes in TRANSCRIPT_NOTES.md.
