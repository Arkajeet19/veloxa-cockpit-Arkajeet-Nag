# VOICE_NOTES: responses to the CEO's voice notes


## T6a (released Tue 17 Nov, 10:00 IST; answered the same day)

**What Ananya said:** "I won't type questions every morning. When I open it, it should just tell me what to worry about. Top three."

**Decision: I made the change, with four deliberate limits.**

**What changed**
- `python -m cockpit` with no arguments now prints the top three worries and nothing else.
- `python -m cockpit serve` opens a local page (http://127.0.0.1:8000) that starts on the top three; the ask box sits below it.
- Each item shows why, a suggested action, a confidence level and its evidence ids.
- The remaining ranked items are one click or one command away ("N more items below the top 3"), so the cut is visible, not hidden.

**What I pushed back on, and why**
1. **Not a bare list.** "Just tell me" does not mean "without evidence". The CEO's own numbers (ARR, burn, headcount) turned out to be unreliable, so an unsupported alarm would do her harm. Confidence and evidence stay on every item; they are short, but never removed.
2. **Three is a cut, not the truth.** Items 2 and 3 tie on score (4.0) and the tie-break is just the risk id. The page says how many items sit below the cut. The ranking is my own severity judgement (D-007), and it will be wrong sometimes. I would rather she see that than a confident "the three".
3. **No "worry about people".** A morning list invites "who is about to quit". The cockpit will not name or rank individuals by resignation risk, even though the data (leave dates, survey) tempts that reading. It reports team-level signals only (D-011). Engineering engagement is item 3 for that reason.
4. **No push yet.** She said "when I open it". I did not build notifications, WhatsApp or a scheduled digest. It is a local page on this machine, bound to 127.0.0.1, because the data includes payroll totals and HR records. Putting it on a phone needs an access decision I should not make for her.

**Not done / open**
- Severity values are my judgement. If she disagrees, they are one number each in `knowledge/risks.json`.
- The page does not learn what she cares about.
- A standing "headline numbers disagree" banner (ARR, burn) is worth considering; it currently ranks 6th.

## T6b (released Wed 18 Nov, 10:00 IST; answered the same day)

**What Ananya said:** "Marketing will report to the new CRO from next month. Or the month after, still finalising. Make sure the thing doesn't break when we move people around."

**Decision: I changed how the system models reporting lines, and I did not make the move itself.**

**What changed**
- Reporting changes are now dated records (`knowledge/org_changes.json`, table `org_changes`), each marked `planned` or `confirmed`, with an effective date and a source record. Keka stays the truth until a change is confirmed.
- A person's manager and direct reports are computed *as of* a date. A confirmed change takes effect on its date; a planned change only adds a "planned, not confirmed" note to the card.
- The marketing move is recorded as `planned` (source: this voice note), and shows up on Nikhil's card, in the "who will marketing report to" answer, and as a ranked item in the worry list.
- A new test applies hypothetical, dated moves (Nikhil to a new CRO on 1 Dec, Aisha on 1 Jan) to a throwaway copy of the database and checks that: managers are right before and after each date, direct reports update on both sides, the worry list still builds, and every other test question still runs without error.

**What I pushed back on**
1. **I did not move marketing.** No CRO exists in Keka, the hiring tracker or the ledger; nobody is named; "next month, or the month after" is a two-month window; and Nikhil only "heard" it (T4). Changing a reporting line on a voice note would be inventing a fact. Confirming it is one record, so it is cheap to do once HR has it.
2. **"Doesn't break" is a promise I can only partly make.** Tested: reporting lines moving, someone being added, direct reports and manager answers following the dates. Not covered: department renames or mergers; the pulse survey's team boundaries (they would change if marketing moves); hand-written claims that mention a reporting line, which would need a human review. The 14 agents are fixed by roster, so a reporting change does not add or remove one.
3. **The move interacts with open problems.** Marketing is losing its product marketer, has no launch date from engineering, and its spend numbers do not match finance's. I added this as a low-ranked risk rather than treating the move as settled.

**Not done**
- No CRO person or agent; I will not invent one.
- No automatic handling of department-level changes.
