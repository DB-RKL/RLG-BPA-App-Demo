# Royal London · Bulk Purchase Annuity (BPA) · Demo Script

> **Audience.** Royal London BPA operations, pensions data, and technology stakeholders.
> **Runtime.** ~15 minutes (core), ~25 minutes (with deep dives).
> **URL.** https://rlg-demo-1444828305810485.aws.databricksapps.com
> **Narrative.** "This is what your BPA pricing and onboarding process looks like when the unstructured scheme documents are treated as first-class data on the Databricks Data Intelligence Platform."

---

## 1. Before you walk in (2 min prep)

1. Open the app in a fresh Chrome window. Sign in with your Databricks identity.
2. Confirm state:
   - **Overview** shows recent activity.
   - **Customers** shows 6 prospect schemes (BDO, Renishaw, Reading University, Thames Water, Spirax-Sarco, RSM UK).
   - Pick **one customer** (recommended: **BDO Pension Fund**) and confirm there are ≥ 3 files in "Pending Extraction" and ≥ 1 in "In Review" so the speed-run lands.
   - **Reporting** loads and the embedded AI/BI dashboard renders on the default tab. Click the **Power BI** tab once to pre-warm the iframe (see 6c).
   - **Genie AI** auto-loads the provisioned space (ID `01f13a464fb81f5e921abb671a38c087`) — no "Connect a Genie Space" empty state.
3. Open a second tab pinned to the Databricks workspace with `main.bpa_rubjit` catalog so you can pivot to SQL and Genie at the end.
4. Be signed into Power BI ([app.powerbi.com](https://app.powerbi.com)) in the same browser session so the Power BI embed auto-authenticates on first click.

---

## 2. Opening — the business problem (90 sec)

> "Three things I want to put on the table before we start the demo — because they're the reason your pricing team hits a ceiling on how many schemes they can quote.
>
> **One. UK BPA volume has surged.** Schemes are moving to insurers faster than ever, exclusivity windows are measured in weeks, and the limiting factor is almost never the pricing model — it's how quickly your actuaries can get a clean structured view of a scheme to run it through.
>
> **Two. Every scheme arrives in a different shape.** Some sponsors send a 10-page triennial valuation PDF and a BPA data pack. Some send multi-tab Excel contribution schedules and XLSX member data extracts. Some send Word benefit specs or scanned trustee minutes. Your team today maintains a different reading rhythm — and a different spreadsheet — for each one.
>
> **Three. The work itself is largely re-keying.** Before a pricing actuary can exercise any judgement, someone on the team is transcribing 40+ structured fields per scheme — benefit bases, contribution rates, revaluation rules, commutation factors, exclusions — from paragraphs and tables into a master workbook. That's the bottleneck.
>
> What I'm going to show you today is the same process, running on the Databricks Data Intelligence Platform. The pitch is simple: **raw document to priced scheme-ready data in minutes, not days, with full lineage and a live dashboard the actuarial team can trust.**"

---

## 3. Act I — The Customer Portal (60 sec)

Navigate to **Customers**.

> "This is the front door for the BPA ops team. Six live prospects, each with their own document pipeline."

Click into **BDO Pension Fund**.

Call out on-screen:
- "**New**, **In Review**, **Approved** — same stages your pricing workflow uses today."
- "**Pending Extraction** shows documents that have been dropped into Unity Catalog but haven't been processed yet. This is the only manual touchpoint — everything else is automatic."

**Talking point — UC Volumes.**
> "The files themselves live in a Unity Catalog Volume. That means they're governed, audited, access-controlled by the same catalog that governs your Delta tables, and they're immediately available to any Databricks compute — notebooks, jobs, AI agents, SQL."

---

## 4. Act II — The Speed Run (3 min, the wow moment)

This is the part the customer is watching. Keep narrating while the UI works.

### 4a. Single file extraction (~30s)

1. In "Pending Extraction", click **Extract** on one file (e.g. `bdo_benefit_spec_2024.pdf`).
2. The row flips to **Processing…** with a spinner.

> "Behind that button we're doing three things in one call — and **every step is a native Databricks primitive, no bespoke Python parser on our side:**
> 1. **`ai_parse_document`** reads the PDF directly from the Unity Catalog Volume — Databricks' own document parser handles layout, tables, and text in one SQL call.
> 2. **`ai_extract`** takes that parsed text plus a **document-kind-specific field list** — 10-20 BPA fields chosen for *this* type of document — and returns a structured JSON. Still just SQL, running on a serverless warehouse.
> 3. The structured output lands in our operational store in **Lakebase Postgres**, categorised and confidence-scored, ready for the reviewer."

**Talking point — per-document-kind extraction.**
> "Notice we don't ask the same forty questions of every document. A **benefit spec** gets asked about accrual rate, normal retirement age, pension increase basis, commutation factors. A **triennial valuation** gets asked about discount rates, mortality tables, CMI improvement models. A **funding update** gets asked about technical provisions, scheme assets, funding level. Filename-based classification routes each document to the right BPA schema — so the signal-to-noise on the review screen stays high."

When it flips to **Complete** (takes 15-25s for a 10-page PDF):

> "That's a ten-page benefit spec, structured, categorised, confidence-scored — in twenty seconds."

### 4b. Batch — the real speed run (~90s)

1. Click **Extract all** at the top of the Pending Extraction list.
2. Watch the rows complete in parallel.

> "The actuarial team doesn't deal with one document, they deal with a scheme's worth. So batch is the real test.
>
> What you're watching is `ai_parse_document` and `ai_extract` running concurrently on a serverless SQL warehouse. No separate inference cluster, no queue, no prompt engineering to maintain — Databricks owns the document-AI stack, and we're just calling SQL functions."

**Talking point — the variety story.**
> "Scroll your eye down the batch while it runs. Some of those rows are 10-page triennial valuation PDFs. Some are multi-tab Excel contribution schedules. Some are Word benefit specs. Some are CSV member-options extracts. Whatever your sponsor adviser has emailed over, **the same two SQL functions — `ai_parse_document` and `ai_extract` — handle it.** The actuary doesn't pre-clean anything, and the team doesn't maintain a separate parser for each scheme's favourite template. Variety stops being a bottleneck."

**Talking point — why Databricks AI functions instead of bolting an LLM on.**
> "Three reasons that matter for a regulated insurer:
> 1. **The data never leaves your platform.** Documents, extracted fields, audit trail — all inside your Unity Catalog, your VPC, your governance. The model call is a SQL function, not an outbound API call.
> 2. **No prompt brittleness.** `ai_extract` is Databricks' managed extraction function — they tune the prompt, they handle model upgrades, we just pass a field list. Upgrade path is a platform release, not a codebase rewrite.
> 3. **Cost and latency.** Pay-per-token on the serverless warehouse, no reserved capacity, and the model is co-located with your Delta tables."

---

## 5. Act III — Review (2 min)

Click into one of the newly-extracted documents (the "Review" action).

The Review page has two panels:
- **Left — Source document.** Rendered PDF inline, so the reviewer never leaves the screen. **Lineage is the default** — the field on the right literally knows which source document produced it, and the reviewer never has to hunt for the evidence.
- **Right — Extracted fields.** Grouped into BPA-shaped categories drawn from the scheme itself: *Scheme Details, Benefits, Contributions, Funding Position, Actuarial Assumptions, Membership, Investment Strategy, Investment Performance, Governance, Conditions & Caveats, PPF, GMP Equalisation, Cashflows.* Only the categories that matter for **this** document kind show up — a funding update shows Scheme Details + Funding Position; a benefit spec shows Scheme Details + Benefits + Conditions & Caveats — so the reviewer isn't sifting through empty sections. Every field shows the AI's extracted value with a confidence pill.

Click into one field, change its value (or just toggle "Approved").

> "This is the hardest requirement in BPA: **the AI is fast, but the actuary is accountable.** Every field is editable, every field has a confidence score, every approval is logged against the user and timestamp."

**Talking point — the evidence pack is a by-product.**
> "For an actuarial team this screen is the piece that unlocks sign-off. Every field on the pricing sheet traces back to a source page, a confidence score, a reviewer and an approval timestamp — all in one Delta table in Unity Catalog. **That is the evidence pack for internal second-line review, PRA audit, and trustee reporting — produced as a by-product of the day job, not a separate tidy-up sprint at month-end.** When the auditor asks 'where did this revaluation rule come from', the answer is one row and one click, not a hunt through inboxes."

Click a confidence badge, show the fully-verified category rollup.

Now the speed moment: click **Approve & Sync to Catalog**.

> "Under the hood, that just did three things:
> 1. Marked every field on this document as approved in Lakebase Postgres.
> 2. Updated the document status to *approved*.
> 3. Kicked off a background sync to our governed Delta tables in Unity Catalog — `main.bpa_rubjit.benefit_plans_summary` and `benefit_plans_detail`."

Within a second the UI flips green with **"Approved and synced to Unity Catalog"** and offers two CTAs: **Back to BDO Pension Fund** or **View reporting**.

### 5a. Bulk approve (optional, 20s)

If there are several reviewed docs for one customer:

1. Back to the customer page.
2. In the "In Review" section header, click **Approve all (N)**.

> "For schemes where the AI confidence is high and reviewers are spot-checking, they can bulk-approve an entire batch in one click. Same background sync, one HTTP call, dashboard refresh in seconds."

---

## 6. Act IV — The Dashboard (3 min)

Click **View reporting** (from the success banner) — you land on `/insights`.

Two things on the screen:

### 6a. Operational KPI tiles

Point at the tile row at the top.

> "Four operational KPIs the BPA team can watch every morning: **Approved plans, Customers with data, Awaiting review, Average confidence.** All backed by the same Delta tables we just wrote to — **Error-status extractions are automatically filtered out of this view, so the reviewer and the dashboard always see the clean portfolio.**"

> "The point of this page isn't a static HTML report. The tiles are a header; the real content is the live BI below."

### 6b. Embedded AI/BI Dashboard (the Databricks differentiator)

Scroll to the "Portfolio insights" section. Two tabs: **Databricks AI/BI** (selected) and **Power BI**.

Stay on **Databricks AI/BI** first.

> "This is Databricks' native AI/BI dashboard — **Lakeview** — embedded right inside the app. Same Delta tables, no ETL, no second BI tool, no extra seat cost for actuarial users who just need to look."

Walk through the four bands in order:

1. **Executive KPIs.** "How much have we processed, how many customers active, total fields ingested."
2. **Throughput / Funnel.** "Documents in, extracted, reviewed, approved. The actuarial manager knows where the bottleneck is today."
3. **Per-customer portfolio.** "Pipeline by prospect — which schemes are ready to price, which are stuck in review."
4. **Quality / completeness.** "Average confidence, approval rate, which field categories are the hardest for the model."

**Talking point — live, not static.**
> "Every time someone approves a document, this dashboard updates. No nightly job, no broken dashboards at 9am Monday. It's a query on a Delta table — and the Delta table is 20 seconds behind the extraction."

### 6c. Power BI — same data, customer's tool of choice

Now click the **Power BI** tab in the same section.

> "Because we know not every team lives in Databricks — especially in insurance. This is the **same report, the same Delta tables**, rendered through Power BI and embedded right next to the AI/BI view. Royal London actuarial can keep using Power BI; platform and data engineering run on Databricks. **One source of truth, two BI surfaces, zero duplication.**"

Key messages while the Power BI iframe loads:

- **No data movement.** The Power BI dataset is a DirectQuery into `main.bpa_rubjit.benefit_plans_summary` / `benefit_plans_detail` — the numbers are the same numbers, not a nightly copy.
- **No licensing trap.** If an actuary only needs to *look*, they stay in the BPA app and use the AI/BI tab — no Power BI seat. If they want to drill in Power BI, they're already licensed. The app hosts both.
- **Tab-level deep-link.** The **Open in Power BI** button pops the report into a full Power BI tab for anyone who wants the native Power BI filters and bookmarks.

---

## 7. Act V — Genie AI (2 min, the closer)

Click **Genie AI** in the left sidebar. The embedded space loads automatically (ID `01f13a464fb81f5e921abb671a38c087`, scoped to `main.bpa_rubjit.*`) — no setup required.

> "The last piece. This is **Databricks Genie** — a conversational interface on top of the same Delta tables, embedded directly in the app."

Ask, in the Genie box:

- *"Which schemes have the highest average pension?"*
- *"Show me documents with more than 5 low-confidence fields."*
- *"What's our approval rate by customer this week?"*

> "Genie is text-to-SQL, but governed. It only sees the tables this user is entitled to via Unity Catalog, and every answer comes with the SQL it ran — **the actuary can validate the query before trusting the number.**
>
> For a regulated workflow that's the difference between 'chat with your data' as a marketing line and 'chat with your data' as something audit will sign off on."

---

## 7a. Business impact for the actuarial team (90 sec)

Before the close, pause here and make this explicit. This is the slide the pricing head takes back into their Monday meeting.

> "Put aside the technology for a second. Here's what changes for your actuarial team the week after this is live."

- **Per scheme: days of reading → a few hours of spot-checking.** ~40 structured fields across hundreds of pages per scheme. The actuary signs off; they don't transcribe. Cycle time per scheme is measured in hours of review, not days of re-keying.
- **Variety stops being a bottleneck.** PDF, Excel, Word, CSV — **one extraction pipeline**, not a per-template parser the team has to own and update every time an adviser changes their layout. No "we can't quote this one until someone builds a new template" conversations.
- **Throughput scales in busy season.** Every extraction call is serverless and parallel on the SQL warehouse. The team scales with document volume instead of accumulating a backlog of unread scheme packs through year-end.
- **Quality-of-work shift.** Senior actuaries spend their time on outliers, judgement calls, and negotiation — not on re-keying benefit tables. Junior actuaries learn pricing from day one, not data entry.
- **Defensible by default.** Confidence scores, source pages, reviewer identity and approval timestamps live alongside the numbers in Delta. The evidence pack for internal second-line, PRA audit, and trustee reporting is **built as you go**, not rebuilt every quarter.
- **Consistent interpretation across deals.** Same `ai_extract` function, same field list, same confidence model for every scheme — so two actuaries working in parallel produce the same shape of output, with no drift between personal spreadsheet conventions.

**Where this goes next.**
> "The same pattern applies beyond BPA. Workplace-pension VFM reviews, group-risk claims evidence, M&A acquired-book due diligence packs — anything where a regulated team today is reading unstructured documents and re-keying into a master workbook. **BPA is the first proof point; the platform underneath it is the same.**"

---

## 8. Close — the platform story (60 sec)

Zoom back out. One slide worth of talking points:

| What you saw | The Databricks primitive |
| --- | --- |
| PDFs, Excel, Word ingestion | **Unity Catalog Volumes** — governed file storage |
| Document parsing | **`ai_parse_document`** — managed SQL function, no bespoke PDF pipeline |
| Structured extraction | **`ai_extract`** — managed SQL function, no prompt engineering to maintain |
| Operational store | **Lakebase Postgres** — real transactional workload, same platform |
| Approval & audit | **Delta tables** — time-travel, lineage, row-level governance |
| Live dashboard (Databricks) | **AI/BI Lakeview** — embedded, no license per user |
| Live dashboard (Microsoft) | **Power BI** on DirectQuery — same Delta tables, customer's tool of choice |
| Conversational BI | **Genie** — governed text-to-SQL, embedded in-app |
| Everything above | **One platform, one identity, one audit log** |

> "Three things to leave you with — framed for the actuarial team, not for the platform team:
> - **Days to hours, per scheme.** Same actuarial team, same quality bar, materially more schemes through the door. Cycle time shrinks from days of reading to hours of spot-checking, and the bottleneck moves from data entry to pricing judgement — where you want your actuaries spending their day.
> - **Variety without friction.** Whatever the sponsor adviser sends — PDF, Excel, Word, CSV — one pipeline handles it and produces the same governed output. No per-template parser to maintain, no 'we can't quote that one yet' conversations.
> - **Audit trail is the output, not an afterthought.** Every pricing input carries its source document, source page, confidence, reviewer and approval timestamp into Delta — so internal review, PRA audit and trustee reporting all draw from the same place the actuary does. The evidence pack is a by-product of the day job.
>
> That's what 'Bulk Purchase Annuity on the Data Intelligence Platform' looks like. The next step is picking one real scheme, running the same flow on your own documents, and proving the numbers on live data."

---

## 9. Appendix — Demo hygiene and recovery

### Safe-run checklist (5 min before demo)

- [ ] Hard-refresh the app (Cmd+Shift+R) to pick up the latest build.
- [ ] Top-right of the header reads **"Good morning / afternoon / evening, Ruby"** — confirms the latest build is live.
- [ ] Sidebar reads **Review** (not "Human Review") — secondary confirmation.
- [ ] `Customers` → every customer card loads, no red error banners.
- [ ] `Overview` loads — no "Loading…" spinner stuck on.
- [ ] `Reporting` shows **four tiles** (Approved plans, Customers with data, Awaiting review, Average confidence), **no "Approved benefit plans" table**, and the Portfolio Insights section with **Databricks AI/BI** and **Power BI** tabs directly beneath.
- [ ] `Reporting` — **Databricks AI/BI** tab renders the Lakeview dashboard. If it shows an OAuth prompt, click through once and leave that tab open.
- [ ] `Reporting` — click the **Power BI** tab. If Power BI asks to sign in, sign in once in another tab at [app.powerbi.com](https://app.powerbi.com) and come back; the iframe will then render cleanly.
- [ ] `Genie AI` page loads the pre-provisioned space automatically (no "Connect a Genie Space" empty state). Paste a known-working question and confirm it returns a table.
- [ ] Pick the customer you'll demo: confirm `Pending Extraction` > 3, `In Review` ≥ 1.
- [ ] Customer you'll demo has a **mix of file types** visible in Pending (at least one each of PDF / XLSX / DOCX) — so the "variety of forms" talking point in Section 4 lands on-screen, not just in narration.
- [ ] Open one **benefit spec** and one **funding update** from the Review queue and eyeball the right-hand categories — benefit spec should have *Benefits* / *Conditions & Caveats*, funding update should have only *Funding Position* (plus Scheme Details on both). That proves per-document-kind extraction is wired correctly for the Section 4a talking point.

### If something goes wrong on stage

| Symptom | Recovery |
| --- | --- |
| "Extract" hangs on one file | Click **Back**, pick a different file. Don't retry in front of the customer. Error-status docs are auto-hidden from Reporting so it stays clean. |
| AI/BI iframe is blank | Refresh the page once. If still blank, narrate the KPI tiles and skip to Power BI. |
| Power BI tab shows "Sign in" screen | In a new tab, go to [app.powerbi.com](https://app.powerbi.com) and sign in with the tenant account, then return and refresh. Worst case, click **Open in Power BI** to pop the report out. |
| Genie returns SQL but no rows | Ask it a simpler question (`"how many documents do we have"`). Never edit its SQL live. |
| Genie page shows "Connect a Genie Space" empty state | Hard-refresh (Cmd-Shift-R). If still empty, clear `bpa.genieUrl` from `localStorage` (DevTools → Application → Local Storage) and reload — the server-side `DATABRICKS_GENIE_SPACE_ID` will auto-populate. |
| 502 on a batch extract | Click individual **Extract** on 1-2 files instead, then move on. The background sync is idempotent. |

### Reset between demos

If you want a pristine state for the next customer:
1. In the Databricks workspace, open a SQL editor connected to warehouse `e9b34f7a2e4b0561`.
2. Reset the Lakebase doc state:
   ```sql
   UPDATE main.bpa_rubjit.documents SET status = 'uploaded' WHERE status IN ('approved','review');
   UPDATE main.bpa_rubjit.extracted_fields SET is_approved = FALSE;
   ```
3. Re-run `scripts/deploy_dashboard.py` if the dashboard embed url needs refreshing.

---

## 10. Timing cheatsheet

| Section | Target | Hard cap |
| --- | --- | --- |
| Opening | 1 min | 1:30 |
| Customer portal | 1 min | 1:30 |
| Speed run (single + batch) | 3 min | 4 min |
| Review + approve | 2 min | 3 min |
| Dashboard walkthrough (AI/BI + Power BI) | 3 min | 4:30 |
| Genie | 2 min | 3 min |
| Close | 1 min | 1:30 |
| **Total** | **13 min** | **~19 min** |
