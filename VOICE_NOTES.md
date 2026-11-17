# VOICE_NOTES: responses to the CEO's voice notes

> DRAFT for owner review. Rewrite in your own words before relying on it; you will be asked to defend each choice.

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
