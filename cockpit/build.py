"""Build build/veloxa.db from data/raw + knowledge/ + agents/. Deterministic and idempotent."""
import json
import sqlite3
from pathlib import Path

from . import derive, ingest

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "build" / "veloxa.db"


class BuildError(Exception):
    pass


def _resolve_source(con, prefix):
    hits = [r[0] for r in con.execute("SELECT source_id FROM sources WHERE source_id LIKE ?", (prefix + "%",))]
    if len(hits) != 1:
        raise BuildError(f"source prefix {prefix!r} matched {hits}")
    return hits[0]


def _resolve_quote(con, source_id, quote):
    q = ingest.norm(quote)
    for rec_id, text in con.execute("SELECT rec_id, text FROM records WHERE source_id=? ORDER BY rowid", (source_id,)):
        if q in text:
            return rec_id
    raise BuildError(f"quote not found in {source_id}: {quote!r}")


def _loaded(e, loaded):
    if "rec_id" in e:
        return e["rec_id"].split(":")[0] in loaded
    return any(s.startswith(e["source"]) for s in loaded)


def _evidence(con, e):
    if "rec_id" in e:  # direct pointer, used when quoting would expose a salary
        if not con.execute("SELECT 1 FROM records WHERE rec_id=?", (e["rec_id"],)).fetchone():
            raise BuildError(f"missing record {e['rec_id']}")
        return e["rec_id"], e.get("quote", "")
    return _resolve_quote(con, _resolve_source(con, e["source"]), e["quote"]), e["quote"]


def people_aliases(con):
    """Leave register style names: 'A. Das' -> person, plus approver initials."""
    out = []
    for emp_id, name in con.execute("SELECT emp_id, name FROM people"):
        parts = name.split()
        out.append((f"{parts[0][0]}. {parts[-1]}", "person", emp_id, "High", "Leave register / initial-surname style"))
        out.append(("".join(p[0] for p in parts), "person", emp_id, "High" if emp_id in ("VX001","VX003","VX004","VX005","VX006") else "Medium", "Approver initials in the leave register"))
    return out


def load_org_changes(con):
    """Planned and confirmed reporting-line changes, effective-dated. Keka stays the truth until a change is `confirmed`."""
    f = ROOT / "knowledge" / "org_changes.json"
    if not f.exists():
        return
    for c in json.load(open(f)):
        try:
            rec_id, _ = _evidence(con, c["evidence"])
        except BuildError:
            continue  # its source has not been released yet
        known = con.execute("SELECT known_at FROM sources WHERE source_id=?", (rec_id.split(":")[0],)).fetchone()[0]
        con.execute("INSERT INTO org_changes VALUES (?,?,?,?,?,?,?,?,?)", (c["id"], c["person"], c.get("new_manager"), c["new_manager_label"],
                    c["status"], c.get("effective_from"), c["note"], rec_id, known))


def load_reported_events(con):
    """Events someone reports (a resignation) before any HR record exists. They add a note; they never change Keka's status."""
    f = ROOT / "knowledge" / "reported_events.json"
    if not f.exists():
        return
    for e in json.load(open(f)):
        try:
            rec_id, _ = _evidence(con, e["evidence"])
        except BuildError:
            continue  # its source has not been released yet
        known = con.execute("SELECT known_at FROM sources WHERE source_id=?", (rec_id.split(":")[0],)).fetchone()[0]
        con.execute("INSERT INTO reported_events VALUES (?,?,?,?,?,?)", (e["id"], e["person"], e["kind"], e["note"], rec_id, known))


def _insert_claim(con, topic, c, evidence):
    kn = max(con.execute("SELECT known_at FROM sources WHERE source_id=?", (r.split(":")[0],)).fetchone()[0] for r, _ in evidence)
    con.execute("INSERT INTO claims VALUES (?,?,?,?,?,?,?,?)",
                (c["id"], topic, c["role"], c["statement"], c["confidence"], c["reasoning"], kn, c.get("supersedes")))
    for rec_id, quote in evidence:
        con.execute("INSERT INTO claim_evidence VALUES (?,?,?)", (c["id"], rec_id, quote))


def build(raw_dir=None, db=DB):
    raw_dir = Path(raw_dir or ROOT / "data" / "raw")
    db.parent.mkdir(parents=True, exist_ok=True)
    if db.exists():
        db.unlink()
    con = sqlite3.connect(db)
    con.executescript(ingest.SCHEMA)
    days = ingest.ingest(raw_dir, con)
    ingest.load_people(con)
    for a in json.load(open(ROOT / "knowledge" / "aliases.json")):
        con.execute("INSERT INTO aliases VALUES (?,?,?,?,?)", (a["alias"], a["kind"], a["resolves_to"], a["confidence"], a["note"]))
    loaded = {r[0] for r in con.execute("SELECT source_id FROM sources")}
    for p in people_aliases(con):
        con.execute("INSERT INTO aliases VALUES (?,?,?,?,?)", p)
    loaded = {r[0] for r in con.execute("SELECT source_id FROM sources")}
    # topics.json first, then topics_day*.json: later files add claims (and may add new topics)
    for kf in sorted((ROOT / "knowledge").glob("topics*.json")):
        for t in json.load(open(kf)):
            if not con.execute("SELECT 1 FROM topics WHERE topic=?", (t["topic"],)).fetchone():
                con.execute("INSERT INTO topics VALUES (?,?,?,?,?,?)",
                            (t["topic"], t["title"], json.dumps(t["keywords"]), t.get("open_question"), t.get("unknown_reason"), t["dispute"]))
            if t.get("keywords") and con.execute("SELECT 1 FROM topics WHERE topic=?", (t["topic"],)).fetchone():
                have = json.loads(con.execute("SELECT keywords FROM topics WHERE topic=?", (t["topic"],)).fetchone()[0])
                con.execute("UPDATE topics SET keywords=? WHERE topic=?", (json.dumps(have + [k for k in t["keywords"] if k not in have]), t["topic"]))
            if t.get("set_dispute"):
                con.execute("UPDATE topics SET dispute=? WHERE topic=?", (t["set_dispute"], t["topic"]))
            if t.get("remove_keywords"):
                have = json.loads(con.execute("SELECT keywords FROM topics WHERE topic=?", (t["topic"],)).fetchone()[0])
                con.execute("UPDATE topics SET keywords=? WHERE topic=?", (json.dumps([k for k in have if k not in t["remove_keywords"]]), t["topic"]))
            for c in t["claims"]:
                try:
                    ev = [_evidence(con, e) for e in c["evidence"]]
                except BuildError:
                    # Evidence from a day that has not been loaded yet: claim is simply not available.
                    if any(not _loaded(e, loaded) for e in c["evidence"]):
                        continue
                    raise
                _insert_claim(con, t["topic"], c, ev)
            if t.get("derived"):
                for c in derive.DERIVERS[t["derived"]](con):
                    _insert_claim(con, t["topic"], c, [(e["rec_id"], e["quote"]) for e in c["evidence"]])
    load_org_changes(con)
    load_reported_events(con)
    con.commit()
    return con, days


if __name__ == "__main__":
    con, days = build()
    print("built", DB, "days", days,
          {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("sources", "records", "people", "topics", "claims")})
