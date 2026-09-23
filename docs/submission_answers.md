# FE Bar Submission — Answers

**Customer name:** Royal London Group
**Industry / vertical:** Regulated (UK life insurance / pensions)

---

## What is the business challenge you are solving?

Royal London prices Bulk Purchase Annuity deals — taking on closed defined-benefit pension
schemes. Before an actuary can price a scheme, someone hand-copies about 40 fields (benefit
bases, revaluation rules, commutation factors, funding position) out of PDFs, spreadsheets,
Word docs and CSVs into a master workbook. Every scheme arrives in a different shape, so the
team keeps a different reading routine for each. That re-keying is slow, error-prone and hard
to audit — and it caps how many schemes the team can quote inside tight exclusivity windows.

---

## How does your Databricks solution address this challenge?

One governed pipeline turns any scheme document into priced-ready data:

- **Lakeflow** — scheme packs land in a **Unity Catalog Volume**; a serverless **Lakeflow
  Declarative Pipeline** running **Auto Loader** ingests each new file exactly once
  (checkpointed, incremental) into a governed `bronze_documents` Delta table. Drop a new pack
  in and it is picked up automatically — no batch reload.
- **Gen AI** — **`ai_parse_document`** reads each file on the SQL warehouse; **`ai_extract`**
  pulls a field list chosen per document type (a benefit spec and a funding update get
  different questions). Every field is confidence-scored.
- **Lakebase** — extracted fields land in Postgres, holding live document and review state for the app.
- **Review app** — a FastAPI + React **Databricks App** where an actuary edits values, sees
  confidence per field, and approves. Nothing is trusted until a person signs it off.
- **Unity Catalog / Delta** — on approval, the clean record syncs to Delta tables with its
  source, confidence, reviewer and timestamp attached.
- **Genie + AI/BI** — a **Genie** space (governed text-to-SQL) and an embedded **Lakeview**
  dashboard sit on the same tables.

Architecture: raw docs → UC Volume → Lakeflow (Auto Loader) → bronze Delta → `ai_extract` →
Lakebase → approved Delta → Genie + Lakeview → app. One catalog, one identity, one audit trail.

---

## What AI tools did you use, and what was your workflow? Decisions and trade-offs?

Built with **Claude Code** driving the Databricks CLI, SQL and app deploy end to end —
provisioning the schema, volume, Lakeflow pipeline, Lakebase tables, dashboard and Genie space,
then running the workflow and harvesting evidence. The extraction itself is AI: Databricks
`ai_parse_document` + `ai_extract`.

Decisions and trade-offs:
- **`ai_extract` SQL functions, not a custom LLM integration.** Data stays in Unity Catalog,
  no prompt to maintain, model upgrades ship with the platform. Trade-off: less prompt control
  — accepted, because governance and low maintenance matter more here.
- **Field list keyed to document type**, not one list for everything — keeps the review screen
  high-signal, at the cost of defining more schemas up front.
- **Lakebase for live state, Delta for the record of truth.** Review needs row-level updates;
  audit needs lineage and time travel. Two stores, kept in sync by one sync-on-approve step.
- **Human approval gate kept in the middle** — the AI is fast; the actuary stays accountable.
  Not fully hands-off, by design.
- **Reused an existing warehouse and Lakebase instance** to avoid standing up new compute.
- **Let Claude Code handle the mechanical span** (retarget config, generate DDL, drive the
  workflow, collect evidence) while the judgement calls — model choice, the approval gate, the
  live-vs-audit split — stayed explicit and reviewed.

---

## What are the business outcomes and impact?

- **Days of reading become hours of spot-checking.** The actuary reviews and signs off instead
  of transcribing ~40 fields per scheme.
- **Quantified:** ~1.5 actuarial days saved per scheme. At ~150 schemes a year, that is ~225
  days — roughly **£150k of actuarial time a year** redeployed from re-keying to pricing.
  (Estimate; validate against Royal London's own volumes.) The larger prize is **win rate** —
  quoting more schemes inside the exclusivity window.
- **No new lead time for new formats.** One pipeline handles PDF, Excel, Word and CSV — no
  "we can't quote that one until we build a parser."
- **The audit pack is a by-product.** Every priced input carries its source, confidence,
  reviewer and timestamp in Delta — ready for second-line, PRA audit and trustee reporting,
  not rebuilt each quarter.
- **Proven, not slideware.** Run end to end on the live app: Lakeflow ingested 72 documents
  then incrementally picked up a new scheme's 4 files; 251 fields extracted, reviewed and
  approved; Genie answered portfolio questions in checkable SQL.
