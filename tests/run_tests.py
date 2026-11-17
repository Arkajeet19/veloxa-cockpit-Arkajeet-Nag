"""Run every question in tests/questions.json against the cockpit. One command: python -m cockpit test"""
import json
from pathlib import Path

from cockpit import ask as askmod, build, ingest  # noqa: F401


def check(case, res):
    errs = []
    if res["status"] not in case["status"].split("|"):
        errs.append(f"status {res['status']!r} not in {case['status']!r}")
    text = res["answer"] + " " + " ".join(d["claim"] for d in res["dissent"])
    for s in case.get("contains", []):
        if s.lower() not in res["answer"].lower():
            errs.append(f"answer missing {s!r}")
    for s in case.get("not_contains", []):
        if s.lower() in text.lower():
            errs.append(f"answer must not contain {s!r}")
    ids = " ".join(c["rec_id"] for c in res["citations"])
    for s in case.get("cites", []):
        if s not in ids:
            errs.append(f"missing citation containing {s!r}")
    if case.get("no_citations") and res["citations"]:
        errs.append("leaked citations from unreleased material")
    for s in case.get("no_citations_from", []):
        if s in ids:
            errs.append(f"leaked citation from {s!r} (released later)")
    if case.get("dissent") and not res["dissent"]:
        errs.append("expected conflicting sources to be shown")
    if "conf" in case and res["confidence"] != case["conf"]:
        errs.append(f"confidence {res['confidence']} != {case['conf']}")
    return errs


def structural_checks(con):
    errs = []
    # every claim must cite at least one record that exists
    for (cid,) in con.execute("SELECT claim_id FROM claims WHERE claim_id NOT IN (SELECT claim_id FROM claim_evidence)"):
        errs.append(f"claim {cid} has no evidence")
    for (cid,) in con.execute("SELECT DISTINCT claim_id FROM claim_evidence WHERE rec_id NOT IN (SELECT rec_id FROM records)"):
        errs.append(f"claim {cid} cites a missing record")
    # every invented persona must be logged in ASSUMPTIONS.md
    root = Path(__file__).resolve().parent.parent
    log = (root / "ASSUMPTIONS.md").read_text()
    for a in json.load(open(root / "agents" / "personas.json")):
        if a["assumption_id"] not in log:
            errs.append(f"{a['assumption_id']} not logged in ASSUMPTIONS.md")
    # every grounded persona quote must exist in the cited source
    for a in json.load(open(root / "agents" / "personas.json")):
        for g in a["grounded"]:
            srcs = [s for (s,) in con.execute("SELECT source_id FROM sources") if s.startswith(g["source"])]
            ok = any(g["quote"].replace("\u2019", "'") in t for s in srcs for (t,) in con.execute("SELECT text FROM records WHERE source_id=?", (s,)))
            if not ok:
                errs.append(f"{a['emp_id']}: grounded quote not found in {g['source']}: {g['quote']!r}")
    if con.execute("SELECT COUNT(*) FROM people WHERE is_agent=1").fetchone()[0] != 14:
        errs.append("expected exactly 14 agents")
    return errs


def run():
    con, _ = build.build()
    con.close()
    con = askmod.connect()
    cases = json.load(open(Path(__file__).parent / "questions.json"))
    failed = 0
    for c in cases:
        res = askmod.ask(c["q"], c.get("as_of"), con)
        errs = check(c, res)
        failed += bool(errs)
        print(("PASS " if not errs else "FAIL ") + c["id"] + "  " + c["q"] + (f"  [as of {c['as_of']}]" if c.get("as_of") else ""))
        for e in errs:
            print("      -", e)
    for e in structural_checks(con):
        failed += 1
        print("FAIL structural:", e)
    honest = sum(1 for c in cases if c["status"] in ("unknown", "refused", "cannot_predict") or c.get("dissent"))
    print(f"\n{len(cases) - 0} questions ({honest} test refusal/uncertainty/disagreement), {failed} failed")
    return 1 if failed else 0
