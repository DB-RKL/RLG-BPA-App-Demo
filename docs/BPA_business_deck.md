# Bulk Purchase Annuity on the Data Intelligence Platform
### Raw scheme document → priced-ready data in minutes, with full lineage
**Royal London · BPA Pricing & Onboarding**

Presenter: Solution Architecture · Built on Databricks (Unity Catalog · Lakebase · AI Functions · Genie · Databricks Apps)

---

## Slide 1 — The outcome, up front

**Today:** an actuary spends **~1.5–2 days per scheme** transcribing ~40 structured fields out
of PDFs, Excel, Word and CSV packs before any pricing judgement can begin.

**With this build:** the same scheme is **document-to-structured-data in minutes**, with a
one-click audit trail — the actuary *reviews and signs off* instead of *re-keying*.

### The number
**~1.5 actuarial days saved per scheme.** At ~150 schemes quoted a year, that is **~225 days —
roughly £150k of actuarial time a year** redeployed from re-keying to pricing. The larger prize
is **win rate**: quoting more schemes inside the exclusivity window.

> The bottleneck moves from **data entry** to **pricing judgement** — where you want your
> actuaries spending their day.

*(Estimate. Assumes ~1.5 days saved/scheme, ~150 schemes/year, ~£700 fully-loaded actuarial
day. Validate against Royal London's own volumes in the pilot.)*

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

**Raw scheme docs → UC Volume → `ai_parse`/`ai_extract` → Lakebase → Delta (Unity Catalog) →
Genie + Lakeview → Databricks App.** One flow, one catalog, one audit trail — not stitched-together demos.

1. **Ingest** — scheme documents land in a **Unity Catalog Volume** (governed, audited).
2. **Extract** — **`ai_parse_document`** + **`ai_extract`** turn any format into structured,
   confidence-scored fields — *chosen per document kind*.
3. **Serve** — results land in **Lakebase Postgres** for the live review workflow.
4. **Review & approve** — actuary edits, confidence pills, per-field sign-off.
5. **Govern** — approval syncs to **Delta tables** in Unity Catalog (lineage + time travel).
6. **Consume** — **AI/BI Lakeview dashboard**, **Genie** (governed text-to-SQL), Power BI —
   all on the *same* tables. Surfaced in one **Databricks App**.

*The same field flows from the source page through to the dashboard number with its lineage intact.*

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

## Slide 7 — Decisions & trade-offs

| Decision | Why | Trade-off we accepted |
|---|---|---|
| **`ai_extract` SQL functions**, not a custom LLM integration | Data stays in Unity Catalog; no prompt to maintain; model upgrades ship with the platform | Less control over the exact prompt — fine for a regulated team that values governance over tuning |
| **Field list keyed to document kind** | Keeps the review screen high-signal | More schemas to define up front |
| **Lakebase for live state, Delta for the record of truth** | Review needs row-level updates; audit needs lineage + time travel | Two stores to keep in sync (handled by one sync-on-approve step) |
| **Human approval gate kept in the middle** | The AI is fast; the actuary stays accountable | Not fully "hands-off" — by design, for sign-off |
| **Reused an existing warehouse + Lakebase instance** | No new compute to stand up | Shared capacity, acceptable for a demo/pilot |

---

## Slide 8 — How we built it (AI as a force multiplier)

- **Built with Claude Code** driving the Databricks CLI, SQL, and app deploy end-to-end —
  provisioning, extraction pipeline, dashboard, Genie space, and the workflow run.
- **The extraction is itself AI** — Databricks `ai_parse_document` + `ai_extract`, so there is
  no bespoke parser or prompt to maintain.
- **Pattern that worked:** let the model handle the mechanical span (retarget config, generate
  DDL, drive the HTTP workflow, harvest evidence) while decisions — model choice, the human
  approval gate, live-vs-Delta split — stayed explicit and reviewed.
- **Result:** a retarget-and-deploy of a full six-stage journey into a new workspace, with
  committed run evidence, in a single working session.

---

## Slide 9 — Proof it runs (this is not a mock-up)

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

## Slide 10 — The platform story (one slide the platform team keeps)

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

## Slide 11 — Where this goes next

The same pattern applies well beyond BPA — anywhere a regulated team reads unstructured
documents and re-keys into a master workbook:

- Workplace-pension **Value-for-Money** reviews
- Group-risk **claims evidence**
- M&A **acquired-book due-diligence** packs

**BPA is the first proof point; the platform underneath is the same.**

---

## Slide 12 — The ask

**Run one real scheme through this flow on your own documents in a 2-week paid pilot.**

- You bring: 3–5 real scheme packs (redacted as needed) and one actuary reviewer.
- We prove: cycle time per scheme, extraction accuracy vs. your ground truth, and the
  audit pack — on *your* data, in *your* governance.
- Success criteria agreed up front, in your KPIs.

*Live build:* `https://rlg-demo-7474653316213627.aws.databricksapps.com`

---

## Slide 13 — Appendix: objection handling

**Business stakeholder (pricing / actuarial head)**
- *"Can we trust the AI?"* — Nothing is priced on an unreviewed field. Every value has a
  confidence score, an editable review step, and a named approver in the audit trail.
- *"What about the schemes it gets wrong?"* — The confidence score surfaces exactly those for
  closer review; the actuary's time goes to the hard 10%, not the easy 90%.

**Technical stakeholder (platform / data)**
- *"Is our data leaving the platform?"* — No. Extraction is a SQL function inside Unity
  Catalog, in your VPC. No outbound API call.
- *"What do we have to maintain?"* — No parser per template, no prompt. `ai_extract` is managed;
  upgrades ship with the platform. The only bespoke code is the review app and the field lists.
- *"How does this govern access?"* — One catalog, one identity. Genie and the dashboard inherit
  Unity Catalog permissions; the app runs as a service principal with scoped grants.
