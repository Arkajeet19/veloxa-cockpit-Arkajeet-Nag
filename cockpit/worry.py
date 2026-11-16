"""'What should I worry about?': a ranked list, every item backed by claims and records.

score = severity (1-5, my judgement, see DECISIONS D-007) x confidence weight of the weakest supporting claim.
A risk is shown only if ALL its claims were released by the as-of date (no leakage from later days).
"""
import json
from datetime import datetime

from .ask import _citations, connect, parse_as_of
from .build import ROOT

WEIGHT = {"High": 1.0, "Medium": 0.7, "Low": 0.4}


def worry(as_of=None, con=None, limit=10):
    con = con or connect()
    when = parse_as_of(as_of)
    claims = {r["claim_id"]: dict(r) for r in con.execute("SELECT * FROM claims")}
    items = []
    for r in json.load(open(ROOT / "knowledge" / "risks.json")):
        cs = [claims.get(c) for c in r["claims"]]
        if any(c is None or datetime.fromisoformat(c["known_at"]) > when for c in cs):
            continue
        weakest = min((c["confidence"] for c in cs), key=WEIGHT.get)
        items.append({"id": r["id"], "title": r["title"], "score": round(r["severity"] * WEIGHT[weakest], 2),
                      "severity": r["severity"], "confidence": weakest, "why": r["why"],
                      "suggested_action": r["suggested_action"],
                      "citations": _citations(con, r["claims"], when)})
    items.sort(key=lambda i: (-i["score"], i["id"]))
    return items[:limit]


def format_worry(items):
    if not items:
        return "Nothing to rank: no released records support any risk yet."
    out = []
    for n, i in enumerate(items, 1):
        out.append(f"{n}. {i['title']}  [score {i['score']}, confidence {i['confidence']}]\n   Why: {i['why']}\n   Do: {i['suggested_action']}")
        out.append("   Evidence: " + ", ".join(c["rec_id"] for c in i["citations"][:6]))
    return "\n".join(out)
