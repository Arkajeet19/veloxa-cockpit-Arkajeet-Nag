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
    for t in json.load(open(ROOT / "knowledge" / "topics.json")):
        con.execute("INSERT INTO topics VALUES (?,?,?,?,?,?)",
                    (t["topic"], t["title"], json.dumps(t["keywords"]), t.get("open_question"), t.get("unknown_reason"), t["dispute"]))
        for c in t["claims"]:
            try:
                ev = [(_resolve_quote(con, _resolve_source(con, e["source"]), e["quote"]), e["quote"]) for e in c["evidence"]]
            except BuildError:
                # Evidence from a day that has not been loaded yet: claim is simply not available.
                if any(not any(s.startswith(e["source"]) for s in loaded) for e in c["evidence"]):
                    continue
                raise
            _insert_claim(con, t["topic"], c, ev)
        if t.get("derived"):
            for c in derive.DERIVERS[t["derived"]](con):
                _insert_claim(con, t["topic"], c, [(e["rec_id"], e["quote"]) for e in c["evidence"]])
    con.commit()
    return con, days


if __name__ == "__main__":
    con, days = build()
    print("built", DB, "days", days,
          {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("sources", "records", "people", "topics", "claims")})
