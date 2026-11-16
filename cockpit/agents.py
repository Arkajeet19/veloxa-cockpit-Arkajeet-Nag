"""The 14 colleagues. Facts from Keka are grounded; personal life is invented and tagged with an assumption id."""
import json
from .ask import _people_in, connect
from .build import ROOT


def load():
    return {a["emp_id"]: a for a in json.load(open(ROOT / "agents" / "personas.json"))}


def card(who, con=None):
    con = con or connect()
    personas = load()
    ids = [i for i in _people_in(con, who.lower()) if i in personas]
    if not ids:
        return f"No agent matches {who!r}. Agents: " + ", ".join(
            r["name"] for r in con.execute("SELECT name FROM people WHERE is_agent=1 ORDER BY emp_id"))
    pid = ids[0]
    p = dict(con.execute("SELECT * FROM people WHERE emp_id=?", (pid,)).fetchone())
    a = personas[pid]
    mgr = con.execute("SELECT name FROM people WHERE emp_id=?", (p["manager_id"],)).fetchone()
    lines = [f"{p['name']} - {p['title']}, {p['department']} ({p['emp_id']})",
             f"GROUNDED (Keka {p['rec_id']}): joined {p['join_date']}, {p['location']}, status {p['status']}"
             + (f", reports to {mgr['name']}" if mgr else ""),
             f"VOICE (invented): {a['voice']}"]
    for k, v in a["invented"].items():
        lines.append(f"{k.upper()} (invented, see {a['assumption_id']}): {v}")
    for g in a["grounded"]:
        lines.append(f"GROUNDED in {g['source']}: \"{g['quote']}\"")
    return "\n".join(lines)


def all_cards(con=None):
    con = con or connect()
    return "\n\n".join(card(r["name"], con) for r in con.execute("SELECT name FROM people WHERE is_agent=1 ORDER BY emp_id"))
