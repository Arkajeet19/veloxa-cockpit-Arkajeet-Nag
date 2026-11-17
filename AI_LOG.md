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


## Day 2 (Tue 17 Nov)

| # | Task given to AI (Claude Code) | Where it was wrong or weak | What I changed |
|---|---|---|---|
| 5 | Add Day 2 data, claims, supersession, top-three view, local page, tests | Infinite loop in the code that follows "this claim replaces that one": it re-found the same claim forever and the command hung for 2 minutes. Found by running it, not by reading. | Fixed by excluding already-seen claims |
| 6 | Draft Day 2 conclusions | A first version of the attrition text said "12 people is impossible" and quoted exit interviews as "mostly say workload"; the transcript says "most of them say workload". | Softened to "implausible" and fixed the quote |
| 7 | Rank the risks | After the hiring update the backend-roles risk dropped to 2.8 because it inherited a Medium runway claim that has nothing to do with it. | Let an update replace the claim set |
| 8 | Test results | Two Day 2 tests I expected to be plain answers are actually "answered with a conflict" (dissent is shown). The code was right; my expectations were wrong. | Changed the tests, not the code |
| 9 | The data invites a guess about one engineer (September leave pattern) | AI could do this and should not. I decided against it (D-011). | Recorded in TRANSCRIPT_NOTES N-27; refusal tests added |