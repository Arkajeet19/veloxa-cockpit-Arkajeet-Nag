# TRANSCRIPT_NOTES

> **Status: DRAFT proposals for owner review.** Each entry records the evidence and the conclusion I currently lean towards. The hackathon rules require that *I* own every conflict resolution, so each entry has a `Reviewed` box to be ticked only after I have re-read the evidence and rewritten the reasoning in my own words.

Format: ID | what looks wrong | evidence | conclusion | confidence | Reviewed.

## Day 1 (T1 CEO kickoff, T2 CFO call, brief, README, board updates, exports)

**N-01 Company size.** T1 says "roughly eighteen people ('one-eighty, give or take')"; brief says 180-person. Keka lists 19, both board updates say Team 19, the Mar payroll register has 19 people, and payroll totals Rs 31.75 L/month (about Rs 1.7 L per head; for 180 it would be Rs 17k each). *Conclusion:* 19; the 180 is a misstatement, and "eighteen" is the summariser trying to reconcile with the audio. T1 is internally inconsistent, which is itself a sign of a bad transcript. High. Reviewed: [ ]

**N-02 ARR.** T1: "forty-two crore, maybe forty-five now". T2: start of year "forty-eight". Board: Rs 5.8 Cr (Jun) and Rs 6.1 Cr (Sep). *Conclusion:* believe the board numbers. Three spoken figures cannot be reconciled with one another or with the board; if they are 4.2/4.5/4.8 Cr then ARR would have grown 4.8 -> 5.8 in one quarter, which is large but the board is the only written source. I report `sources_disagree` rather than pretending it is solved. Medium. Reviewed: [ ]

**N-03 Burn.** T1 "around two point two (unit not stated)"; T2 "two point two lakhs a month, sometimes two point five". Board: Rs 46 L, then Rs 44 L. GL payroll alone is Rs 31.75 L/month. *Conclusion:* "2.2 lakh" is impossible; two speakers saying 2.2 suggests a systematic unit error (maybe crore per year/quarter, or "forty-two" heard as "two"). Board figure believed, Medium; flagged unresolved. Also noted: burn 44 L vs ARR 6.1 Cr (51 L/mo revenue) vs 13-month runway does not reconcile under either gross or net definitions. Reviewed: [ ]

**N-04 Tool names.** "Jeera" = Jira, "Git Hub" = GitHub, "Cult Amp" = Culture Amp, "Joho books" = Zoho Books, "Kayka" = Keka, "hub sport" = HubSpot (probable), "slag channel" = Slack (probable). T1 hedges "Linear, I think, or they moved back to the Jeera board"; the README lists Jira (ATLAS) as the engineering export. *Conclusion:* the README and export headers beat spoken names. Linear is not supported by any record. High (Slack/HubSpot Medium). Reviewed: [ ]

**N-05 Names.** "Pria" -> Priya Nair (only Priya); "Kartik" -> Karthik Subramanian; "Fatima Shaikh" -> Fatima Sheikh (Keka, e-mails); "Vicky" -> probably Vikram Menon (Low). Processed/Entered By "FS" = Fatima, "KS" = Karthik. Reviewed: [ ]

**N-06 Fiscal year.** T2 "FY twenty-six (maybe twenty-seven)". April-March year puts Nov 2026 in FY27. The payroll sheet called "Payroll Q4" (Jan-Mar 2026) is Q4 of FY26. Medium. Reviewed: [ ]

**N-07 Books migration.** T2: moved from Tally to Zoho "Jan or Feb", older numbers "may not match". The only GL given is Apr-Sep 2026 (all Zoho), so I cannot test the mismatch. Jan-Mar payroll comes from a pre-Keka workbook; its total matches Apr-Sep GL payroll to the rupee, so no break there. Reviewed: [ ]

**N-08 "The two backend roles".** Mentioned in passing in T2. GL: Rs 1.77 L = 50% advance for a 2-role search (30 Jun). Board Q2 plans two backend hires; Q3 says hiring paused; Keka shows no joiner after 3 Feb (Rahul Verma). *Conclusion:* not filled as of 31 Oct. Medium (absence of evidence; contractors not in Keka). Reviewed: [ ]

**N-09 Summit vendors.** "Sapphire Events Pvt Ltd" (INV-2291) and "Saphire Event Mgmt" (SEM-0087) are both MKT-EVT. "Sapphire Residency Hotel" is SAL-TRV, sales offsite. *Conclusion:* first two are one vendor (Medium); the hotel is a false friend and is excluded. T2 "Nikhil's numbers never match mine" cannot be tested until marketing's own numbers arrive. Reviewed: [ ]

**N-10 Payroll anomaly (not a mishearing, a record error).** Rahul Verma joined 3 Feb but the Feb register shows 28/28 days payable at the full amount. E-mails 01-03 explain it (Karthik covered while Fatima was out, reused the Jan sheet; Rahul queried on 6 Mar; Fatima: "Will check and get back" on 10 Mar). Not a quirk: a real error. Reviewed: [ ]

**N-11 Things that look wrong but are not.** (a) Rahul is absent from the Jan register: he joined in Feb. (b) Siddharth is "Notice period" with exit date equal to the export date: consistent with exiting that day. (c) GL vouchers out of date order (JV-0904 dated 3 Sep before JV-0903 dated 4 Sep): voucher number sequence is not chronological, not an error. (d) AWS booked "previous month": txn date is a month after the service month. (e) GL says "selected cost centres": absence of a cost is not proof of no cost. Reviewed: [ ]

**N-12 Brief vs HR e-mail.** Brief: 10 working days, live sessions on days 2/4/8, drops on days 1/3/4. E-mail: 5 days, no live sessions, folders on days 1/2/3/4. Latest instruction wins (A-012). Reviewed: [ ]

**N-13 Board "number by March".** Speaker 2 unidentified, referent unclear. Cockpit says "I don't know". Reviewed: [ ]
