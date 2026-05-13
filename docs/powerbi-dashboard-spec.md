# Power BI Dashboard Design Specification

## Data Sources (Views in `main.bpa_rubjit`)

| View                    | Alias in Power BI  | Grain                      |
|-------------------------|--------------------|-----------------------------|
| `vw_plan_overview`      | Plans              | One row per document        |
| `vw_field_detail`       | Fields             | One row per extracted field |
| `vw_extraction_quality` | Quality            | One row per document        |
| `vw_category_summary`   | Categories         | One row per doc x category  |

---

## DAX Measures

Create these in a dedicated "Measures" table:

```dax
Total Plans = COUNTROWS(Plans)

Avg Confidence = AVERAGE(Plans[avg_confidence])

Fully Reviewed % = 
    DIVIDE(
        COUNTROWS(FILTER(Plans, Plans[is_fully_reviewed] = TRUE)),
        COUNTROWS(Plans)
    )

Total Fields Extracted = SUM(Quality[total_fields])

Extraction Accuracy = AVERAGE(Quality[extraction_accuracy])

Fields Changed = SUM(Quality[fields_changed])

High Confidence % = 
    DIVIDE(
        SUM(Quality[high_confidence_count]),
        SUM(Quality[total_fields])
    )

Category Completeness = AVERAGE(Categories[pct_complete])
```

---

## Page 1: Executive Summary

**Purpose**: At-a-glance health of the BPA pipeline.

### Layout (top to bottom, left to right)

**Row 1 -- KPI cards** (4 cards across the top)

| Card               | Measure / Field          | Format     |
|---------------------|--------------------------|------------|
| Total Plans         | `Total Plans`            | Integer    |
| Avg Confidence      | `Avg Confidence`         | Percentage |
| Fully Reviewed %    | `Fully Reviewed %`       | Percentage |
| Extraction Accuracy | `Extraction Accuracy`    | Percentage |

**Row 2 -- Left (60% width): Plan Overview Table**

| Column            | Source                         |
|-------------------|--------------------------------|
| Scheme Name       | `Plans[scheme_name]`           |
| Scheme Type       | `Plans[scheme_type]`           |
| Underwriter       | `Plans[underwriter]`           |
| Effective Date    | `Plans[effective_date]`        |
| Confidence Band   | `Plans[confidence_band]`       |
| Days Since Upload | `Plans[days_since_upload]`     |

Conditional formatting: confidence_band as background colour (High = green, Medium = amber, Low = red).

**Row 2 -- Right (40% width): Donut Chart**

- **Values**: Count of `Plans[document_id]`
- **Legend**: `Plans[scheme_type]`
- **Title**: "Plans by Scheme Type"

**Row 3 -- Stacked Bar Chart**

- **Axis**: `Plans[status]`
- **Values**: Count of `Plans[document_id]`
- **Title**: "Document Pipeline Status"

---

## Page 2: Extraction Quality

**Purpose**: How well the AI extraction is performing.

### Layout

**Row 1 -- KPI cards** (3 cards)

| Card                 | Measure                 | Format     |
|----------------------|-------------------------|------------|
| Extraction Accuracy  | `Extraction Accuracy`   | Percentage |
| Fields Changed       | `Fields Changed`        | Integer    |
| High Confidence %    | `High Confidence %`     | Percentage |

**Row 2 -- Left: Clustered Bar Chart**

- **Axis**: `Quality[filename]`
- **Values**: `Quality[high_confidence_count]`, `Quality[medium_confidence_count]`, `Quality[low_confidence_count]`
- **Legend**: Series names (High / Medium / Low)
- **Colours**: High = #056970 (teal), Medium = #e9c176 (gold), Low = #ba1a1a (red)
- **Title**: "Confidence Distribution by Document"

**Row 2 -- Right: Heat Map (Matrix)**

- **Rows**: `Fields[category_label]`
- **Columns**: `Fields[confidence]`
- **Values**: Count of `Fields[field_name]`
- **Conditional formatting**: Background colour scale (low count = light, high count = dark)
- **Title**: "Confidence by Category"

**Row 3 -- Line Chart**

- **Axis**: `Quality[upload_time]` (Date)
- **Values**: `Quality[avg_confidence]`
- **Title**: "Confidence Trend Over Time"

---

## Page 3: Benefit Plan Details

**Purpose**: Drill into specific documents and categories.

### Layout

**Top: Slicers row**

| Slicer           | Source                    | Type     |
|------------------|---------------------------|----------|
| Document         | `Plans[filename]`         | Dropdown |
| Scheme Type      | `Plans[scheme_type]`      | Buttons  |
| Underwriter      | `Plans[underwriter]`      | Dropdown |

**Left (50%): Matrix -- Category Completeness**

- **Rows**: `Categories[category_label]`
- **Columns**: (none -- flat table)
- **Values**: `Categories[expected_fields]`, `Categories[populated_fields]`, `Categories[pct_complete]`, `Categories[avg_category_confidence]`
- **Conditional formatting**: `pct_complete` as data bars; `avg_category_confidence` as background colour scale
- **Title**: "Extraction Completeness by Category"

**Right (50%): Detail Table**

| Column           | Source                          | Notes                          |
|------------------|---------------------------------|--------------------------------|
| Field Name       | `Fields[field_name]`            |                                |
| Category         | `Fields[category_label]`        |                                |
| Final Value      | `Fields[final_value]`           |                                |
| Confidence       | `Fields[confidence]`            | Icon set (tick/dash/cross)     |
| Changed?         | `Fields[was_changed_in_review]` | Conditional: red if TRUE       |

- **Title**: "Extracted Fields"
- Responds to slicer selections

---

## Page 4: Contribution and Rate Analysis

**Purpose**: Compare contribution rates and premium bands across plans.

### Layout

**Top: Grouped Bar Chart**

- **Axis**: `Plans[scheme_name]`
- **Values**: `Plans[employer_contribution]`, `Plans[employee_contribution]`
- **Title**: "Employer vs Employee Contribution Rates"
- Note: These are string fields; may need a DAX measure to parse numeric values:

```dax
Employer Rate Numeric = 
    VALUE(SUBSTITUTE(Plans[employer_contribution], "%", ""))
```

**Middle: Table -- Premium Rate Bands**

Filter `Fields` to `field_category = 'premium_rates'` and pivot:

| Column          | Source                                                   |
|-----------------|----------------------------------------------------------|
| Scheme Name     | `Plans[scheme_name]` (via relationship)                  |
| Under 30        | Filter `field_name = 'Rate - Under 30'`, show final_value|
| 30-39           | Filter `field_name = 'Rate - Age 30-39'`                 |
| 40-49           | Filter `field_name = 'Rate - Age 40-49'`                 |
| 50-59           | Filter `field_name = 'Rate - Age 50-59'`                 |
| 60+             | Filter `field_name = 'Rate - Age 60+'`                   |
| Free Cover Limit| Filter `field_name = 'Free Cover Limit'`                 |

Use a Matrix visual with `Plans[scheme_name]` as rows and `Fields[field_name]` as columns, filtered to `premium_rates` category.

**Bottom: KPI Cards** (3 cards)

| Card              | Logic                                              |
|-------------------|----------------------------------------------------|
| Avg Free Cover    | AVERAGE of `Plans[free_cover_limit]` (parse number)|
| Avg Benefit Cap   | AVERAGE of `Plans[max_benefit_cap]` (parse number) |
| Plans with Rates  | Count of plans where any premium rate is populated  |

---

## Page 5: Review Workflow

**Purpose**: Track the human review process and measure AI-vs-human agreement.

### Layout

**Top Left: Funnel Chart**

- **Group**: Pipeline stage (manually defined as: Uploaded > Extracting > In Review > Approved)
- **Values**: Count of documents per stage
- **Title**: "Document Pipeline Funnel"

Note: Since `vw_plan_overview` only contains approved documents, supplement with a measure that counts from the BPA app's status field if needed. Otherwise show the funnel as a static reference.

**Top Right: KPI Cards**

| Card                  | Measure                                |
|-----------------------|----------------------------------------|
| Fields Changed        | `Fields Changed`                       |
| % Changed             | `AVERAGE(Quality[pct_changed])`        |
| Avg Days to Approval  | `AVERAGE(Plans[days_since_upload])`    |

**Bottom: Table -- Fields Changed in Review**

Filter `Fields` where `was_changed_in_review = TRUE`:

| Column          | Source                        |
|-----------------|-------------------------------|
| Document        | `Fields[filename]`            |
| Field Name      | `Fields[field_name]`          |
| Category        | `Fields[category_label]`      |
| AI Extracted    | `Fields[extracted_value]`     |
| Reviewer Value  | `Fields[reviewed_value]`      |
| Confidence      | `Fields[confidence]`          |

Conditional formatting: highlight rows where confidence was "high" but value was still changed (indicates potential AI error pattern).

- **Title**: "Fields Modified During Review"

---

## Theme and Branding

Apply a custom Power BI theme JSON to match the BPA app:

```json
{
  "name": "Royal London BPA",
  "dataColors": [
    "#460053",
    "#056970",
    "#e9c176",
    "#9fecf4",
    "#ba1a1a",
    "#874391",
    "#86d3da",
    "#ffdea5"
  ],
  "background": "#f9f9f9",
  "foreground": "#1a1c1c",
  "tableAccent": "#460053",
  "visualStyles": {
    "*": {
      "*": {
        "general": [{
          "responsive": true,
          "keepLayerOrder": true
        }],
        "title": [{
          "fontColor": { "solid": { "color": "#1a1c1c" } },
          "fontFamily": "Segoe UI Semibold",
          "fontSize": 12
        }]
      }
    }
  }
}
```

Save as `royal-london-bpa.json` and apply via **View > Themes > Browse for Themes** in Power BI Desktop.
