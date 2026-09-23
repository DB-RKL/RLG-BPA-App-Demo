# Royal London BPA — Live Demo Walkthrough (wx20co)

> **Audience.** Royal London BPA pricing, pensions-data and platform stakeholders.
> **Runtime.** ~15 min core, ~20 min with the deep dives.
> **App.** https://rlg-demo-7474653316213627.aws.databricksapps.com
> **Workspace.** `fevm-serverless-stable-wx20co` · catalog `serverless_stable_wx20co_catalog.bpa_rubjit`
> **Narrative.** "This is your BPA pricing and onboarding process when the unstructured scheme
> documents are treated as first-class, governed data on the Databricks Data Intelligence Platform."

Structure every act as **tell → show → tell**: say what you're about to prove, show it live, then say what it means for the pricing team.

---

## 0. Pre-flight (5 min before)

Have two browser tabs open:
- **Tab A — the app** (URL above), signed in with your Databricks identity.
- **Tab B — the Databricks workspace**, on the pipeline `bpa-bronze-documents-ingest` and a SQL editor on warehouse `ced20c73f16a2915`.

Confirm:
- App **Customers** shows the 6 seeded schemes (BDO, Renishaw, Reading University, Thames Water, Spirax-Sarco, RSM UK), each with pending files available to extract live.
- **Reporting** renders the embedded Lakeview dashboard (`01f1b72a2a1d100fb06e1284b208e373`).
- **Genie AI** loads the space (`01f1b729d86f1055b77bac0c71294adc`) — no empty state.
- A terminal ready to run the arrivals generator (for Act I).

Key IDs (for recovery): Lakeflow pipeline `8c2f4acb-be32-47c1-af7f-60efe925f1f6`; Genie space `01f1b729d86f1055b77bac0c71294adc`; dashboard `01f1b72a2a1d100fb06e1284b208e373`.

---

## 1. Opening — the business problem (90 sec)

> "Three things put a ceiling on how many schemes your pricing team can quote.
> **One — BPA volume has surged;** exclusivity windows are weeks, and the limiter is rarely the
> pricing model, it's getting a clean structured view of a scheme.
> **Two — every scheme arrives in a different shape:** triennial-valuation PDFs, multi-tab Excel
> contribution schedules, Word benefit specs, CSV member extracts.
> **Three — the work is largely re-keying:** ~40 structured fields per scheme, transcribed by hand
> before an actuary exercises any judgement.
> What I'll show is that same process on Databricks: **raw document to priced-ready data in minutes,
> with full lineage** — one governed pipeline, not a bolt-on."

---

## 2. Act I — Lakeflow: raw data arriving in the cloud (2–3 min)

**Tell:** "Scheme packs land in governed cloud storage and are ingested automatically, incrementally —
the platform notices new files the moment they arrive."

**Show (in the terminal):**
```bash
python3 scripts/simulate_document_arrivals.py --scheme greggs --display "Greggs plc Retirement Plan"
```
> "That just dropped a new prospect's pack — benefit spec, contribution schedule, funding update,
> member data — into a **Unity Catalog Volume**, exactly as if an adviser had emailed it over."

**Show (Tab B):** start an update on the `bpa-bronze-documents-ingest` Lakeflow pipeline.
> "This is a **Lakeflow Declarative Pipeline** running **Auto Loader**. It's already seen the existing
> schemes, so it doesn't re-read them — it picks up **only the new files**, exactly once, checkpointed.
> That's the difference between a nightly batch reload and true incremental ingestion."

**Show the result (SQL editor):**
```sql
SELECT customer_slug, COUNT(*) files, MAX(ingest_time) last_ingest
FROM serverless_stable_wx20co_catalog.bpa_rubjit.bronze_documents
GROUP BY customer_slug ORDER BY last_ingest DESC;
```
**Tell:** "Every document that has ever landed is now a governed row in Unity Catalog — the ingest ledger
for the whole book. No files lost in inboxes."

---

## 3. Act II — The speed run: document to structured data (3 min)

Navigate to **Customers → BDO Pension Fund**, open **Pending Extraction**.

**Tell:** "One button does three things, and every step is a native Databricks primitive — no bespoke parser."

**Show:** click **Extract** on one pending file (e.g. a benefit spec or BPA data pack).
> "1. **`ai_parse_document`** reads the file straight from the Volume — layout, tables, text.
> 2. **`ai_extract`** pulls a **document-kind-specific field list** — a benefit spec is asked about accrual
> rate, retirement age, increase basis; a funding update about assets, technical provisions, funding level.
> 3. The structured, confidence-scored output lands in **Lakebase Postgres**, ready for review."

**Show the variety point:** extract a different kind (e.g. contribution schedule CSV, member data XLSX).
> "Different format, different question set — one pipeline. Variety stops being a bottleneck; the team
> doesn't maintain a parser per template."

*(Field counts differ by kind — benefit spec ~17 fields, BPA data pack ~21, triennial valuation ~18 — because each document is only asked what's relevant.)*

---

## 4. Act III — Review & approve: the human gate (2 min)

Open a freshly-extracted document (**Review**).

- **Left:** the source document. **Right:** extracted fields, grouped, each with a confidence pill.
> "The AI is fast, but the actuary is accountable. Every field is editable, every value has a confidence
> score, every approval is logged against a user and timestamp."

**Show:** edit one field, then click **Approve & Sync to Catalog**.
> "That marks the fields approved in Lakebase and syncs the clean record into governed **Delta tables** in
> Unity Catalog — with source, confidence, reviewer and timestamp attached.
> **The audit pack is a by-product of the day job**, not a quarter-end scramble. When audit asks 'where did
> this revaluation rule come from', it's one row and one click."

---

## 5. Act IV — The live dashboard (2 min)

Go to **Reporting**.

- **KPI tiles:** approved plans, schemes with data, awaiting review, average confidence.
- **Embedded Lakeview dashboard:** portfolio by scheme, throughput, extraction quality, category completeness.
> "Native Databricks **AI/BI**, embedded in the app — same Delta tables, no second BI tool, no per-user seat
> for actuaries who just need to look. Every approval updates this; it's a query on a Delta table 20 seconds
> behind the extraction, not a nightly job."

*(Power BI tab is available for teams that live in Power BI — same Delta tables via DirectQuery.)*

---

## 6. Act V — Genie: governed natural language (2 min)

Go to **Genie AI**. Ask, live:

- *"How many schemes have approved data by customer, and what is the average confidence?"*
- *"How many documents have landed by scheme in bronze_documents?"* (ties back to Act I's Lakeflow ingest)
- *"List the benefit fields and their values for BDO Pension Fund."*

> "Genie is **governed text-to-SQL**: it only sees the tables this user is entitled to via Unity Catalog,
> and every answer ships with the **SQL it ran** — so the actuary validates the query before trusting the
> number. For a regulated workflow that's the difference between 'chat with your data' as marketing and as
> something audit will sign off."

---

## 7. Close — platform story, impact, the ask (90 sec)

| What you saw | The Databricks primitive |
|---|---|
| Documents landing + incremental ingest | **UC Volumes** + **Lakeflow / Auto Loader** |
| Parsing & extraction | **`ai_parse_document`** + **`ai_extract`** |
| Operational review state | **Lakebase Postgres** |
| Approval & audit | **Delta tables** — lineage, time travel |
| Live dashboard + NL | **AI/BI Lakeview** + **Genie** |
| All of it | **One catalog, one identity, one audit log** |

**Impact (illustrative, validate in a pilot):** ~1.5 actuarial days saved per scheme → at ~150 schemes/year,
~£150k of actuarial time redeployed from re-keying to pricing — plus the win-rate upside of quoting more
schemes inside the exclusivity window.

**The ask:** "Run one real scheme through this on your own documents in a 2-week paid pilot — success
criteria agreed up front, in your KPIs."

---

## 8. Objection handling (be ready)

**Business (pricing/actuarial head)**
- *"Can we trust the AI?"* — Nothing is priced on an unreviewed field; confidence score + review step + named approver on every value.
- *"The ones it gets wrong?"* — Confidence surfaces exactly those; actuary time goes to the hard 10%.

**Technical (platform/data)**
- *"Is data leaving the platform?"* — No. Extraction is a SQL function inside Unity Catalog, in your VPC.
- *"What do we maintain?"* — No per-template parser, no prompt; `ai_extract` is managed. Only bespoke code is the review app + field lists.
- *"Access control?"* — One catalog, one identity; Genie and the dashboard inherit UC permissions; the app runs as a scoped service principal.

---

## 9. Recovery & reset

| Symptom | Recovery |
|---|---|
| An Extract hangs on one file | Go **Back**, pick another. Don't retry on stage. |
| Dashboard iframe blank | Refresh once; if still blank, narrate the KPI tiles and move to Genie. |
| Genie returns SQL but no rows | Ask a simpler question ("how many documents do we have"). Never edit its SQL live. |
| Lakeflow update slow to start | Serverless cold start is ~2–3 min; run the generator first so files are waiting, or pre-warm before the demo. |

**Reset between demos** (SQL editor on `ced20c73f16a2915`):
```sql
-- reopen approved docs for a fresh review demo (Lakebase state lives in the app's Postgres, not here)
-- to re-demo extraction, simply extract a still-pending Volume file for the chosen scheme.
```
For a clean portfolio, re-approve documents in the app (the sync truncates+reloads the Delta tables each time).
