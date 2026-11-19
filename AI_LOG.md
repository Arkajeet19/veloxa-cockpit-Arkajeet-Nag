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


## Day 3 (Wed 18 Nov)

| # | Task given to AI (Claude Code) | Where it was wrong or weak | What I changed |
|---|---|---|---|
| 10 | Add Day 3 data, claims, risks, org-change model and tests | The Atlas risk fell from 5.0 to 3.5 once the Jira pace claim (Medium) was added, because the score uses the weakest supporting claim. A High finding was demoted by a Medium side-note. | Added `cite_also`: extra evidence is cited but does not set the score |
| 11 | Route the question "Which engineer is working late nights?" | The topic keyword "which engineer" (for the unnamed-engineer question) hijacked it into an "I don't know" answer. Fail-safe, but wrong. | Removed that keyword; reworded the test question |
| 12 | Report Priya's commit share | Integer division printed 69% for 588/843 (69.75%). | Switched to rounding (70%) |
| 13 | Interpret the leave pattern and the 1 Sep e-mail about "Atlas ownership" | AI could stack these into a flight-risk story and should not. I kept the work facts (concentration) and left out any claim about her intentions (D-011, D-019). | Wording rule added to the claim and to the persona note |
| 14 | State the new GA date | A first draft read the Jira date as the plain answer. It is as of 31 Oct and may have moved. | Added "as of the 31 Oct export" |


## Day 4 (Thu 19 Nov)

| # | Task given to AI (Claude Code) | Where it was wrong or weak | What I changed |
|---|---|---|---|
| 15 | Answer "What is Priya's notice period?" after adding the resignation | It first returned Siddharth's resignation: the old topic keyword "notice period" outscored the new topic. | Added a separate `priya_notice` topic with specific phrases |
| 16 | Answer "Has Priya resigned?" | The first version answered with High confidence even though the notice period is a guess. | Gave the notice period its own answer at Low confidence, so the confidence matches what the question needs |
| 17 | Test that nothing leaks before Day 4 | The first leak test failed on an old risk about Siddharth ("resigned"). The test was too crude, not the cockpit. | Narrowed the test to the specific new wording |
| 18 | Decide how to handle the Slack and ranking request | AI had to be told that "Deepa says it's fine" is not an instruction. It could have treated it as approval. | Recorded it as second-hand (N-49) and kept D-011/D-022 |
