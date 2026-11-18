"""'What should I worry about?': a ranked list, every item backed by claims and records.

score = severity (1-5, my judgement, see DECISIONS D-007) x confidence weight of the weakest supporting claim.
- A risk is shown only if ALL its claims were released by the as-of date (no leakage from later days).
- A claim that a later claim supersedes is replaced by the newest released version.
- A risk may carry `updates`: richer text/severity that apply once their required claims are released.
"""
import json
from datetime import datetime

from .ask import _citations, connect, parse_as_of
from .build import ROOT

WEIGHT = {"High": 1.0, "Medium": 0.7, "Low": 0.4}


def _latest(cid, claims, when):
    """Follow supersession to the newest claim released by `when`."""
    seen = {cid}
    while True:
        nxt = [c for c in claims.values() if c["supersedes"] in seen and c["claim_id"] not in seen
               and datetime.fromisoformat(c["known_at"]) <= when]
        if not nxt:
            return cid
        cid = nxt[0]["claim_id"]
        seen.add(cid)


def worry(as_of=None, con=None, limit=10):
    con = con or connect()
    when = parse_as_of(as_of)
    claims = {r["claim_id"]: dict(r) for r in con.execute("SELECT * FROM claims")}
    released = lambda cid: cid in claims and datetime.fromisoformat(claims[cid]["known_at"]) <= when
    items = []
    for r in json.load(open(ROOT / "knowledge" / "risks.json")):
        if not all(released(c) for c in r["claims"]):
            continue
        view = dict(r)
        for u in r.get("updates", []):  # later updates override earlier text once their evidence exists
            if all(released(c) for c in u["requires"]):
                view.update({k: v for k, v in u.items() if k != "requires"})
                if "claims" not in u:  # an update may replace the claim set; otherwise it adds to it
                    view["claims"] = list(dict.fromkeys(view["claims"] + u["requires"]))
        ids = [_latest(c, claims, when) for c in view["claims"]]
        weakest = min((claims[c]["confidence"] for c in ids), key=WEIGHT.get)
        items.append({"id": r["id"], "title": view["title"], "score": round(view["severity"] * WEIGHT[weakest], 2),
                      "severity": view["severity"], "confidence": weakest, "why": view["why"],
                      "suggested_action": view["suggested_action"],
                      "citations": _citations(con, ids + [_latest(c, claims, when) for c in view.get("cite_also", []) if released(c)], when)})
    items.sort(key=lambda i: (-i["score"], i["id"]))
    return items[:limit]


def format_worry(items, top=None, total=None):
    if not items:
        return "Nothing to rank: no released records support any risk yet."
    shown = items[:top] if top else items
    out = []
    for n, i in enumerate(shown, 1):
        out.append(f"{n}. {i['title']}  [score {i['score']}, confidence {i['confidence']}]\n   Why: {i['why']}\n   Do: {i['suggested_action']}")
        out.append("   Evidence: " + ", ".join(c["rec_id"] for c in i["citations"][:6]) + (" ..." if len(i["citations"]) > 6 else ""))
    if top and len(items) > top:
        out.append(f"\n{len(items) - top} more items below the top {top}. Run 'worry' to see them.")
    return "\n".join(out)
