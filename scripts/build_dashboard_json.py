#!/usr/bin/env python3
"""Generate dashboards/bpa_reporting.lvdash.json using the Lakeview builder.

Run standalone: `python scripts/build_dashboard_json.py`
The output is the `serialized_dashboard` payload used by deploy_dashboard.py.
"""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL_RESOURCES = Path(
    "/Users/rubjit.lalli/.claude/plugins/cache/fe-vibe/fe-databricks-tools/1.0.3/"
    "skills/databricks-lakeview-dashboard/resources"
)
sys.path.insert(0, str(SKILL_RESOURCES))

from lakeview_builder import LakeviewDashboard  # noqa: E402

CATALOG = "main"
SCHEMA = "bpa_rubjit"

PORTFOLIO = f"{CATALOG}.{SCHEMA}.vw_portfolio_overview"
FIELDS = f"{CATALOG}.{SCHEMA}.vw_field_detail"
CATEGORY = f"{CATALOG}.{SCHEMA}.vw_category_summary"

ROYAL_PURPLE = "#450350"
PALETTE = [ROYAL_PURPLE, "#8A4C91", "#C6A3CE", "#FFAB00", "#00A972", "#8BCAE7"]


def counter_widget(
    dataset_name: str,
    expression: str,
    field_label: str,
    title: str,
    number_format: str | None = None,
) -> dict:
    """Build a counter widget with a raw SQL expression.

    The builder's `add_counter` only supports SUM/AVG/COUNT/MIN/MAX; we need
    COUNT(DISTINCT ...) and arithmetic. Emit the widget dict directly.
    """
    wid = uuid.uuid4().hex[:8]
    value_encoding = {
        "fieldName": field_label,
        "displayName": title,
    }
    if number_format:
        value_encoding["format"] = {"type": "number-plain", "decimalPlaces": {"type": "exact", "places": 0}}
    return {
        "name": wid,
        "queries": [
            {
                "name": "main_query",
                "query": {
                    "datasetName": dataset_name,
                    "fields": [{"name": field_label, "expression": expression}],
                    "disaggregated": True,
                },
            }
        ],
        "spec": {
            "version": 2,
            "widgetType": "counter",
            "encodings": {"value": value_encoding},
            "frame": {"showTitle": True, "title": title},
        },
    }


def build() -> LakeviewDashboard:
    dash = LakeviewDashboard("BPA Portfolio Insights")

    dash.add_dataset("portfolio", "Portfolio Overview", f"SELECT * FROM {PORTFOLIO}")
    dash.add_dataset("fields", "Field Detail", f"SELECT * FROM {FIELDS}")
    dash.add_dataset("category", "Category Completeness", f"SELECT * FROM {CATEGORY}")

    page = dash.pages[0]

    # ------------------------------------------------------------------
    # Band 1 - Executive KPIs (rows y=0 and y=3, each height 3)
    # ------------------------------------------------------------------
    page["layout"].extend(
        [
            {
                "widget": counter_widget(
                    "portfolio",
                    "COUNT(`document_id`)",
                    "plans_approved",
                    "Plans approved",
                ),
                "position": {"x": 0, "y": 0, "width": 2, "height": 3},
            },
            {
                "widget": counter_widget(
                    "portfolio",
                    "COUNT(DISTINCT `customer`)",
                    "customers_covered",
                    "Customers covered",
                ),
                "position": {"x": 2, "y": 0, "width": 2, "height": 3},
            },
            {
                "widget": counter_widget(
                    "portfolio",
                    "SUM(`approved_fields`)",
                    "fields_approved",
                    "Fields approved",
                ),
                "position": {"x": 4, "y": 0, "width": 2, "height": 3},
            },
            {
                "widget": counter_widget(
                    "portfolio",
                    "ROUND(AVG(`avg_confidence`) * 100, 1)",
                    "avg_confidence_pct",
                    "Avg extraction confidence (%)",
                ),
                "position": {"x": 0, "y": 3, "width": 2, "height": 3},
            },
            {
                "widget": counter_widget(
                    "portfolio",
                    "ROUND(AVG(`extraction_accuracy`), 1)",
                    "accuracy_pct",
                    "AI extraction accuracy (%)",
                ),
                "position": {"x": 2, "y": 3, "width": 2, "height": 3},
            },
            {
                "widget": counter_widget(
                    "portfolio",
                    "SUM(`fields_changed`)",
                    "fields_changed",
                    "Fields changed in review",
                ),
                "position": {"x": 4, "y": 3, "width": 2, "height": 3},
            },
        ]
    )

    # ------------------------------------------------------------------
    # Band 2 - Throughput + confidence mix (y=6, height 5)
    # ------------------------------------------------------------------
    dash.add_line_chart(
        dataset_name="portfolio",
        x_field="upload_time",
        y_field="document_id",
        y_agg="COUNT",
        time_grain="WEEK",
        title="Plans approved per week",
        color_field="confidence_band",
        position={"x": 0, "y": 6, "width": 4, "height": 5},
    )
    dash.add_bar_chart(
        dataset_name="portfolio",
        x_field="confidence_band",
        y_field="document_id",
        y_agg="COUNT",
        title="Confidence distribution",
        colors=[ROYAL_PURPLE, "#8A4C91", "#C6A3CE"],
        position={"x": 4, "y": 6, "width": 2, "height": 5},
    )

    # ------------------------------------------------------------------
    # Band 3 - Customer portfolio (y=11, height 5)
    # ------------------------------------------------------------------
    dash.add_bar_chart(
        dataset_name="portfolio",
        x_field="customer",
        y_field="document_id",
        y_agg="COUNT",
        title="Plans per customer",
        color_field="confidence_band",
        colors=PALETTE,
        sort_descending=True,
        position={"x": 0, "y": 11, "width": 3, "height": 5},
    )
    dash.add_bar_chart(
        dataset_name="portfolio",
        x_field="customer",
        y_field="extraction_accuracy",
        y_agg="AVG",
        title="Extraction accuracy by customer (%)",
        colors=[ROYAL_PURPLE],
        sort_descending=True,
        position={"x": 3, "y": 11, "width": 3, "height": 5},
    )

    # ------------------------------------------------------------------
    # Band 4 - Quality and completeness (y=16, height 5)
    # ------------------------------------------------------------------
    dash.add_bar_chart(
        dataset_name="fields",
        x_field="category_label",
        y_field="was_changed_in_review",
        y_agg="AVG",
        title="Review edit rate by category",
        colors=["#FFAB00"],
        sort_descending=True,
        position={"x": 0, "y": 16, "width": 3, "height": 5},
    )
    dash.add_bar_chart(
        dataset_name="category",
        x_field="category_label",
        y_field="pct_complete",
        y_agg="AVG",
        title="Category completeness (%)",
        colors=["#00A972"],
        sort_descending=True,
        position={"x": 3, "y": 16, "width": 3, "height": 5},
    )

    return dash


def main() -> None:
    dash = build()
    out = REPO / "dashboards" / "bpa_reporting.lvdash.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dash.to_dict(), indent=2))
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
