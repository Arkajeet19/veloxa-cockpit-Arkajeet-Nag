"""Stretch goal: the 14 agents keep producing plausible activity after the data ends (31 Oct 2026).

Rules, so the output can never be mistaken for evidence (DECISIONS D-025):
1. Simulated events live in their own table (`simulated_events`). The cockpit's ask and worry views never read it.
2. Every event is labelled SIMULATED and names the claims it is based on (`based_on`); the tests check those exist.
3. It is rule-based and seeded: same seed, same events. No model, no randomness beyond random.Random(seed).
4. Hard consistency rules, all tested: nobody acts after their exit date (Siddharth: none after 31 Oct); Priya does no new feature
   work after the 19 Nov resignation report (handover only); nothing says Atlas shipped; no pay figures; no guesses about why anyone leaves;
   working days only.
"""
import random
from datetime import date, timedelta

from .ask import connect

RESIGNATION = date(2026, 11, 19)  # CEO's T6d report. Her last day is unknown (A-031), so she is never simulated as gone.

# person -> list of (kind, text, based_on claim ids, phase) ; phase: any | before_resignation | after_resignation
PLAN = {
    "VX007": [("commit", "atlas-engine: re-routing fix pushed to the core engine branch", ["KP3", "JP1"], "before_resignation"),
              ("commit", "atlas-engine: unit tests for the re-routing cache", ["KP3"], "before_resignation"),
              ("commit", "atlas-engine: refactors the route-scoring function", ["KP3", "JP1"], "before_resignation"),
              ("jira", "moves a re-routing story to In Progress", ["KP3", "JP1"], "before_resignation"),
              ("handover", "writes handover notes for the re-routing module", ["RS1", "RS3"], "after_resignation"),
              ("handover", "walks Rahul through the core engine code paths", ["RS3", "PR1"], "after_resignation")],
    "VX004": [("meeting", "reviews open Atlas stories with the team", ["JP1", "AG2"], "any"),
              ("email", "chases the plan for the 15 Dec GA with the team", ["AG2", "AG3"], "any")],
    "VX018": [("commit", "atlas-api: endpoint changes for the routing service", ["JP1"], "any"),
              ("jira", "moves an API story to In Progress", ["JP1"], "any")],
    "VX009": [("commit", "atlas-ui: dashboard screen fixes", ["JP1"], "any"),
              ("jira", "updates a UI story and notes a blocker on the API", ["JP1"], "any")],
    "VX012": [("jira", "works on a hardening ticket between pages", ["JP1", "IN1"], "any"),
              ("oncall", "hands the on-call week to the contractor", ["OC2", "RT1"], "any")],
    "VX003": [("email", "asks Nikhil for the campaign sheet again", ["MS1", "MS2"], "any"),
              ("meeting", "reviews cash and the burn definition with Karthik", ["B1", "B2"], "any")],
    "VX010": [("sheet", "updates the runway forecast", ["B1"], "any"),
              ("email", "asks Fatima to reconcile a ledger line", ["PT1"], "any")],
    "VX014": [("voucher", "enters GL vouchers for the month", ["PT1"], "any"),
              ("payroll", "prepares the payroll inputs and double-checks proration for joiners", ["PF1", "PF2"], "any")],
    "VX005": [("meeting", "checks in on the engineering team after the pulse drop", ["PL1"], "any"),
              ("email", "reminds Vikram about the 1:1s", ["PL1"], "any")],
    "VX015": [("email", "updates the candidates for the paused backend roles", ["HB2"], "any"),
              ("interview", "runs a screening call for the product-marketing backfill", ["MD2"], "any")],
    "VX017": [("task", "plans the office space and equipment for the month", ["HC1"], "any")],
    "VX006": [("meeting", "reviews the summit leads with Aisha", ["MS2"], "any"),
              ("email", "asks engineering for a launch date", ["LK1"], "any")],
    "VX011": [("report", "pulls the Google Ads cost report", ["MS1"], "any"),
              ("task", "adjusts the LinkedIn campaign budget", ["MS1"], "any")],
}

# dated events that follow from facts already in the data
FIXED = [
    ("2026-11-20", "VX004", "email", "asks HR for the notice terms and a handover plan for the core engine", ["RS1", "RS4"]),
    ("2026-11-20", "VX005", "task", "checks the notice clause in the contract on file", ["RS5"]),
    ("2026-11-30", "VX014", "payroll", "runs the November payroll", ["PT1", "PF2"]),
    ("2026-12-01", "VX003", "meeting", "reviews the November AWS bill against the trend", ["AW1"]),
    ("2026-12-15", "VX004", "meeting", "reviews GA readiness against the Jira target date", ["AG2", "JP1"]),
]


def _working_days(start, end):
    d = start
    while d <= end:
        if d.weekday() < 5:
            yield d
        d += timedelta(days=1)


def simulate(start="2026-11-02", end="2026-12-15", seed=7, con=None):
    con = con or connect()
    start, end = date.fromisoformat(start), date.fromisoformat(end)
    people = {r["emp_id"]: dict(r) for r in con.execute("SELECT * FROM people WHERE is_agent=1")}
    rng = random.Random(seed)
    events, used = [], {}
    for pid, plan in PLAN.items():
        p = people[pid]
        exit_ = date.fromisoformat(p["exit_date"]) if p["exit_date"] else None
        for d in _working_days(start, end):
            if exit_ and d > exit_:
                break
            if rng.random() > 0.4:  # about two events per person per week
                continue
            ok = [t for t in plan if t[3] == "any"
                  or (t[3] == "before_resignation" and d < RESIGNATION)
                  or (t[3] == "after_resignation" and d > RESIGNATION)]
            if ok:
                # take the least recently used template, so the same line does not repeat back to back
                kind, text, based_on, _ = min(ok, key=lambda t: (used.get((pid, t[1]), -1), rng.random()))
                used[(pid, text)] = d.toordinal()
                events.append((d.isoformat(), pid, kind, text, based_on))
    for d, pid, kind, text, based_on in FIXED:
        if start <= date.fromisoformat(d) <= end:
            events.append((d, pid, kind, text, based_on))
    events.sort(key=lambda e: (e[0], e[1], e[2]))
    return events


def store(con, events):
    con.execute("DROP TABLE IF EXISTS simulated_events")
    con.execute("CREATE TABLE simulated_events(sim_id TEXT PRIMARY KEY, sim_date TEXT, person_id TEXT, kind TEXT, text TEXT, based_on TEXT, label TEXT)")
    for n, (d, pid, kind, text, based_on) in enumerate(events, 1):
        con.execute("INSERT INTO simulated_events VALUES (?,?,?,?,?,?,?)",
                    (f"SIM-{n:03d}", d, pid, kind, text, ",".join(based_on), "SIMULATED"))
    con.commit()


def format_events(events, people, who=None):
    out = ["SIMULATED activity (not evidence; the cockpit never cites it). Based on claims in the data room as of 20 Nov."]
    for d, pid, kind, text, based_on in events:
        name = people[pid]["name"]
        if who and who.lower() not in name.lower():
            continue
        out.append(f"{d}  [{kind}]  {name} {text}   (based on {', '.join(based_on)})")
    return "\n".join(out)


def run(until="2026-12-15", who=None, seed=7):
    con = connect()
    people = {r["emp_id"]: dict(r) for r in con.execute("SELECT * FROM people")}
    events = simulate(end=until, seed=seed, con=con)
    return format_events(events, people, who)
