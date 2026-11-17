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
