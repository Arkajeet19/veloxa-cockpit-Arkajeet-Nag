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
FORECAST = re.compile(r"\b(will|would|going to|forecast|predict|projected|likely|by (december|january|february|march|next))\b")


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

    # 2. Topic match.
    topics = {t["topic"]: dict(t) for t in con.execute("SELECT * FROM topics")}
    scored = sorted(((_score(q, json.loads(t["keywords"])), k) for k, t in topics.items()), reverse=True)
    best_score, best = scored[0]
    if best_score > 0:
        t = topics[best]
        tc = [c for c in claims if c["topic"] == best]
        if not tc:
            return _result("unknown", f"I don't know. The records on '{t['title']}' had not been released by {when.date()}.", "High", as_of=when)
        if t["open_question"] and re.search(t["open_question"], q):
            return _result("unknown", f"I don't know. {t['unknown_reason']} What the records do say: " + " ".join(c["statement"] for c in tc if c["role"] in ("answer", "context")),
                           "High", citations=_citations(con, [c["claim_id"] for c in tc], when), as_of=when,
                           reasoning="Refusing to invent a value the sources do not contain.")
        answers = [c for c in tc if c["role"] == "answer"] or [c for c in tc if c["role"] == "context"]
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
            mgr = byid.get(p["manager_id"])
            cards.append(f"{p['name']} ({p['emp_id']}): {p['title']}, {p['department']}"
                         + (f", reports to {mgr['name']}" if mgr else "") +
                         f". Joined {p['join_date']}, based in {p['location']}. Status: {p['status']}"
                         + (f" (exit {p['exit_date']})" if p["exit_date"] else "") + ".")
            recs.append(p["rec_id"])
            reports = [x["name"] for x in people if x["manager_id"] == pid]
            if reports:
                cards[-1] += " Direct reports: " + ", ".join(reports) + "."
        if cards:
            return _result("answered", " ".join(cards), "High",
                           [{"rec_id": r, "quote": "", "released": "2026-11-16"} for r in recs], reasoning="Keka employee master is the system of record for roles and reporting lines.", as_of=when)

    return _result("unknown", "I don't know. Nothing in the data room released so far answers that. "
                   "I only answer from the loaded records and will not guess from general knowledge.", "High", as_of=when)


def format_result(r):
    lines = [f"[{r['status'].upper()} | confidence: {r['confidence']}]", r["answer"]]
    if r["dissent"]:
        lines.append("Conflicting sources I did not rely on:")
        lines += [f"  - {d['claim']}\n    Why: {d['why_not_believed']}" for d in r["dissent"]]
    if r["citations"]:
        lines.append("Evidence:")
        for c in r["citations"][:12]:
            lines.append(f"  - {c['rec_id']}" + (f"  \"{c['quote']}\"" if c["quote"] else ""))
        if len(r["citations"]) > 12:
            lines.append(f"  ... and {len(r['citations']) - 12} more records")
    return "\n".join(lines)
