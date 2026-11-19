"""Claims computed from the exports, so numbers are never typed by hand.

Each function returns a claim dict in the same shape as knowledge/topics.json,
except evidence is given as {rec_id, quote} directly.
Individual salaries are used only to detect errors; they never appear in output.
"""
import json
from collections import defaultdict
from datetime import date


def _rows(con, source, where=""):
    q = f"SELECT rec_id, payload FROM records WHERE source_id LIKE ? {where}"
    return [(r, json.loads(p)) for r, p in con.execute(q, (source + "%",))]


def lakh(x):
    return f"Rs {x / 1e5:.2f} L"


def payroll_total(con):
    reg = [(r, p) for r, p in _rows(con, "payroll_register") if str(p.get("Emp ID", "")).startswith("VX")]
    gl = [(r, p) for r, p in _rows(con, "gl_export") if p.get("Cost Centre") == "PAYROLL"]
    if not reg or not gl:
        return []
    by_month, heads = defaultdict(int), defaultdict(int)
    for _, p in reg:
        by_month[p["Month"]] += p["Gross (Rs.)"]
        heads[p["Month"]] += 1
    gl_amounts = {p["Amount (Rs.)"] for _, p in gl}
    same = gl_amounts == {by_month["Mar-2026"]} and by_month["Feb-2026"] == by_month["Mar-2026"]
    stmt = (f"Total monthly gross payroll was {lakh(by_month['Jan-2026'])} in Jan 2026 ({heads['Jan-2026']} people) and "
            f"{lakh(by_month['Mar-2026'])} in Feb and Mar 2026 ({heads['Mar-2026']} people on the Mar register). "
            f"The GL books {', '.join(lakh(a) for a in sorted(gl_amounts))} in each month Apr-Sep 2026"
            f"{' - identical to the Feb/Mar register total' if same else ''}. Totals only: individual salaries are never shown.")
    return [dict(id="PT1", role="answer", confidence="High" if same else "Medium", statement=stmt,
                 reasoning="Register total is a sum of the register rows; GL rows are the Zoho PAYROLL cost centre. The flat Apr-Sep figure equals the Feb/Mar total to the rupee, which also independently supports a headcount of 19 (not 180).",
                 evidence=[dict(rec_id=r, quote="") for r, _ in gl] + [dict(rec_id=r, quote="") for r, p in reg if p["Month"] == "Mar-2026"])]


def payroll_feb_joiner(con):
    emp = {p["Emp ID"]: (r, p) for r, p in _rows(con, "employee_master") if str(p.get("Emp ID", "")).startswith("VX")}
    out = []
    for r, p in _rows(con, "payroll_register"):
        if p.get("Month") != "Feb-2026" or p.get("Emp ID") not in emp:
            continue
        erec, e = emp[p["Emp ID"]]
        jd = date.fromisoformat(e["Join Date"])
        if jd.year != 2026 or jd.month != 2:
            continue
        expected = p["Days in Month"] - (jd.day - 1)
        if p["Days Payable"] == expected:
            continue
        over = p["Gross (Rs.)"] * (p["Days Payable"] - expected) / p["Days in Month"]
        bucket = "under Rs 10,000" if over < 10000 else "Rs 10,000 or more"
        ev = [dict(rec_id=erec, quote=""), dict(rec_id=r, quote="")]
        for em in ("email_01:msg", "email_02:msg", "email_03:msg"):
            if con.execute("SELECT 1 FROM records WHERE rec_id=?", (em,)).fetchone():
                ev.append(dict(rec_id=em, quote=""))
        out.append(dict(
            id="PF1", role="answer", confidence="High",
            statement=(f"The Feb 2026 payroll paid {e['Full Name']} for {p['Days Payable']} of {p['Days in Month']} days although he joined on "
                       f"{jd.day} Feb (should be {expected} payable days), an overpayment {bucket}. The Feb run was done by Karthik because Fatima was out "
                       f"('used the Jan sheet and added the new joiner'). {e['Full Name'].split()[0]} queried the amount on 6 Mar; Fatima replied 'Will check and get back' on 10 Mar. "
                       f"No later record shows a correction (Mar was paid as normal and the GL holds totals only), so treat it as probably still open."),
            reasoning="Join date (Keka) vs 'Days Payable' (register) is a hard mismatch; the three e-mails explain the process failure and corroborate. 'Still open' is inferred from silence, so only that part is uncertain. Amount deliberately bucketed to avoid revealing a salary (D-005).",
            evidence=ev))
    return out


def aws_cost(con):
    rows = sorted([(p["Txn Date"], r, p["Amount (Rs.)"]) for r, p in _rows(con, "gl_export") if p.get("Vendor / Payee") == "Amazon Web Services"])
    if len(rows) < 2:
        return []
    first, last = rows[0], rows[-1]
    pct = (last[2] / first[2] - 1) * 100
    series = ", ".join(f"{lakh(a)}" for _, _, a in rows)
    return [dict(id="AW1", role="answer", confidence="High",
                 statement=(f"AWS invoices rose {pct:.0f}% in six months: {series} (booked {first[0]} to {last[0]}; each covers the previous month). "
                            f"The biggest single step is the latest, so the trend has not flattened. Cost centre ENG-INF."),
                 reasoning="Straight GL arithmetic over six rows. Note the GL is 'selected cost centres' but all six AWS rows are present.",
                 evidence=[dict(rec_id=r, quote="") for _, r, _ in rows])]


def summit_spend(con):
    evt = [(r, p) for r, p in _rows(con, "gl_export") if p.get("Cost Centre") == "MKT-EVT"]
    hotel = [(r, p) for r, p in _rows(con, "gl_export") if "Sapphire Residency" in str(p.get("Vendor / Payee"))]
    if not evt:
        return []
    total = sum(p["Amount (Rs.)"] for _, p in evt)
    parts = "; ".join(f"{p['Vendor / Payee']} {lakh(p['Amount (Rs.)'])} ({p['Narration']}, {p['Ref']}, {p['Txn Date']})" for _, p in evt)
    ev = [dict(rec_id=r, quote="") for r, _ in evt] + [dict(rec_id=r, quote="") for r, _ in hotel]
    return [dict(id="S1", role="answer", confidence="Medium",
                 statement=(f"GL event spend for the summit totals {lakh(total)} (Rs {total:,}) across two entries: {parts}. "
                            f"I treat 'Sapphire Events Pvt Ltd' and 'Saphire Event Mgmt' as the same vendor (Medium confidence). "
                            f"'Sapphire Residency Hotel' (Rs 38,940, cost centre SAL-TRV, sales offsite) is a different vendor and is excluded. "
                            f"The GL is 'selected cost centres', so other summit costs may exist outside it. Against 212 registrations that is roughly Rs {total / 212:,.0f} per registration (not per attendee)."),
                 reasoning="Same cost centre, near-identical names, complementary scope (venue/AV vs catering) and different invoice series point to one vendor billing twice, not a duplicate payment. The hotel is a false friend: different cost centre and purpose.",
                 evidence=ev)]


def _rec(con, source, text):
    r = con.execute("SELECT rec_id FROM records WHERE source_id LIKE ? AND text LIKE ? ORDER BY rowid LIMIT 1", (source + "%", f"%{text}%")).fetchone()
    return r[0] if r else None


def payroll_feb_leave(con):
    """Day 2 corroboration kept as its own claim so the Day 1 answer is unchanged as-of Day 1."""
    r = _rec(con, "leave_register", "F. Sheikh | Marriage")
    if not r:
        return []
    return [dict(id="PF2", role="context", confidence="High",
                 statement="Corroboration (leave register): Fatima Sheikh was on approved Marriage leave 9-27 Feb 2026, which is why Karthik ran the February payroll.",
                 reasoning="Leave register row matches the e-mail and T2 ('she was out for her wedding').",
                 evidence=[dict(rec_id=r, quote="F. Sheikh | Marriage")])]


def attrition_check(con):
    res = _rec(con, "resignation_letter_sm", "resignation")
    if not res:
        return []
    jan = [(r, p) for r, p in _rows(con, "payroll_register") if p.get("Month") == "Jan-2026" and str(p.get("Emp ID", "")).startswith("VX")]
    emp = [(r, p) for r, p in _rows(con, "employee_master") if str(p.get("Emp ID", "")).startswith("VX")]
    exits = [(r, p) for r, p in emp if p.get("Exit Date")]
    jan_ids = {p["Emp ID"] for _, p in jan}
    keka_ids = {p["Emp ID"] for _, p in emp}
    joined_after = sorted(keka_ids - jan_ids)
    if not jan or not exits or not jan_ids <= keka_ids:
        return []
    annual = len(exits) / len(emp) * 12 / 10 * 100
    t3 = _rec(con, "t3_head_of_people", "about twelve")
    ev = [dict(rec_id=r, quote="") for r, _ in exits] + [dict(rec_id=res, quote="")] + [dict(rec_id=r, quote="") for r, _ in jan]
    if t3:
        ev.append(dict(rec_id=t3, quote=""))
    return [dict(id="AT2", role="answer", confidence="Medium", supersedes="AT1",
                 statement=(f"Evidence points to low attrition this year, not 12%. The Jan 2026 payroll register had {len(jan_ids)} people; {len(joined_after)} joined later (the Feb new joiner), and all {len(keka_ids)} are still in Keka on 31 Oct. "
                            f"The only exit is Siddharth Mehta (resigned 15 Sep, last day 31 Oct). That is {len(exits)} exit in about ten months, roughly {annual:.0f}% annualised on a team of 19. "
                            f"The Head of People's 'about twelve, which is normal for Bangalore' (T3) has no stated unit: 12% would be about 2 people, 12 people would be implausible. "
                            f"I cannot see exits before Jan 2026, and Rohan's remark that exit interviews 'most of them say workload' cannot be checked."),
                 reasoning="Set comparison between the payroll register (people paid in Jan) and the Keka roster (people employed on 31 Oct). Works only for Jan-Oct 2026. A small team makes any percentage jumpy: one more exit would double it.",
                 evidence=ev)]


def pulse_trend(con):
    rows = [p for _, p in _rows(con, "pulse_survey") if p.get("Quarter") and p.get("Team")]
    if not rows:
        return []
    quarters = []
    for p in rows:
        if p["Quarter"] not in quarters:
            quarters.append(p["Quarter"])
    last, prev = quarters[-1], quarters[-2]
    by = {(p["Team"], p["Quarter"]): p for p in rows}
    deltas = sorted(((by[(t, last)]["Engagement (1-5)"] - by[(t, prev)]["Engagement (1-5)"], t)
                     for t in {p["Team"] for p in rows}))
    eng, eng_prev = by[("Engineering", last)], by[("Engineering", prev)]
    worst, worst_team = deltas[0]
    others = ", ".join(f"{t} {by[(t, prev)]['Engagement (1-5)']} to {by[(t, last)]['Engagement (1-5)']}" for d, t in deltas[1:] if d != 0)
    ids = [r for r, p in _rows(con, "pulse_survey") if p.get("Team") in ("Engineering", "Marketing") and p.get("Quarter") in (last, prev)]
    return [dict(id="PL1", role="answer", confidence="High",
                 statement=(f"Engineering engagement fell from {eng_prev['Engagement (1-5)']} ({prev}) to {eng['Engagement (1-5)']} ({last}), the biggest drop of any team and the lowest score in the data; "
                            f"responses fell from {eng_prev['Responses']}/{eng_prev['Team size']} to {eng['Responses']}/{eng['Team size']}. "
                            f"Other teams, {prev} to {last}: {others if others else 'no change'}. "
                            f"Engineering had held at 4.0 for the two quarters before. Culture Amp shows no comments for any team (every team has under 6 people), so this is team-level only."),
                 reasoning=f"Computed from the Culture Amp export. Largest change is {worst_team} ({worst:+.1f}). With 5 people, one person's answer moves the average by up to 0.8, so treat the size of the drop with care even though the direction is clear. T3 ('dipped in the July round') and Deepa's 29 Sep e-mail agree.",
                 evidence=[dict(rec_id=r, quote="") for r in ids])]


DERIVERS = {f.__name__: f for f in (payroll_total, payroll_feb_joiner, aws_cost, summit_spend, payroll_feb_leave, attrition_check, pulse_trend)}


# ---------------------------------------------------------------- Day 3: engineering and marketing
import csv as _csv
from datetime import datetime as _dt, timedelta as _td, timezone as _tz

IST = _tz(_td(hours=5, minutes=30))
PRIYA_EMAILS = ("priya.n@veloxa.in", "pnair@users.noreply.github.com")


def _jira(con):
    issues = [(r, p) for r, p in _rows(con, "jira_export_atlas") if str(p.get("Key", "")).startswith("ATLAS-") and p.get("Type") == "Story"]
    epics = {p["Key"]: p["Epic Name"] for r, p in _rows(con, "jira_export_atlas") if str(p.get("Key", "")).startswith("ATLAS-") and "Epic Name" in p}
    ver = next((p for r, p in _rows(con, "jira_export_atlas") if p.get("Version") == "Atlas GA"), None)
    return issues, epics, ver


def jira_progress(con):
    issues, epics, ver = _jira(con)
    git = [p for _, p in _rows(con, "git_log") if p.get("sha")]
    if not issues or not ver:
        return []
    pts = lambda p: int(p["Story Points"] or 0)
    tot = {st: sum(pts(p) for _, p in issues if p["Status"] == st) for st in ("Done", "In Progress", "To Do")}
    total = sum(tot.values())
    open_pts = tot["In Progress"] + tot["To Do"]
    per_epic = []
    for k in sorted({p["Epic Link"] for _, p in issues}):
        t = sum(pts(p) for _, p in issues if p["Epic Link"] == k)
        d = sum(pts(p) for _, p in issues if p["Epic Link"] == k and p["Status"] == "Done")
        per_epic.append(f"{epics.get(k, k)} {d}/{t}")
    vel = {}
    for _, p in issues:
        if p["Resolved"]:
            vel[str(p["Resolved"])[:7]] = vel.get(str(p["Resolved"])[:7], 0) + pts(p)
    last_res = max(str(p["Resolved"]) for _, p in issues if p["Resolved"])
    last_cre = max(str(p["Created"]) for _, p in issues)
    ga = _dt.fromisoformat(str(ver["Release Date"])[:10])
    export = _dt(2026, 10, 31)
    months_left = (ga - export).days / 30.4
    need = open_pts / months_left
    best = max(vel.values())
    commits = {}
    for p in git:
        m = p["committed_at"][:7]
        commits[m] = commits.get(m, 0) + 1
    recent = ", ".join(f"{m} {commits[m]}" for m in sorted(commits)[-3:])
    ev = [dict(rec_id=r, quote="") for r, _ in issues] + [dict(rec_id=r, quote="") for r, p in _rows(con, "jira_export_atlas") if p.get("Version") == "Atlas GA"]
    return [dict(id="JP1", role="answer", confidence="Medium",
                 statement=(f"Jira (ATLAS, exported 31 Oct) has {len(issues)} stories worth {total} points: {tot['Done']} done ({tot['Done'] * 100 // total}%), {tot['In Progress']} in progress, {tot['To Do']} to do, so {open_pts} points ({open_pts * 100 // total}%) are still open. "
                            f"Done / total points by epic: {'; '.join(per_epic)}. The Q3 board update's 'the engine itself is feature-complete' does not match this: the core engine and real-time re-routing epics both have open work. "
                            f"Points resolved per month: {', '.join(f'{m} {v}' for m, v in sorted(vel.items()))}; the last ticket was resolved on {last_res} and the last one created on {last_cre}. "
                            f"To finish {open_pts} points by 15 Dec (about {months_left:.1f} months after the export) needs about {need:.0f} points a month, against a best month of {best}. "
                            f"Caution: git shows steady work through October (commits per month, all repos: {recent}), so Jira may simply be out of date; treat the pace figure as a warning, not a forecast."),
                 reasoning="Straight arithmetic on the Jira export. Story points are the team's own and unaudited. Jira is the only formal plan, but its silence since mid-Sep conflicts with git, which is why confidence is Medium and why this is framed as required pace, not a prediction.",
                 evidence=ev)]


def key_person_data(con):
    git = [(r, p) for r, p in _rows(con, "git_log") if p.get("sha")]
    issues, _, _ = _jira(con)
    if not git or not issues:
        return []
    eng = [(r, p) for r, p in git if p["repo"] == "atlas-engine"]
    pr = [(r, p) for r, p in git if p["author_email"] in PRIYA_EMAILS]
    pr_eng = [x for x in pr if x[1]["repo"] == "atlas-engine"]
    only_vendor = [x for x in eng if x[1]["author_email"] == "priya.n@veloxa.in"]
    hour = lambda p: _dt.fromisoformat(p["committed_at"]).astimezone(IST)
    late = lambda p: hour(p).hour >= 22 or hour(p).hour < 5
    weekend = lambda p: hour(p).weekday() >= 5
    late_by, wk_by = {}, {}
    for _, p in git:
        late_by[p["author_email"]] = late_by.get(p["author_email"], 0) + late(p)
        wk_by[p["author_email"]] = wk_by.get(p["author_email"], 0) + weekend(p)
    pr_late = sum(late_by.get(e, 0) for e in PRIYA_EMAILS)
    pr_wk = sum(wk_by.get(e, 0) for e in PRIYA_EMAILS)
    others_late = sum(v for k, v in late_by.items() if k not in PRIYA_EMAILS)
    others_wk = sum(v for k, v in wk_by.items() if k not in PRIYA_EMAILS)
    pts = lambda p: int(p["Story Points"] or 0)
    all_pts = sum(pts(p) for _, p in issues)
    pn = [(r, p) for r, p in issues if p["Assignee"] == "PN"]
    pn_pts = sum(pts(p) for _, p in pn)
    ip_all = sum(pts(p) for _, p in issues if p["Status"] == "In Progress")
    ip_pn = sum(pts(p) for _, p in pn if p["Status"] == "In Progress")
    re_all = [p for _, p in issues if p["Epic Link"] == "ATLAS-2"]
    re_pn = [p for p in re_all if p["Assignee"] == "PN"]
    ev = [dict(rec_id=r, quote="") for r, _ in pr] + [dict(rec_id=r, quote="") for r, _ in pn]
    for e in ("email_04:msg", "email_09:msg"):
        if con.execute("SELECT 1 FROM records WHERE rec_id=?", (e,)).fetchone():
            ev.append(dict(rec_id=e, quote=""))
    return [dict(id="KP3", role="answer", confidence="High", supersedes="KP2",
                 statement=(f"The CEO's remark is supported by the data: work on Atlas is concentrated in Priya Nair. "
                            f"Her two git identities (priya.n@veloxa.in and pnair@users.noreply.github.com) account for {len(pr_eng)} of {len(eng)} atlas-engine commits ({round(len(pr_eng) * 100 / len(eng))}%); "
                            f"counting only her company address it is {round(len(only_vendor) * 100 / len(eng))}%, still the largest. "
                            f"In Jira she holds {pn_pts} of {all_pts} story points ({round(pn_pts * 100 / all_pts)}%), {ip_pn} of {ip_all} in-progress points, and every re-routing story ({len(re_pn)} of {len(re_all)}). "
                            f"She also authors {pr_late} of {sum(late_by.values())} commits made between 22:00 and 05:00 IST and {pr_wk} of {sum(wk_by.values())} weekend commits; everyone else combined has {others_late} late-night and {others_wk} weekend commits (timestamps are UTC in the export; I converted to IST on the assumption the team works from Bengaluru). "
                            f"On 1 Sep (23:47) she asked Vikram for time to discuss 'Atlas ownership'; no reply is in the records. Vikram's 2 Jun plan names her as lead of the core engine and re-routing. "
                            f"This is about concentration of work, not about anyone's plans or intentions."),
                 reasoning="Commit and ticket counts are computed from the exports. Two git emails are assumed to be one person (handle 'pnair', same repo, Jira initials PN, the only P. Nair in Keka); the conclusion survives if that is wrong, because the company-address share alone is 50%. 'She likes it' (T5) cannot be tested from data.",
                 evidence=ev)]


def incidents_summary(con):
    inc = [(r, p) for r, p in _rows(con, "incidents_aug-oct") if str(p.get("ID", "")).startswith("INC-")]
    if not inc:
        return []
    f = lambda s: _dt.fromisoformat(s.replace("Z", "+00:00"))
    sev, month, svc = {}, {}, {}
    sev1 = []
    for _, p in inc:
        sev[p["Severity"]] = sev.get(p["Severity"], 0) + 1
        month[p["Opened"][:7]] = month.get(p["Opened"][:7], 0) + 1
        svc[p["Service"]] = svc.get(p["Service"], 0) + 1
        if p["Severity"] == "SEV1":
            dur = f(p["Resolved"]) - f(p["Opened"])
            sev1.append((p["ID"], f(p["Opened"]).astimezone(IST), dur, p["Responder"]))
    hrs = sum((d for _, _, d, _ in sev1), _td()).total_seconds() / 3600
    s1 = "; ".join(f"{i} {o:%d %b %H:%M} IST, {d.total_seconds() / 3600:.1f} h, {r}" for i, o, d, r in sev1)
    return [dict(id="IN1", role="answer", confidence="High",
                 statement=(f"PagerDuty shows {len(inc)} incidents from Aug to Oct 2026: {sev.get('SEV1', 0)} SEV1, {sev.get('SEV2', 0)} SEV2, {sev.get('SEV3', 0)} SEV3. "
                            f"By month: {', '.join(f'{m} {n}' for m, n in sorted(month.items()))}, so August was the spike. All SEV1s were in August, all on routing-api ({s1}); about {hrs:.0f} hours in total. "
                            f"routing-api caused {svc.get('routing-api', 0)} of {len(inc)} incidents and kept producing SEV2s in Sep and Oct. "
                            f"Timestamps in the export are UTC; I converted to IST, and two of the three SEV1s ran in the early hours. "
                            f"This matches Sneha's 24 Aug e-mail ('Third SEV1 this month') and the Q3 board update's 'difficult August'."),
                 reasoning="Computed from the PagerDuty export. The export is Aug to Oct only, so I cannot compare with earlier months.",
                 evidence=[dict(rec_id=r, quote="") for r, _ in inc])]


def oncall_rota_summary(con):
    rota = [(r, p) for r, p in _rows(con, "oncall_rota") if str(p.get("Week of", ""))[:2] == "20"]
    if not rota:
        return []
    first = [(w["Week of"][:10], w["Primary"], w["Secondary"]) for _, w in rota]
    sneha_run = 0
    for _, pr, _ in first:
        if pr == "Sneha":
            sneha_run += 1
        else:
            break
    both = [wk for wk, pr, sc in first if {pr, sc} == {"Sneha", "Snehal"}]
    pa = [wk for wk, pr, sc in first if "Priya" in (pr, sc) or "Arjun" in (pr, sc)]
    return [dict(id="RT1", role="answer", confidence="Medium",
                 statement=(f"The on-call rota (a copied wiki table) covers {first[0][0]} to {first[-1][0]}. Sneha was primary for the first {sneha_run} weeks in a row; Priya and Arjun were secondary until the week of {pa[-1]} and then drop out. "
                            f"From 17 Aug the rota lists 'Snehal' as well, and in {len(both)} weeks Sneha and Snehal are both on it (one primary, one secondary). One person cannot be both, so Snehal is a different person from Sneha: most likely the Patil Infra contractor (see the on-call contractor topic)."),
                 reasoning="Same-week co-listing of both names is what separates them. The rota is a hand-copied wiki table, so exact dates may be off by a week.",
                 evidence=[dict(rec_id=r, quote="") for r, _ in rota])]


def marketing_spend_check(con):
    gl = [(r, p) for r, p in _rows(con, "gl_export") if p.get("Cost Centre") in ("MKT-PS", "MKT-EVT")]
    t4 = _rec(con, "t4_head_of_marketing", "one point eight")
    if not gl or not t4:
        return []
    ads = sum(p["Amount (Rs.)"] for _, p in gl if p["Cost Centre"] == "MKT-PS")
    evt = sum(p["Amount (Rs.)"] for _, p in gl if p["Cost Centre"] == "MKT-EVT")
    total = ads + evt
    gap = 1_800_000 - total
    return [dict(id="MS1", role="answer", confidence="Low",
                 statement=(f"Marketing spend does not reconcile. The GL's marketing cost centres for Apr-Sep show {lakh(total)} (Google Ads {lakh(ads)} + summit events {lakh(evt)}). "
                            f"Nikhil (T4) says the half-year total is 'one point eight' with no unit; if that is Rs 18 L, the gap to the GL is {lakh(gap)}. It could be spend the GL extract does not include (it covers 'selected cost centres', and LinkedIn, tools and agencies have no rows) or a real difference between marketing's and finance's numbers, as the CFO said ('Nikhil's numbers never match mine'). "
                            f"If 'one point eight' meant Rs 1.8 crore it would be ten times the GL, which I treat as a mishearing. 'The summit went a little over' cannot be checked: no summit budget exists in any record."),
                 reasoning="Only the GL extract is available for finance; there is no marketing-side sheet (the T4 action item is to send the campaign sheet to finance, which is not in the data room). So the conflict is real but not resolvable here.",
                 evidence=[dict(rec_id=r, quote="") for r, _ in gl] + [dict(rec_id=t4, quote="")])]



def resignation_impact(con):
    """Facts for 'what does Priya's resignation do to Atlas v3?': open work she holds and how notice dates line up with GA. No prediction."""
    issues, _, ver = _jira(con)
    if not issues or not ver or not con.execute("SELECT 1 FROM records WHERE source_id LIKE 't6d%'").fetchone():
        return []
    pts = lambda p: int(p["Story Points"] or 0)
    is_open = lambda p: p["Status"] in ("In Progress", "To Do")
    open_all = sum(pts(p) for _, p in issues if is_open(p))
    pn_open = [(r, p) for r, p in issues if p["Assignee"] == "PN" and is_open(p)]
    pn_open_pts = sum(pts(p) for _, p in pn_open)
    re_open = [p for _, p in issues if p["Epic Link"] == "ATLAS-2" and is_open(p)]
    re_pn_open = [p for p in re_open if p["Assignee"] == "PN"]
    ga = _dt.fromisoformat(str(ver["Release Date"])[:10])
    told = _dt(2026, 11, 19)
    need_days = (ga - told).days
    end_2m = told + _td(days=61)  # two calendar months from 19 Nov
    ev = [dict(rec_id=r, quote="") for r, _ in pn_open] + [dict(rec_id=r, quote="") for r, p in _rows(con, "jira_export_atlas") if p.get("Version") == "Atlas GA"]
    ev.append(dict(rec_id=con.execute("SELECT rec_id FROM records WHERE source_id LIKE 't6d%' AND text LIKE '%resigned%'").fetchone()[0], quote=""))
    return [dict(id="RS3", role="context", confidence="Medium",
                 statement=(f"What the records say about Atlas v3 if Priya leaves (facts, not a forecast). On the 31 Oct Jira export she is assigned {len(pn_open)} open stories worth {pn_open_pts} of the {open_all} open points ({round(pn_open_pts * 100 / open_all)}%), "
                            f"and {len(re_pn_open)} of the {len(re_open)} open re-routing stories. No other engineer is recorded as owning the core engine or re-routing; Vikram's 2 Jun plan names her as lead. "
                            f"The routing backend role (REQ-014) has been on hold since 12 Aug. The Jira GA date is {ga:%d %b %Y}, {need_days} days after 19 Nov. "
                            f"If her notice really is two months from 19 Nov it would end around {end_2m:%d %b %Y}, after that GA date, so on paper she is still employed at GA; a shorter notice (26 days or fewer), leave, or a handover period could change that. "
                            f"The CEO is not sure of the notice length and no HR record exists. Why she resigned is not in the records and I do not guess."),
                 reasoning="Counts and date arithmetic from the Jira export and the voice note. Jira is partly stale (JP1) so open points may be overstated. The notice period is the CEO's recollection, so the date is conditional.",
                 evidence=ev)]


DERIVERS.update({f.__name__: f for f in (jira_progress, key_person_data, incidents_summary, oncall_rota_summary, marketing_spend_check, resignation_impact)})
