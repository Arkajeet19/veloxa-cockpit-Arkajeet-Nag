# TRANSCRIPT_NOTES

> **Status: DRAFT proposals for owner review.** Each entry records the evidence and the conclusion I currently lean towards. The hackathon rules require that *I* own every conflict resolution, so each entry has a `Reviewed` box to be ticked only after I have re-read the evidence and rewritten the reasoning in my own words.

Format: ID | what looks wrong | evidence | conclusion | confidence | Reviewed.

## Day 1 (T1 CEO kickoff, T2 CFO call, brief, README, board updates, exports)

**N-01 Company size.** T1 says "roughly eighteen people ('one-eighty, give or take')"; brief says 180-person. Keka lists 19, both board updates say Team 19, the Mar payroll register has 19 people, and payroll totals Rs 31.75 L/month (about Rs 1.7 L per head; for 180 it would be Rs 17k each). *Conclusion:* 19; the 180 is a misstatement, and "eighteen" is the summariser trying to reconcile with the audio. T1 is internally inconsistent, which is itself a sign of a bad transcript. High. Reviewed: [x]

**N-02 ARR.** T1: "forty-two crore, maybe forty-five now". T2: start of year "forty-eight". Board: Rs 5.8 Cr (Jun) and Rs 6.1 Cr (Sep). *Conclusion:* believe the board numbers. Three spoken figures cannot be reconciled with one another or with the board; if they are 4.2/4.5/4.8 Cr then ARR would have grown 4.8 -> 5.8 in one quarter, which is large but the board is the only written source. I report `sources_disagree` rather than pretending it is solved. Medium. Reviewed: [x]

**N-03 Burn.** T1 "around two point two (unit not stated)"; T2 "two point two lakhs a month, sometimes two point five". Board: Rs 46 L, then Rs 44 L. GL payroll alone is Rs 31.75 L/month. *Conclusion:* "2.2 lakh" is impossible; two speakers saying 2.2 suggests a systematic unit error (maybe crore per year/quarter, or "forty-two" heard as "two"). Board figure believed, Medium; flagged unresolved. Also noted: burn 44 L vs ARR 6.1 Cr (51 L/mo revenue) vs 13-month runway does not reconcile under either gross or net definitions. Reviewed: [x]

**N-04 Tool names.** "Jeera" = Jira, "Git Hub" = GitHub, "Cult Amp" = Culture Amp, "Joho books" = Zoho Books, "Kayka" = Keka, "hub sport" = HubSpot (probable), "slag channel" = Slack (probable). T1 hedges "Linear, I think, or they moved back to the Jeera board"; the README lists Jira (ATLAS) as the engineering export. *Conclusion:* the README and export headers beat spoken names. Linear is not supported by any record. High (Slack/HubSpot Medium). Reviewed: [x]

**N-05 Names.** "Pria" -> Priya Nair (only Priya); "Kartik" -> Karthik Subramanian; "Fatima Shaikh" -> Fatima Sheikh (Keka, e-mails); "Vicky" -> probably Vikram Menon (Low). Processed/Entered By "FS" = Fatima, "KS" = Karthik. Reviewed: [x]

**N-06 Fiscal year.** T2 "FY twenty-six (maybe twenty-seven)". April-March year puts Nov 2026 in FY27. The payroll sheet called "Payroll Q4" (Jan-Mar 2026) is Q4 of FY26. Medium. Reviewed: [x]

**N-07 Books migration.** T2: moved from Tally to Zoho "Jan or Feb", older numbers "may not match". The only GL given is Apr-Sep 2026 (all Zoho), so I cannot test the mismatch. Jan-Mar payroll comes from a pre-Keka workbook; its total matches Apr-Sep GL payroll to the rupee, so no break there. Reviewed: [x]

**N-08 "The two backend roles".** Mentioned in passing in T2. GL: Rs 1.77 L = 50% advance for a 2-role search (30 Jun). Board Q2 plans two backend hires; Q3 says hiring paused; Keka shows no joiner after 3 Feb (Rahul Verma). *Conclusion:* not filled as of 31 Oct. Medium (absence of evidence; contractors not in Keka). Reviewed: [x]

**N-09 Summit vendors.** "Sapphire Events Pvt Ltd" (INV-2291) and "Saphire Event Mgmt" (SEM-0087) are both MKT-EVT. "Sapphire Residency Hotel" is SAL-TRV, sales offsite. *Conclusion:* first two are one vendor (Medium); the hotel is a false friend and is excluded. T2 "Nikhil's numbers never match mine" cannot be tested until marketing's own numbers arrive. Reviewed: [x]

**N-10 Payroll anomaly (not a mishearing, a record error).** Rahul Verma joined 3 Feb but the Feb register shows 28/28 days payable at the full amount. E-mails 01-03 explain it (Karthik covered while Fatima was out, reused the Jan sheet; Rahul queried on 6 Mar; Fatima: "Will check and get back" on 10 Mar). Not a quirk: a real error. Reviewed: [x]

**N-11 Things that look wrong but are not.** (a) Rahul is absent from the Jan register: he joined in Feb. (b) Siddharth is "Notice period" with exit date equal to the export date: consistent with exiting that day. (c) GL vouchers out of date order (JV-0904 dated 3 Sep before JV-0903 dated 4 Sep): voucher number sequence is not chronological, not an error. (d) AWS booked "previous month": txn date is a month after the service month. (e) GL says "selected cost centres": absence of a cost is not proof of no cost. Reviewed: [x]

**N-12 Brief vs HR e-mail.** Brief: 10 working days, live sessions on days 2/4/8, drops on days 1/3/4. E-mail: 5 days, no live sessions, folders on days 1/2/3/4. Latest instruction wins (A-012). Reviewed: [x]

**N-13 Board "number by March".** Speaker 2 unidentified, referent unclear. Cockpit says "I don't know". Reviewed: [x]

## Day 2 (T3 Head of People call, T6a voice note, leave register, hiring tracker, pulse survey, resignation letter, e-mails 06, 07, 10, 11)


**N-14 "Twenty-two open roles in April", "lost six of them in August".** T3 (Rohan). The hiring tracker has six requisitions in total; at most one (REQ-011, closed 2 Apr) was open in April; REQ-014/015 opened 18 May. 22 is impossible for a 19-person company. *Conclusion:* misheard or a different measure; tracker believed. "Offer acceptance fifty-something" cannot be checked (one accepted offer recorded). High that 22 is wrong; unknown what was meant. Reviewed: [x]

**N-15 "The two backend roles" are now identified.** REQ-014 (Routing) and REQ-015 (Platform), opened 18 May under Vikram, paused by Meera on 12 Aug (e-mail 06, cc Ananya and Rohan); Vikram: "We'll absorb it" (e-mail 07). Tracker agrees on 12 Aug. This confirms my Day 1 inference that neither was filled and replaces it (HB2 supersedes HB1). High. Reviewed: [x]

**N-16 Board: "Hiring is paused" vs tracker.** Tracker has two other requisitions Open (REQ-016 PMM backfill from 17 Sep, REQ-017 Support Associate from 1 Oct). *Conclusion:* the board sentence over-generalises one decision (pausing the two backend roles). Tracker believed. High. Reviewed: [x]

**N-17 Attrition "about twelve".** T3, unit unclear. Jan 2026 payroll had 18 people, one joined in Feb, all 19 are still in Keka on 31 Oct, and only Siddharth is leaving: 1 exit in ~10 months, about 6% annualised. 12% would be ~2 people; 12 people is implausible. *Conclusion:* attrition is not high in the data I can see; I cannot see before Jan 2026, and one more exit would double the percentage. Medium. Supersedes Day 1 AT1. Reviewed: [x]

**N-18 Comment visibility: T3 vs e-mail 11 vs export.** T3: Deepa wants Ananya to see survey comments directly. E-mail 11 (later, her own words): "the team is too small for me to share comments". Export: "Not shown: team smaller than 6" for every team. *Conclusion:* the cockpit shows no comments. Whether to override is Ananya's decision (T3 action item), not mine (D-011). High. Reviewed: [ ]

**N-19 Engineering pulse.** 4.0, 4.0, 3.9, 3.1; responses 5/5 then 4/5. T3 ("dipped in the July round") and e-mail 11 agree with the export. Three other signals: Marketing 3.8 to 3.4; Finance, People, Sales and Support within 0.2. With 5 people one answer can move the average by up to 0.8, so size of the drop is uncertain, direction is not. High on direction. Reviewed: [ ]

**N-20 Team sizes in the pulse (5+3+3+3+2+2 = 18, plus the CEO = 19)** corroborate headcount again (see N-01). Reviewed: [ ]

**N-21 Resignation letter.** Dated 15 Sep, to Nikhil, last day 31 Oct; Keka exit date 31 Oct; T3 "Sid from marketing has put in his papers". Consistent. His stated reason is wanting "clearer launch timelines". 15 Sep is also Atlas's original GA date; I report that as a timing observation, not a cause. High (facts), Low (any causal reading). Reviewed: [ ]

**N-22 Lakshmi's role.** T3: "Lakshmi as HRBP (she handles exits)". Keka: HR & Office Executive. *Conclusion:* Keka title stands; handling exit paperwork can be part of her duties. No conflict worth resolving. Reviewed: [ ]

**N-23 "Liver", "Kekka".** T3. Tracker header says Keka Hire, so "Liver" is a mishearing (Lever possible but unsupported); "Kekka" = Keka. Medium/High. Reviewed: [ ]

**N-24 Manager training "after Diwali, November-ish" (Deepa) vs "January" (Rohan).** No record settles it; left unresolved and not used. Reviewed: [ ]

**N-25 "Vicky" (Day 1) now Medium.** E-mail 06 shows the CFO pausing reqs with Vikram, i.e. the freeze decision was checked with Vikram. Alias confidence raised from Low to Medium. Reviewed: [ ]

**N-26 Leave register quirks.** (a) Names are abbreviated ("A. Das"); approvers are initials (VM, MI, AR, NB, DJ) resolved through aliases. (b) "Days" counts working days (Fatima 9-27 Feb = 15 weekdays). (c) It is a Google Sheet, so I do not treat it as complete. (d) It corroborates Fatima's Feb leave (so Karthik ran the Feb payroll), Karthik's exam week, and Arjun's relocation in March. Reviewed: [ ]

**N-27 One engineer "I'm worried about" (T3), and a pattern in the leave register.** Five half-day personal leaves by one engineer in September invite a guess. *Conclusion:* I am deliberately not making it. It is a guess about a named person, from thin data; the policy (D-011) is that the cockpit reports team-level indicators only. The register and the persona are kept, but their reasons are left unspecified. Reviewed: [ ]


## Day 3 (T4 Head of Marketing, T5 VP Engineering, T6b voice note, Jira, git log, incidents, on-call rota, launch kit, invoice PIS-114, e-mails 04 05 08 09, e-mail printouts)


**N-28 Atlas GA date.** Jira's "Atlas GA" version: release date 2026-12-15, original 2026-09-15, last changed 2026-09-02 by `vikram`. Board Q3 (6 Oct): "moved GA", no date. T5 (Vikram): "on track, maybe a couple of weeks of buffer", board date "still September-ish". T1 (CEO): customers promised "by the festive season". *Conclusion:* believe Jira (system record with author and stamp). Vikram's T5 statement is contradicted by his own change on 2 Sep, so I do not rely on it; he owns delivery and has reason to sound reassuring. The date is as of the 31 Oct export. The CEO's festive-season promise (Diwali was 8 Nov, my own calendar knowledge) is missed. High. Reviewed: [ ]

**N-29 Sneha vs "Snehal".** The on-call rota lists both in the same week (a person cannot be primary and secondary at once); PagerDuty has both names as responders; T5 uses both and says it is "unclear if same person"; invoices bill "S. Patil" for on-call SRE support, and a contractor is not in Keka. *Conclusion:* two people: Sneha Kulkarni (employee, VX012) and a contractor I call Snehal (S. Patil). Medium (no record gives the contractor's full name). Reviewed: [ ]

**N-30 Contractor start date (unresolved).** Rota and invoice PIS-108 start 17/18 Aug; Sneha's 24 Aug e-mail says the contractor "starts on the rota this week" and Sneha handled SEV1 INC-205 on 22 Aug. If the later start is right, about a week of the Rs 70,800 invoice may be for time before the contractor started (roughly Rs 34,000 incl. GST on calendar-day pro-rata). I do not resolve this; I flag it as a question for Vikram. Low. Reviewed: [ ]

**N-31 Priya's two git identities.** `priya.n@veloxa.in` (425 commits) and `pnair@users.noreply.github.com` (163), both only in atlas-engine, from the first day of the log. Handle `pnair`, Jira initials PN, only P. Nair in Keka. *Conclusion:* same person (Medium). Matters: together 70% of atlas-engine commits; the company address alone 50%. The conclusion (concentration) holds either way. Reviewed: [ ]

**N-32 Jira quirks.** Assignee is shown as initials (PN, RV, AD, SK); summaries end in "(pn-3)" style counters, which are initials plus a counter, not people. Issue keys start at ATLAS-11 (epics are ATLAS-1..5; 6-10 are absent). Last ticket resolved 17 Sep; last created 1 Aug; yet git shows ~115-137 commits a month through October. *Conclusion:* Jira is partly stale, so the pace figure (about 77 points a month needed vs best month 42) is a warning, not a forecast. Story points are the team's own. Medium. Reviewed: [ ]

**N-33 Incident times.** PagerDuty times are UTC ("Z"); the rest of the data room is IST. I convert to IST. Two of the three SEV1s ran in the early hours IST. The incident count (6 Aug, 3 Sep, 2 Oct) matches Sneha's "third SEV1 this month" (24 Aug) and the board's "difficult August". High. Reviewed: [ ]

**N-34 Late nights.** T5: "Pria has been doing late nights but she likes it", placed after a 4-minute audio gap (11:20 to 15:30), so the wording is unreliable. Git (converted to IST): every one of the 103 late-night (22:00-05:00) commits and all 40 weekend commits are Priya's. "She likes it" cannot be tested. I treat this as concentration of work, not as a statement about her plans (D-011, D-019). Reviewed: [ ]

**N-35 Marketing spend.** T4 "one point eight" (no unit) vs the GL's Rs 14.27 L (Google Ads 4.24 L + summit 10.03 L; selected cost centres only). T2 "Nikhil's numbers never match mine". If it is Rs 18 L the gap is Rs 3.7 L, which could be spend outside the extract. I cannot tell who is right; no marketing-side sheet exists. Low. Reviewed: [ ]

**N-36 Summit leads.** T4: "best quarter ever for pipeline" vs "Manoj from sales says the summit leads are cold" (dismissed by Nikhil). No HubSpot or CRM export. The cockpit says "I don't know". Reviewed: [ ]

**N-37 Names and tools.** "Ayesha" = Aisha Khan (performance marketing); "Hub Spot" = HubSpot; "Linked in campaign manager" = LinkedIn. T5 "tried Linear for a month and went back" explains the CEO's "Linear or Jira" in T1: Jira. Reviewed: [ ]

**N-38 Launch kit.** Kit v1 dated 21 Jul, owner Sid; e-mail 22 Jul "Just need a date from engineering"; T4 "ready since July". Planned launch 22 Sep (one week after the original GA, so no conflict); stale now. Marketing was waiting on engineering. This also explains Siddharth's stated reason. High. Reviewed: [ ]

**N-39 Invoice quirks that are not errors.** IGST at 18% on Rs 1,20,000 = Rs 21,600 is correct (vendor in Maharashtra, customer in Karnataka: inter-state). PIS-108 Rs 70,800 = Rs 60,000 + 18% (half a month's retainer, while a strict 14/31 pro-rata would be Rs 63,949 incl. GST). PIS-114 is dated 1 Oct, outside the Apr-Sep ledger, so its absence from the GL is not a gap. GL amounts are gross of GST. Reviewed: [ ]

**N-40 T4 action item "Backfill Sid's role (owner: unassigned)".** The hiring tracker shows REQ-016 (PMM, Backfill) opened 17 Sep under Nikhil's ID with 7 candidates. Tracker believed; the action item is stale or loosely worded. Reviewed: [ ]

**N-41 Board "engine itself is feature-complete" vs Jira.** Jira has open work in the core engine and re-routing epics and the hardening epic is 6 of 43 points done. Unresolved: either the board text is optimistic or Jira is stale. Reviewed: [ ]

**N-42 The new CRO.** T4 (hearsay) and T6b (CEO) only. No CRO in Keka, the tracker or the ledger. Recorded as a planned change, not applied (D-016). Reviewed: [ ]

**N-43 E-mail printouts.** `Email_Printouts.pdf` repeats e-mails 01-11 word for word. I cite the original .eml files; the printout is a redundant source. Reviewed: [ ]


## Day 4 (T6c and T6d voice notes; no data-room files were released today)


**N-44 "slag messages".** The T6c transcript says "slag messages". The context ("so I can see what they're saying") and the company's tools point to **Slack**. It is an auto-transcription slip, like "Pria" and "Hub Spot". Either way, no Slack or chat export exists in any day folder, so the answer is the same. Medium-High. Reviewed: [ ]

**N-45 "Pria" in T6d.** Same slip as T1 and T5 ("Pria"); only one Priya/Pria in Keka (Priya Nair, VX007); the alias is already logged at High. Reviewed: [ ]

**N-46 "version three".** Taken to mean Atlas v3 (the GA release): T1 says customers were promised "v3". Medium-High. Reviewed: [ ]

**N-47 The resignation itself.** Only source is the CEO's voice note, on the day it happened, which is after the Keka export (31 Oct) and every other source. Nothing can confirm or contradict it. Keka stays "Active" until HR records it; I store it as a reported event. *Conclusion:* credible report, unconfirmed record. Reviewed: [ ]

**N-48 "Two months, I think".** The CEO is unsure. No notice period for Priya exists in the data room. Siddharth's notice (resigned 15 Sep, last day 31 Oct, 46 days) is a different contract, so it is not a guide. I count two months as 61 days from 19 Nov (about 19 Jan 2027), but only as a conditional. Low. Reviewed: [ ]

**N-49 "Deepa says it's fine."** Second-hand from the CEO, with no source I can check. The same pattern appears in T1 ("Deepa says it's normal" about attrition) where the data shows about 6%, not the 12% in one document, so this is the second time the CEO relays Deepa's reassurance. I do not treat either as a verdict. Deepa's own e-mail 11 says the engineering team is too small to share survey comments. Reviewed: [ ]

**N-50 Day 4 has no new records.** The Day 4 folder contains only T6c and T6d. So the data model, the agents and the claims are unchanged; only the voice notes and the two reported facts are new. The Day 3 findings about concentration (about 70% of atlas-engine commits, 56% of story points) are what T6d plugs into. Reviewed: [ ]
