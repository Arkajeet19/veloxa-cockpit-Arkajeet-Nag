"""Load every released day-folder under data/raw into SQLite with provenance.

Every spreadsheet row, PDF page, e-mail and transcript paragraph becomes one
`records` row with a stable id `<source_id>:<locator>`. Each source carries the
`known_at` timestamp of the day-folder it was released in, which is what makes
point-in-time ("what did we know on date X") answers possible.
"""
import csv
import email
import json
import re
from datetime import datetime
from email import policy
from pathlib import Path

import docx
import openpyxl
import pypdf

# Release times from the hackathon e-mail (all IST).
RELEASE = {
    1: "2026-11-16T10:00:00+05:30",
    2: "2026-11-17T10:00:00+05:30",
    3: "2026-11-18T10:00:00+05:30",
    4: "2026-11-19T10:00:00+05:30",
}

SCHEMA = """
CREATE TABLE sources(source_id TEXT PRIMARY KEY, kind TEXT, path TEXT, day INT, known_at TEXT);
CREATE TABLE records(rec_id TEXT PRIMARY KEY, source_id TEXT, locator TEXT, text TEXT, payload TEXT);
CREATE TABLE people(emp_id TEXT PRIMARY KEY, name TEXT, email TEXT, department TEXT, title TEXT,
    manager_id TEXT, join_date TEXT, location TEXT, status TEXT, exit_date TEXT, rec_id TEXT, is_agent INT);
CREATE TABLE aliases(alias TEXT, kind TEXT, resolves_to TEXT, confidence TEXT, note TEXT);
CREATE TABLE topics(topic TEXT PRIMARY KEY, title TEXT, keywords TEXT, open_question TEXT,
    unknown_reason TEXT, dispute TEXT);
CREATE TABLE claims(claim_id TEXT PRIMARY KEY, topic TEXT, role TEXT, statement TEXT,
    confidence TEXT, reasoning TEXT, known_at TEXT, supersedes TEXT);
CREATE TABLE claim_evidence(claim_id TEXT, rec_id TEXT, quote TEXT);
CREATE TABLE org_changes(change_id TEXT PRIMARY KEY, person_id TEXT, new_manager_id TEXT, new_manager_label TEXT, status TEXT, effective_from TEXT, note TEXT, rec_id TEXT, known_at TEXT);
"""


def norm(s):
    """Collapse whitespace so quotes survive PDF/e-mail line wrapping."""
    return re.sub(r"\s+", " ", str(s)).strip()


def _xlsx(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    multi = len(wb.sheetnames) > 1
    for ws in wb:
        pre = f"{ws.title}!" if multi else ""
        rows = [r for r in ws.iter_rows(values_only=True)]
        header_i = next(i for i, r in enumerate(rows) if sum(c is not None for c in r) >= 2)
        header = [str(c) for c in rows[header_i]]
        for i, r in enumerate(rows, start=1):
            if all(c is None for c in r):
                continue
            if i - 1 < header_i:  # title / note rows above the header
                yield f"{pre}r{i}", norm(r[0]), {"title": r[0]}
            elif i - 1 > header_i:
                cells = ["" if c is None else str(c) for c in r]
                yield f"{pre}r{i}", " | ".join(cells), dict(zip(header, r))


def _csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f), start=2):
            yield f"r{i}", " | ".join(row.values()), row


def _docx(path):
    d = docx.Document(path)
    n = 0
    for p in d.paragraphs:
        if p.text.strip():
            n += 1
            yield f"p{n}", norm(p.text), {}
    for ti, t in enumerate(d.tables, start=1):
        for ri, row in enumerate(t.rows, start=1):
            yield f"t{ti}r{ri}", " | ".join(norm(c.text) for c in row.cells), {}


def _pdf(path):
    for i, page in enumerate(pypdf.PdfReader(path).pages, start=1):
        yield f"pg{i}", norm(page.extract_text() or ""), {}


def _eml(path):
    m = email.message_from_binary_file(open(path, "rb"), policy=policy.default)
    body = m.get_body(preferencelist=("plain",)).get_content()
    text = norm(f"From: {m['From']} To: {m['To']} Subject: {m['Subject']} Date: {m['Date']} {body}")
    yield "msg", text, {"from": str(m["From"]), "to": str(m["To"]), "subject": str(m["Subject"]), "date": str(m["Date"])}


def _txt(path):
    for i, line in enumerate(open(path, encoding="utf-8"), start=1):
        if line.strip():
            yield f"l{i}", norm(line), {}


READERS = {".xlsx": _xlsx, ".csv": _csv, ".docx": _docx, ".pdf": _pdf, ".eml": _eml, ".txt": _txt}


def source_id_for(path: Path):
    stem = path.stem.lower()
    return f"email_{stem}" if path.suffix == ".eml" else stem


def ingest(raw_dir: Path, con):
    """Ingest all Day* folders found. Returns list of day numbers loaded."""
    days = []
    for day_dir in sorted(raw_dir.glob("Day*")):
        day = int(re.match(r"Day(\d)", day_dir.name).group(1))
        days.append(day)
        for f in sorted(p for p in day_dir.rglob("*") if p.is_file()):
            if f.suffix not in READERS or "templates" in f.parts:
                continue
            sid = source_id_for(f)
            kind = f.parent.name if f.parent.name != day_dir.name else "root"
            con.execute("INSERT INTO sources VALUES (?,?,?,?,?)",
                        (sid, kind, str(f.relative_to(raw_dir)), day, RELEASE[day]))
            for loc, text, payload in READERS[f.suffix](f):
                con.execute("INSERT INTO records VALUES (?,?,?,?,?)",
                            (f"{sid}:{loc}", sid, loc, text, json.dumps(payload, default=str)))
    return days


def load_people(con):
    """Employee_Master rows -> people table (Keka is the system of record for who exists)."""
    rows = con.execute("SELECT rec_id, payload FROM records WHERE source_id='employee_master' AND payload LIKE '%Emp ID%'").fetchall()
    agents = json.load(open(Path(__file__).parent.parent / "agents" / "personas.json"))
    agent_ids = {a["emp_id"] for a in agents}
    for rec_id, payload in rows:
        p = json.loads(payload)
        if not str(p.get("Emp ID", "")).startswith("VX"):
            continue
        con.execute("INSERT INTO people VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (
            p["Emp ID"], p["Full Name"], p["Work Email"], p["Department"], p["Title"], p["Manager ID"],
            p["Join Date"], p["Location"], p["Status"], p["Exit Date"], rec_id, int(p["Emp ID"] in agent_ids)))


def known_at_dt(s):
    return datetime.fromisoformat(s)
