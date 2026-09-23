# Bulk Purchase Annuity on the Data Intelligence Platform
### Raw scheme document → priced-ready data in minutes, with full lineage
**Royal London · BPA Pricing & Onboarding**

Presenter: Solution Architecture · Built on Databricks (Unity Catalog · Lakebase · AI Functions · Genie · Databricks Apps)

---

## Slide 1 — The outcome, up front

**Today:** an actuary spends **days per scheme** transcribing ~40 structured fields out of
PDFs, Excel, Word and CSV packs before any pricing judgement can begin.

**With this build:** the same scheme is **document-to-structured-data in minutes**, with a
one-click audit trail — the actuary *reviews and signs off* instead of *re-keying*.

> The bottleneck moves from **data entry** to **pricing judgement** — where you want your
> actuaries spending their day.

---

## Slide 2 — Why this matters now (the buyer's context)

- **UK BPA volume has surged.** Exclusivity windows are measured in weeks; the limiting
  factor is rarely the pricing model — it's how fast the team gets a clean structured view.
- **Every scheme arrives in a different shape.** 10-page triennial valuations, multi-tab
  Excel contribution schedules, Word benefit specs, CSV member extracts.
- **The work is largely re-keying.** 40+ fields per scheme, transcribed by hand into a
  master workbook, before judgement even starts.

**The ask from the business:** quote *more* schemes, at the *same* quality bar, without
growing the team linearly with deal flow.

---

## Slide 3 — What we built (one integrated journey)

A single governed pipeline on Databricks — no bolt-on LLM, no per-template parser:

1. **Ingest** — scheme documents land in a **Unity Catalog Volume** (governed, audited).
2. **Extract** — **`ai_parse_document`** + **`ai_extract`** turn any format into structured,
   confidence-scored fields — *chosen per document kind*.
3. **Serve** — results land in **Lakebase Postgres** for the live review workflow.
4. **Review & approve** — actuary edits, confidence pills, per-field sign-off.
5. **Govern** — approval syncs to **Delta tables** in Unity Catalog (lineage + time travel).
6. **Consume** — **AI/BI Lakeview dashboard**, **Genie** (governed text-to-SQL), Power BI —
   all on the *same* tables. Surfaced in one **Databricks App**.

---

## Slide 4 — The KPIs this moves (executive sponsor)

| KPI | Today | With BPA-on-Databricks | Why |
|-----|-------|------------------------|-----|
| **Cycle time per scheme** | Days of reading | **Hours of spot-checking** | AI extracts 40+ fields in minutes; actuary reviews, doesn't transcribe |
| **Schemes quotable per actuary / quarter** | Capped by re-keying | **Materially higher** | Throughput scales with serverless compute, not headcount |
| **New-template lead time** | "Can't quote until we build a parser" | **Zero** | One `ai_extract` pipeline handles every format |
| **Audit-pack effort** | Rebuilt each quarter | **By-product of the day job** | Source, confidence, reviewer, timestamp captured in Delta as you go |

*Illustrative, directional — validate against your own volumes in a paid pilot.*

---

## Slide 5 — What changes for the actuarial team (domain owner)

- **Days of reading → hours of spot-checking.** ~40 fields across hundreds of pages; the
  actuary signs off, not transcribes.
- **Variety stops being a bottleneck.** PDF, Excel, Word, CSV — one pipeline, no per-template
  parser to own and update.
- **Quality-of-work shift.** Seniors spend time on outliers and negotiation; juniors learn
  pricing from day one, not data entry.
- **Consistent interpretation across deals.** Same function, same field list, same confidence
  model — two actuaries produce the same shape of output, no personal-spreadsheet drift.

---

## Slide 6 — Defensible by default (the regulated-insurer requirement)

- **The data never leaves your platform.** Documents, extracted fields, audit trail — all
  inside *your* Unity Catalog, *your* VPC, *your* governance. The model call is a SQL
  function, not an outbound API.
- **Every pricing input carries its lineage:** source document → source field → confidence →
  reviewer → approval timestamp, in one Delta table.
- **Genie is governed text-to-SQL:** it only sees tables the user is entitled to, and every
  answer ships with the SQL it ran — *validate before you trust*.
- **The evidence pack** for internal second-line, PRA audit and trustee reporting is produced
  as you go, not rebuilt at quarter-end.

---

## Slide 7 — Proof it runs (this is not a mock-up)

Executed end-to-end in a Databricks workspace on 2026-09-23 (see `evidence/` in the repo):

- **72 documents** uploaded to the UC Volume across **6 pension-scheme prospects**.
- **16 documents** ingested through the deployed app — `ai_parse_document` on PDFs, native
  parsers on DOCX/XLSX/CSV — producing **251 structured fields**, reviewed & approved.
- **16 summary + 251 detail rows** synced into governed Delta tables.
- **Genie** answered *"how many schemes have approved data by customer, and average
  confidence?"* with correct governed SQL over `vw_portfolio_overview`.
- **Per-document-kind routing verified:** benefit spec → 17 fields, BPA data pack → 21,
  triennial valuation → 18, funding update → 10 — each asked only the questions that matter.

---

## Slide 8 — The platform story (one slide the platform team keeps)

| What the business saw | The Databricks primitive |
|---|---|
| PDF / Excel / Word / CSV ingestion | **Unity Catalog Volumes** — governed file storage |
| Document parsing | **`ai_parse_document`** — managed SQL function |
| Structured extraction | **`ai_extract`** — managed SQL function, no prompt engineering |
| Operational store | **Lakebase Postgres** — real transactional workload |
| Approval & audit | **Delta tables** — time travel, lineage, row-level governance |
| Live dashboard | **AI/BI Lakeview** — embedded, no per-user license |
| Conversational BI | **Genie** — governed text-to-SQL, embedded |
| Everything above | **One platform, one identity, one audit log** |

---

## Slide 9 — Where this goes next

The same pattern applies well beyond BPA — anywhere a regulated team reads unstructured
documents and re-keys into a master workbook:

- Workplace-pension **Value-for-Money** reviews
- Group-risk **claims evidence**
- M&A **acquired-book due-diligence** packs

**BPA is the first proof point; the platform underneath is the same.**

---

## Slide 10 — The ask

**Run one real scheme through this flow on your own documents in a 2-week paid pilot.**

- You bring: 3–5 real scheme packs (redacted as needed) and one actuary reviewer.
- We prove: cycle time per scheme, extraction accuracy vs. your ground truth, and the
  audit pack — on *your* data, in *your* governance.
- Success criteria agreed up front, in your KPIs.

*Live build:* `https://rlg-demo-7474653316213627.aws.databricksapps.com`
