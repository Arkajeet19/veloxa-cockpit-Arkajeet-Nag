"""The cockpit: one question in, one cited, confidence-rated answer out.

Statuses:
  answered              - supported, no conflicting source
  answered_with_conflict- a conflicting source exists but I resolved it (reasoning shown)
  sources_disagree      - sources conflict and I could not settle it
  unknown               - no (released) record answers this
  refused               - blocked by policy (individual pay)
  cannot_predict        - a forecast; only the facts so far are given
"""
import json
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .build import DB

IST = timezone(timedelta(hours=5, minutes=30))
CONF_RANK = {"High": 3, "Medium": 2, "Low": 1}

PAY_WORDS = re.compile(r"\b(salary|salaries|ctc|compensation|earns?|earning|pay ?slip|take[- ]home|net pay|gross pay|pay ?cut|how much (is|does|do) .* (paid|make))\b")
EVERYONE = re.compile(r"\b(everyone|everybody|each|every employee|all employees|individual|highest|lowest|most|least|who (is|are) paid|who earns)\b")
FLIGHT = re.compile(r"(flight risk|likely to (resign|leave|quit)|(who|which \w+|which of (them|us)).{0,40}(might|will|may|is going to|are going to|could|about to) (quit|resign|leave)|at risk of (leaving|resigning)|attrition risk (of|for|by) (a |an |the )?(person|employee|engineer|individual)|rank.{0,30}(resign|leav|quit|attrition)|who is unhappy|who else.{0,30}(leave|leaving|quit|resign|go)|(thinking|planning) (of|about|to) (leav|quit|resign)|looking (to leave|for (a|another) (new )?job)|(disgruntled|dissatisfied|unhappy|upset) (employees|people|engineers)|predict.{0,40}(who (leaves|quits|resigns)|resignations)|who leaves next|next to (leave|resign|quit))")
# Reading people's private messages to judge them (T6c): no such data exists, and I would not read individuals' messages to rank them.
SURVEIL = re.compile(r"((slack|slag|whatsapp|teams|chat|private|direct|dm|dms)\s+(messages?|chats?|logs?|dms?|history)|(their|everyone's|employees'|people's|his|her) (messages|chats|dms)|read (their|everyone's|my team's) (messages|chats|dms|emails?)|what (are|were) (they|people|employees|everyone) saying (in|on) (slack|chat|teams))")
FORECAST = re.compile(r"\b(will|would|going to|forecast|predict|projected|likely|by (december|january|february|march|next)|what does (this|that|it) do to)\b")


def parse_as_of(as_of):
    """None -> now. 'YYYY-MM-DD' -> end of that day IST (what was known by the end of day X)."""
    if as_of is None:
        return datetime.now(IST)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", as_of):
        return datetime.fromisoformat(as_of + "T23:59:59+05:30")
    return datetime.fromisoformat(as_of)


def connect(db=DB):
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    return con


def effective_manager(con, person, byid, when):
    """Manager as of `when`: Keka, overridden by confirmed effective changes. Planned changes only add a note."""
    mgr = byid.get(person["manager_id"])
    name = mgr["name"] if mgr else None
    note = None
    for c in con.execute("SELECT * FROM org_changes WHERE person_id=? ORDER BY effective_from", (person["emp_id"],)):
        if datetime.fromisoformat(c["known_at"]) > when:
            continue
        if c["status"] == "confirmed" and c["effective_from"] and datetime.fromisoformat(c["effective_from"] + "T00:00:00+05:30") <= when:
            name = byid[c["new_manager_id"]]["name"] if c["new_manager_id"] in byid else c["new_manager_label"]
            note = None
        elif c["status"] == "planned":
            note = f"Planned change, not confirmed: {c['note']}"
    return name, note


def reported_notes(con, person_id, when):
    """Notes for events reported (not yet in Keka) and released by `when`."""
    return [f"Reported, not in Keka: {e['note']}" for e in con.execute(
        "SELECT * FROM reported_events WHERE person_id=? ORDER BY known_at", (person_id,))
        if datetime.fromisoformat(e["known_at"]) <= when]


def _people_in(con, q):
    ids = set()
    for p in con.execute("SELECT emp_id, name FROM people"):
        name = p["name"].lower()
        first = name.split()[0]
        if name in q or re.search(rf"\b{re.escape(first)}\b", q):
            ids.add(p["emp_id"])
    for a in con.execute("SELECT alias, resolves_to FROM aliases WHERE kind='person'"):
        if len(a["alias"]) > 2 and re.search(rf"\b{re.escape(a['alias'].lower())}\b", q):
            ids.add(a["resolves_to"])
    if re.search(r"\b(ceo|ananya)\b", q):
        ids.add("VX001")
    return sorted(ids)


def _citations(con, claim_ids, as_of):
    out, seen = [], set()
    for cid in claim_ids:
        for e in con.execute("""SELECT e.rec_id, e.quote, s.source_id, s.known_at, s.path FROM claim_evidence e
                JOIN records r ON r.rec_id=e.rec_id JOIN sources s ON s.source_id=r.source_id WHERE e.claim_id=?""", (cid,)):
            if e["rec_id"] in seen or datetime.fromisoformat(e["known_at"]) > as_of:
                continue
            seen.add(e["rec_id"])
            out.append({"rec_id": e["rec_id"], "quote": e["quote"], "released": e["known_at"][:10]})
    return out


def _score(q, keywords):
    return sum(len(k) for k in keywords if k in q)


def _result(status, answer, confidence, citations=(), dissent=(), reasoning="", as_of=None):
    return {"status": status, "answer": answer, "confidence": confidence, "citations": list(citations),
            "dissent": list(dissent), "reasoning": reasoning, "as_of": as_of.isoformat() if as_of else None}


def ask(question, as_of=None, con=None):
    con = con or connect()
    when = parse_as_of(as_of)
    q = question.lower().replace("’", "'")

    available = lambda: [dict(r) for r in con.execute("SELECT * FROM claims")]
    claims = [c for c in available() if datetime.fromisoformat(c["known_at"]) <= when]
    people = [dict(p) for p in con.execute("SELECT * FROM people")] if con.execute(
        "SELECT 1 FROM sources WHERE known_at<=? LIMIT 1", (when.isoformat(),)).fetchone() else []
    if not claims and not people:
        return _result("unknown", "I don't know. Nothing in the data room had been released by that date.", "High", as_of=when)

    # 1. Policy: individual pay is never shown (CFO, T2).
    ppl = _people_in(con, q)
    if PAY_WORDS.search(q) and (ppl or EVERYONE.search(q)):
        return _result("refused",
                       "I won't give individual salaries or rank people by pay: the CFO said salaries must never appear in anything the CEO sees, only totals. "
                       "I can give total payroll, or flag payroll errors without amounts that reveal anyone's pay.",
                       "High", reasoning="Policy D-005 (source: T2, CFO).", as_of=when,
                       citations=_citations(con, [], when))

    # 1b. Policy: no individual flight-risk guessing (D-011). Team-level indicators only.
    if FLIGHT.search(q):
        return _result("refused",
                       "I won't name or rank individuals by how likely they are to resign: that would be a guess built from leave, survey or HR records about a person. "
                       "I can give team-level indicators instead (engagement trend, open requisitions, known notices). Ask 'how is engineering morale?'.",
                       "High", reasoning="Policy D-011.", as_of=when)

    # 1c. Policy: no reading individuals' messages to judge them (D-022). No Slack or chat export exists in the data room either.
    if SURVEIL.search(q):
        return _result("refused",
                       "I won't pull up people's private messages to see what they are saying or to rank them, and no Slack or chat export is in the data room anyway. "
                       "Reading individuals' messages to judge who might leave is surveillance, not a signal I can stand behind. "
                       "I can give team-level indicators: engagement scores by team, open requisitions, known notices.",
                       "High", reasoning="Policy D-022 (extends D-011).", as_of=when)

    # 2. Topic match.
    topics = {t["topic"]: dict(t) for t in con.execute("SELECT * FROM topics")}
    scored = sorted(((_score(q, json.loads(t["keywords"])), k) for k, t in topics.items()), reverse=True)
    best_score, best = scored[0]
    if best_score > 0:
        t = topics[best]
        tc = [c for c in claims if c["topic"] == best]
        if not tc:
            return _result("unknown", f"I don't know. The records on '{t['title']}' had not been released by {when.date()}.", "High", as_of=when)
        resolved = any(c["role"] == "resolution" for c in tc)  # a later record supplied the missing value
        if t["open_question"] and re.search(t["open_question"], q) and not resolved:
            return _result("unknown", f"I don't know. {t['unknown_reason']} What the records do say: " + " ".join(c["statement"] for c in tc if c["role"] in ("answer", "context")),
                           "High", citations=_citations(con, [c["claim_id"] for c in tc], when), as_of=when,
                           reasoning="Refusing to invent a value the sources do not contain.")
        answers = [c for c in tc if c["role"] in ("answer", "resolution")] or [c for c in tc if c["role"] == "context"]
        superseded = {c["supersedes"] for c in answers if c["supersedes"]}
        answers = [c for c in answers if c["claim_id"] not in superseded]
        context = [c for c in tc if c["role"] == "context" and c not in answers]
        dissent = [c for c in tc if c["role"] == "dissent"]
        conf = min((c["confidence"] for c in answers), key=CONF_RANK.get)
        text = " ".join(c["statement"] for c in answers + context)
        status = "answered"
        if dissent:
            status = "sources_disagree" if t["dispute"] == "unresolved" else "answered_with_conflict"
            if status == "sources_disagree":
                conf = min(conf, "Medium", key=CONF_RANK.get)
        if FORECAST.search(q):
            status = "cannot_predict"
            text = "I can't predict that. What the records show so far: " + text
            conf = "Low"
        return _result(status, text, conf,
                       _citations(con, [c["claim_id"] for c in answers + context + dissent], when),
                       [{"claim": c["statement"], "why_not_believed": c["reasoning"]} for c in dissent],
                       " ".join(c["reasoning"] for c in answers), when)

    # 3. Person lookup (system of record: Keka).
    if ppl:
        byid = {p["emp_id"]: p for p in people}
        cards, recs = [], []
        for pid in ppl:
            p = byid.get(pid)
            if not p:
                continue
            mgr, note = effective_manager(con, p, byid, when)
            cards.append(f"{p['name']} ({p['emp_id']}): {p['title']}, {p['department']}"
                         + (f", reports to {mgr}" if mgr else "") +
                         f". Joined {p['join_date']}, based in {p['location']}. Status: {p['status']}"
                         + (f" (exit {p['exit_date']})" if p["exit_date"] else "") + ".")
            recs.append(p["rec_id"])
            reports = [x["name"] for x in people if effective_manager(con, x, byid, when)[0] == p["name"]]
            if reports:
                cards[-1] += " Direct reports: " + ", ".join(reports) + "."
            if note:
                cards[-1] += " " + note
            for n in reported_notes(con, pid, when):
                cards[-1] += " " + n
        weak = [x for x in con.execute("SELECT alias, confidence FROM aliases WHERE kind='person' AND confidence!='High'")
                if len(x["alias"]) > 2 and re.search(rf"\b{re.escape(x['alias'].lower())}\b", q)]
        conf = "High"
        if weak:
            conf = min((x["confidence"] for x in weak), key=CONF_RANK.get)
            cards.append("Note: this match rests on an alias (" + ", ".join(f"'{x['alias']}' ({x['confidence']})" for x in weak) + "), not on an exact name.")
        if cards:
            return _result("answered", " ".join(cards), conf,
                           [{"rec_id": r, "quote": "", "released": "2026-11-16"} for r in recs], reasoning="Keka employee master is the system of record for roles and reporting lines.", as_of=when)

    return _result("unknown", "I don't know. Nothing in the data room released so far answers that. "
                   "I only answer from the loaded records and will not guess from general knowledge.", "High", as_of=when)


def _cite_lines(cites):
    """Quoted records one per line; bare records (computed from many rows) grouped by source."""
    out, bare = [], {}
    for c in cites:
        if c["quote"]:
            out.append(f"  - {c['rec_id']}  \"{c['quote']}\"")
        else:
            src, loc = c["rec_id"].split(":", 1)
            bare.setdefault(src, []).append(loc)
    for src, locs in bare.items():
        out.append(f"  - {src}: " + (", ".join(locs) if len(locs) <= 3 else f"{len(locs)} records ({locs[0]} ... {locs[-1]})"))
    return out


def format_result(r):
    lines = [f"[{r['status'].upper()} | confidence: {r['confidence']}]", r["answer"]]
    if r["dissent"]:
        lines.append("Conflicting sources I did not rely on:")
        lines += [f"  - {d['claim']}\n    Why: {d['why_not_believed']}" for d in r["dissent"]]
    if r["citations"]:
        lines.append("Evidence:")
        lines += _cite_lines(r["citations"])
    return "\n".join(lines)
