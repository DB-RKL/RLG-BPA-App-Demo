"""
Generate a Power BI PBIX file for the Royal London BPA Dashboard.
Creates a multi-page report with KPI cards, charts, and tables
bound to the vw_plan_overview, vw_extraction_quality, vw_field_detail,
and vw_category_summary views.
"""

import json
import uuid
import zipfile
import os

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "royal-london-bpa-dashboard.pbix")

# ── Royal London brand colors ──
RL_PURPLE = "#460053"
RL_TEAL = "#056970"
RL_GOLD = "#e9c176"
RL_LIGHT_TEAL = "#9fecf4"
RL_RED = "#ba1a1a"
RL_PURPLE_MID = "#874391"
RL_TEAL_LIGHT = "#86d3da"
RL_GOLD_LIGHT = "#ffdea5"

# ── Table schemas (must match Databricks views exactly) ──
TABLES = {
    "vw_plan_overview": {
        "columns": [
            ("document_id", "int64", "none"),
            ("filename", "string", "none"),
            ("file_type", "string", "none"),
            ("status", "string", "none"),
            ("upload_time", "dateTime", "none"),
            ("days_since_upload", "int64", "sum"),
            ("scheme_name", "string", "none"),
            ("scheme_type", "string", "none"),
            ("underwriter", "string", "none"),
            ("effective_date", "string", "none"),
            ("employer_contribution", "string", "none"),
            ("employee_contribution", "string", "none"),
            ("benefit_level", "string", "none"),
            ("max_benefit_cap", "string", "none"),
            ("deferred_period", "string", "none"),
            ("free_cover_limit", "string", "none"),
            ("total_fields", "int64", "sum"),
            ("approved_fields", "int64", "sum"),
            ("avg_confidence", "double", "average"),
            ("is_fully_reviewed", "boolean", "none"),
            ("confidence_band", "string", "none"),
        ],
    },
    "vw_field_detail": {
        "columns": [
            ("document_id", "int64", "none"),
            ("filename", "string", "none"),
            ("document_status", "string", "none"),
            ("field_name", "string", "none"),
            ("field_category", "string", "none"),
            ("category_label", "string", "none"),
            ("extracted_value", "string", "none"),
            ("reviewed_value", "string", "none"),
            ("final_value", "string", "none"),
            ("confidence", "string", "none"),
            ("confidence_score", "double", "average"),
            ("is_approved", "boolean", "none"),
            ("was_changed_in_review", "boolean", "none"),
        ],
    },
    "vw_extraction_quality": {
        "columns": [
            ("document_id", "int64", "none"),
            ("filename", "string", "none"),
            ("upload_time", "dateTime", "none"),
            ("scheme_name", "string", "none"),
            ("total_fields", "int64", "sum"),
            ("approved_fields", "int64", "sum"),
            ("pct_approved", "double", "average"),
            ("avg_confidence", "double", "average"),
            ("high_confidence_count", "int64", "sum"),
            ("medium_confidence_count", "int64", "sum"),
            ("low_confidence_count", "int64", "sum"),
            ("fields_changed", "int64", "sum"),
            ("pct_changed", "double", "average"),
            ("extraction_accuracy", "double", "average"),
        ],
    },
    "vw_category_summary": {
        "columns": [
            ("document_id", "int64", "none"),
            ("filename", "string", "none"),
            ("field_category", "string", "none"),
            ("category_label", "string", "none"),
            ("expected_fields", "int64", "sum"),
            ("extracted_fields", "int64", "sum"),
            ("populated_fields", "int64", "sum"),
            ("approved_fields", "int64", "sum"),
            ("pct_complete", "double", "average"),
            ("avg_category_confidence", "double", "average"),
        ],
    },
}


def build_data_model_schema() -> str:
    """Build the Tabular Object Model JSON for the DataModelSchema."""
    tables = []
    table_order = []

    for tbl_name, tbl_def in TABLES.items():
        table_order.append(tbl_name)
        columns = []
        for col_name, col_type, summarize in tbl_def["columns"]:
            col = {
                "name": col_name,
                "dataType": col_type,
                "sourceColumn": col_name,
            }
            if summarize != "none":
                col["summarizeBy"] = summarize
            else:
                col["summarizeBy"] = "none"
            columns.append(col)

        # Build M expression for empty typed table
        m_cols = []
        for col_name, col_type, _ in tbl_def["columns"]:
            m_type = {
                "int64": "Int64.Type",
                "string": "Text.Type",
                "double": "Number.Type",
                "dateTime": "DateTime.Type",
                "boolean": "Logical.Type",
            }.get(col_type, "Any.Type")
            m_cols.append(f"[{col_name}] = {m_type}")

        m_expr = [
            "let",
            f'    Source = #table(type table [{", ".join(m_cols)}], {{}})',
            "in",
            "    Source",
        ]

        tables.append(
            {
                "name": tbl_name,
                "columns": columns,
                "partitions": [
                    {
                        "name": tbl_name,
                        "dataView": "full",
                        "source": {"type": "m", "expression": m_expr},
                    }
                ],
            }
        )

    model = {
        "name": "SemanticModel",
        "compatibilityLevel": 1567,
        "model": {
            "culture": "en-US",
            "dataAccessOptions": {
                "legacyRedirects": True,
                "returnErrorValuesAsNull": True,
            },
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "sourceQueryCulture": "en-US",
            "tables": tables,
            "annotations": [
                {
                    "name": "PBI_QueryOrder",
                    "value": json.dumps(table_order),
                },
                {
                    "name": "PBIDesktopVersion",
                    "value": "2.140.1000.0",
                },
                {
                    "name": "__PBI_TimeIntelligenceEnabled",
                    "value": "0",
                },
            ],
        },
    }
    return json.dumps(model, indent=2)


# ── Visual helpers ──

def _uid():
    return str(uuid.uuid4()).replace("-", "")[:16]


def _from_ref(alias: str, entity: str) -> dict:
    return {"Name": alias, "Entity": entity, "Type": 0}


def _col_ref(alias: str, prop: str) -> dict:
    return {
        "Column": {
            "Expression": {"SourceRef": {"Source": alias}},
            "Property": prop,
        }
    }


def _agg_ref(alias: str, prop: str, func: str) -> dict:
    return {
        "Aggregation": {
            "Expression": {
                "Column": {
                    "Expression": {"SourceRef": {"Source": alias}},
                    "Property": prop,
                }
            },
            "Function": {"Count": 0, "CountNonNull": 3, "Sum": 1, "Avg": 4, "Min": 2, "Max": 5}.get(func, 0),
        }
    }


def _card_visual(
    name: str,
    x: float, y: float, w: float, h: float,
    table: str, column: str, agg: str,
    title: str,
    format_string: str = None,
) -> dict:
    alias = table[0]
    query_ref = f"{agg}({table}.{column})"

    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h, "tabOrder": 0}}],
        "singleVisual": {
            "visualType": "card",
            "projections": {"Values": [{"queryRef": query_ref, "active": True}]},
            "prototypeQuery": {
                "Version": 2,
                "From": [_from_ref(alias, table)],
                "Select": [{**_agg_ref(alias, column, agg), "Name": query_ref}],
            },
            "objects": {
                "labels": [{"properties": {"color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{RL_PURPLE}'"}}}}}, "fontSize": {"expr": {"Literal": {"Value": "28D"}}}}}],
                "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#666666'"}}}}}}}],
            },
            "vcObjects": {
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},"fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{RL_PURPLE}'"}}}}}, "fontSize": {"expr": {"Literal": {"Value": "10D"}}}}}],
                "background": [{"properties": {"color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
            },
        },
    }
    return {
        "x": x, "y": y, "z": 0, "width": w, "height": h,
        "config": json.dumps(config),
        "filters": "[]",
    }


def _column_chart_visual(
    name: str,
    x: float, y: float, w: float, h: float,
    table: str, category_col: str, value_col: str, agg: str,
    title: str,
) -> dict:
    alias = table[0]
    cat_qr = f"{table}.{category_col}"
    val_qr = f"{agg}({table}.{value_col})"

    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h, "tabOrder": 0}}],
        "singleVisual": {
            "visualType": "clusteredColumnChart",
            "projections": {
                "Category": [{"queryRef": cat_qr, "active": True}],
                "Y": [{"queryRef": val_qr, "active": True}],
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [_from_ref(alias, table)],
                "Select": [
                    {**_col_ref(alias, category_col), "Name": cat_qr},
                    {**_agg_ref(alias, value_col, agg), "Name": val_qr},
                ],
            },
            "objects": {
                "dataPoint": [{"properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{RL_TEAL}'"}}}}}}},],
            },
            "vcObjects": {
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}, "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{RL_PURPLE}'"}}}}}, "fontSize": {"expr": {"Literal": {"Value": "12D"}}}}}],
                "background": [{"properties": {"color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
            },
        },
    }
    return {
        "x": x, "y": y, "z": 0, "width": w, "height": h,
        "config": json.dumps(config),
        "filters": "[]",
    }


def _table_visual(
    name: str,
    x: float, y: float, w: float, h: float,
    table: str, columns: list[tuple[str, str]],
    title: str,
) -> dict:
    alias = table[0]
    projections = []
    selects = []
    for col_name, display_name in columns:
        qr = f"{table}.{col_name}"
        projections.append({"queryRef": qr, "active": True})
        selects.append({**_col_ref(alias, col_name), "Name": qr})

    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h, "tabOrder": 0}}],
        "singleVisual": {
            "visualType": "tableEx",
            "projections": {"Values": projections},
            "prototypeQuery": {
                "Version": 2,
                "From": [_from_ref(alias, table)],
                "Select": selects,
            },
            "objects": {
                "grid": [{"properties": {"gridVertical": {"expr": {"Literal": {"Value": "true"}}}, "gridVerticalColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E0E0E0'"}}}}}}}],
                "columnHeaders": [{"properties": {"fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}, "backColor": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{RL_PURPLE}'"}}}}}, "fontSize": {"expr": {"Literal": {"Value": "10D"}}}}}],
                "values": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "9D"}}}}}],
            },
            "vcObjects": {
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}, "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{RL_PURPLE}'"}}}}}, "fontSize": {"expr": {"Literal": {"Value": "12D"}}}}}],
                "background": [{"properties": {"color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
            },
        },
    }
    return {
        "x": x, "y": y, "z": 0, "width": w, "height": h,
        "config": json.dumps(config),
        "filters": "[]",
    }


def _donut_visual(
    name: str,
    x: float, y: float, w: float, h: float,
    table: str, category_col: str, value_col: str, agg: str,
    title: str,
) -> dict:
    alias = table[0]
    cat_qr = f"{table}.{category_col}"
    val_qr = f"{agg}({table}.{value_col})"

    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h, "tabOrder": 0}}],
        "singleVisual": {
            "visualType": "donutChart",
            "projections": {
                "Category": [{"queryRef": cat_qr, "active": True}],
                "Y": [{"queryRef": val_qr, "active": True}],
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [_from_ref(alias, table)],
                "Select": [
                    {**_col_ref(alias, category_col), "Name": cat_qr},
                    {**_agg_ref(alias, value_col, agg), "Name": val_qr},
                ],
            },
            "vcObjects": {
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}, "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{RL_PURPLE}'"}}}}}, "fontSize": {"expr": {"Literal": {"Value": "12D"}}}}}],
                "background": [{"properties": {"color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
            },
        },
    }
    return {
        "x": x, "y": y, "z": 0, "width": w, "height": h,
        "config": json.dumps(config),
        "filters": "[]",
    }


def _stacked_bar_visual(
    name: str,
    x: float, y: float, w: float, h: float,
    table: str, category_col: str, value_cols: list[tuple[str, str]],
    title: str,
) -> dict:
    alias = table[0]
    cat_qr = f"{table}.{category_col}"

    y_projections = []
    y_selects = []
    for col_name, agg in value_cols:
        qr = f"{agg}({table}.{col_name})"
        y_projections.append({"queryRef": qr, "active": True})
        y_selects.append({**_agg_ref(alias, col_name, agg), "Name": qr})

    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h, "tabOrder": 0}}],
        "singleVisual": {
            "visualType": "clusteredBarChart",
            "projections": {
                "Category": [{"queryRef": cat_qr, "active": True}],
                "Y": y_projections,
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [_from_ref(alias, table)],
                "Select": [
                    {**_col_ref(alias, category_col), "Name": cat_qr},
                    *y_selects,
                ],
            },
            "vcObjects": {
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}, "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{RL_PURPLE}'"}}}}}, "fontSize": {"expr": {"Literal": {"Value": "12D"}}}}}],
                "background": [{"properties": {"color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
            },
        },
    }
    return {
        "x": x, "y": y, "z": 0, "width": w, "height": h,
        "config": json.dumps(config),
        "filters": "[]",
    }


def _text_visual(name: str, x: float, y: float, w: float, h: float, text: str, font_size: int = 20, color: str = "#FFFFFF", bg_color: str = RL_PURPLE) -> dict:
    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h, "tabOrder": 0}}],
        "singleVisual": {
            "visualType": "textbox",
            "objects": {
                "general": [{"properties": {"paragraphs": {"expr": {"Literal": {"Value": json.dumps([{"textRuns": [{"value": text, "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": f"{font_size}px", "color": color}}]}])}}}}}],
            },
            "vcObjects": {
                "background": [{"properties": {"color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{bg_color}'"}}}}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
            },
        },
    }
    return {
        "x": x, "y": y, "z": 0, "width": w, "height": h,
        "config": json.dumps(config),
        "filters": "[]",
    }


def build_report_layout() -> str:
    """Build the Report/Layout JSON with dashboard pages."""

    # ── Page 1: BPA Scheme Overview ──
    page1_visuals = [
        # Header bar
        _text_visual("header", 0, 0, 1280, 60, "Royal London  |  BPA Scheme Dashboard", 22, "#FFFFFF", RL_PURPLE),

        # KPI Cards row
        _card_visual("kpi_schemes", 20, 80, 295, 130, "vw_plan_overview", "document_id", "Count", "Total Schemes"),
        _card_visual("kpi_fields", 335, 80, 295, 130, "vw_plan_overview", "total_fields", "Sum", "Total Fields Extracted"),
        _card_visual("kpi_approved", 650, 80, 295, 130, "vw_plan_overview", "approved_fields", "Sum", "Fields Approved"),
        _card_visual("kpi_confidence", 965, 80, 295, 130, "vw_plan_overview", "avg_confidence", "Avg", "Avg Confidence Score"),

        # Main table - scheme overview
        _table_visual(
            "scheme_table", 20, 230, 820, 450,
            "vw_plan_overview",
            [
                ("scheme_name", "Scheme Name"),
                ("scheme_type", "Scheme Type"),
                ("status", "Status"),
                ("underwriter", "Underwriter"),
                ("total_fields", "Total Fields"),
                ("approved_fields", "Approved"),
                ("avg_confidence", "Confidence"),
                ("confidence_band", "Band"),
            ],
            "Pension Scheme Overview",
        ),

        # Confidence band donut
        _donut_visual(
            "confidence_donut", 860, 230, 400, 220,
            "vw_plan_overview", "confidence_band", "document_id", "Count",
            "Confidence Distribution",
        ),

        # Status donut
        _donut_visual(
            "status_donut", 860, 460, 400, 220,
            "vw_plan_overview", "status", "document_id", "Count",
            "Processing Status",
        ),
    ]

    # ── Page 2: Extraction Quality ──
    page2_visuals = [
        _text_visual("header2", 0, 0, 1280, 60, "Royal London  |  Extraction Quality Analysis", 22, "#FFFFFF", RL_PURPLE),

        # KPI Cards
        _card_visual("kpi_accuracy", 20, 80, 295, 130, "vw_extraction_quality", "extraction_accuracy", "Avg", "Extraction Accuracy %"),
        _card_visual("kpi_changed", 335, 80, 295, 130, "vw_extraction_quality", "fields_changed", "Sum", "Fields Changed in Review"),
        _card_visual("kpi_high", 650, 80, 295, 130, "vw_extraction_quality", "high_confidence_count", "Sum", "High Confidence Fields"),
        _card_visual("kpi_pctapproved", 965, 80, 295, 130, "vw_extraction_quality", "pct_approved", "Avg", "% Approved"),

        # Confidence distribution stacked bar
        _stacked_bar_visual(
            "confidence_bars", 20, 230, 620, 300,
            "vw_extraction_quality", "scheme_name",
            [("high_confidence_count", "Sum"), ("medium_confidence_count", "Sum"), ("low_confidence_count", "Sum")],
            "Confidence Distribution by Scheme",
        ),

        # Extraction accuracy bar
        _column_chart_visual(
            "accuracy_bar", 660, 230, 600, 300,
            "vw_extraction_quality", "scheme_name", "extraction_accuracy", "Avg",
            "Extraction Accuracy by Scheme",
        ),

        # Quality metrics table
        _table_visual(
            "quality_table", 20, 545, 1240, 150,
            "vw_extraction_quality",
            [
                ("scheme_name", "Scheme"),
                ("total_fields", "Total Fields"),
                ("approved_fields", "Approved"),
                ("pct_approved", "% Approved"),
                ("high_confidence_count", "High"),
                ("medium_confidence_count", "Medium"),
                ("low_confidence_count", "Low"),
                ("fields_changed", "Changed"),
                ("extraction_accuracy", "Accuracy %"),
            ],
            "Extraction Quality Metrics",
        ),
    ]

    # ── Page 3: Category Completeness ──
    page3_visuals = [
        _text_visual("header3", 0, 0, 1280, 60, "Royal London  |  Category Completeness", 22, "#FFFFFF", RL_PURPLE),

        # Category completeness bar chart
        _column_chart_visual(
            "cat_complete_bar", 20, 80, 620, 300,
            "vw_category_summary", "category_label", "pct_complete", "Avg",
            "Completeness by Category (%)",
        ),

        # Category confidence bar
        _column_chart_visual(
            "cat_confidence_bar", 660, 80, 600, 300,
            "vw_category_summary", "category_label", "avg_category_confidence", "Avg",
            "Avg Confidence by Category",
        ),

        # Category detail table
        _table_visual(
            "cat_table", 20, 400, 1240, 290,
            "vw_category_summary",
            [
                ("category_label", "Category"),
                ("filename", "Document"),
                ("expected_fields", "Expected"),
                ("extracted_fields", "Extracted"),
                ("populated_fields", "Populated"),
                ("approved_fields", "Approved"),
                ("pct_complete", "% Complete"),
                ("avg_category_confidence", "Avg Confidence"),
            ],
            "Category Detail",
        ),
    ]

    # ── Page 4: Field Detail ──
    page4_visuals = [
        _text_visual("header4", 0, 0, 1280, 60, "Royal London  |  Field-Level Detail", 22, "#FFFFFF", RL_PURPLE),

        # Changed in review donut
        _donut_visual(
            "changed_donut", 20, 80, 400, 250,
            "vw_field_detail", "was_changed_in_review", "document_id", "Count",
            "Fields Changed in Review",
        ),

        # Confidence by category
        _column_chart_visual(
            "field_conf_bar", 440, 80, 420, 250,
            "vw_field_detail", "category_label", "confidence_score", "Avg",
            "Avg Confidence by Category",
        ),

        # Approval by category
        _column_chart_visual(
            "field_approval_bar", 880, 80, 380, 250,
            "vw_field_detail", "confidence", "document_id", "Count",
            "Fields by Confidence Level",
        ),

        # Full detail table
        _table_visual(
            "field_table", 20, 350, 1240, 340,
            "vw_field_detail",
            [
                ("filename", "Document"),
                ("category_label", "Category"),
                ("field_name", "Field"),
                ("extracted_value", "AI Extracted"),
                ("final_value", "Final Value"),
                ("confidence", "Confidence"),
                ("is_approved", "Approved"),
                ("was_changed_in_review", "Changed"),
            ],
            "All Extracted Fields",
        ),
    ]

    def _page(name: str, display_name: str, ordinal: int, visuals: list) -> dict:
        return {
            "name": name,
            "displayName": display_name,
            "filters": "[]",
            "ordinal": ordinal,
            "visualContainers": visuals,
            "config": json.dumps({
                "name": name,
                "layouts": [{"id": 0, "position": {"x": 0, "y": 0, "width": 1280, "height": 720}}],
            }),
            "displayOption": 2,
            "width": 1280,
            "height": 720,
        }

    layout = {
        "id": 0,
        "resourcePackages": [
            {
                "resourcePackage": {
                    "name": "SharedResources",
                    "type": 2,
                    "items": [
                        {"type": 202, "path": "BaseThemes/CY24SU06.json", "name": "CY24SU06"},
                    ],
                    "disabled": False,
                },
            }
        ],
        "sections": [
            _page("ReportSection_Overview", "BPA Scheme Overview", 0, page1_visuals),
            _page("ReportSection_Quality", "Extraction Quality", 1, page2_visuals),
            _page("ReportSection_Categories", "Category Completeness", 2, page3_visuals),
            _page("ReportSection_Fields", "Field Detail", 3, page4_visuals),
        ],
        "config": json.dumps({
            "version": "5.55",
            "themeCollection": {
                "baseTheme": {"name": "CY24SU06", "version": "5.55", "type": 2},
            },
            "activeSectionIndex": 0,
            "defaultDrillFilterOtherVisuals": True,
            "linguisticSchemaSyncVersion": 2,
            "settings": {
                "useStylableVisualContainerHeader": True,
                "exportDataMode": 1,
            },
        }),
        "layoutOptimization": 0,
    }

    return json.dumps(layout, indent=2)


def build_content_types() -> str:
    return """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/DataModelSchema" ContentType=""/>
  <Override PartName="/Report/Layout" ContentType="application/json"/>
  <Override PartName="/Settings" ContentType="application/json"/>
  <Override PartName="/Metadata" ContentType="application/json"/>
  <Override PartName="/DiagramState" ContentType="application/json"/>
  <Override PartName="/Version" ContentType="text/plain"/>
  <Override PartName="/SecurityBindings" ContentType=""/>
  <Override PartName="/DiagramLayout" ContentType="application/json"/>
</Types>"""


def build_metadata() -> str:
    return json.dumps({"version": "1.0", "createdFrom": "api"})


def build_settings() -> str:
    return json.dumps({"version": "3.0"})


def build_diagram_state() -> str:
    return json.dumps({"version": "1.0", "diagrams": []})


def build_rels() -> str:
    """Build OPC root relationships file."""
    return """<?xml version="1.0" encoding="utf-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Type="http://schemas.microsoft.com/DataModelSchema" Target="/DataModelSchema" Id="R1"/>
  <Relationship Type="http://schemas.microsoft.com/ReportLayout" Target="/Report/Layout" Id="R2"/>
  <Relationship Type="http://schemas.microsoft.com/Settings" Target="/Settings" Id="R3"/>
  <Relationship Type="http://schemas.microsoft.com/Metadata" Target="/Metadata" Id="R4"/>
  <Relationship Type="http://schemas.microsoft.com/DiagramState" Target="/DiagramState" Id="R5"/>
  <Relationship Type="http://schemas.microsoft.com/DiagramLayout" Target="/DiagramLayout" Id="R6"/>
  <Relationship Type="http://schemas.microsoft.com/SecurityBindings" Target="/SecurityBindings" Id="R7"/>
  <Relationship Type="http://schemas.microsoft.com/Version" Target="/Version" Id="R8"/>
</Relationships>"""


def create_pbix():
    print(f"Generating PBIX: {OUTPUT_PATH}")

    with zipfile.ZipFile(OUTPUT_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        # OPC relationships
        zf.writestr("_rels/.rels", build_rels())
        zf.writestr("[Content_Types].xml", build_content_types())
        # DataModelSchema - UTF-16LE with BOM (Power BI requirement)
        schema_json = build_data_model_schema()
        schema_bytes = b"\xff\xfe" + schema_json.encode("utf-16-le")
        zf.writestr("DataModelSchema", schema_bytes)
        # Report layout - UTF-8
        zf.writestr("Report/Layout", build_report_layout())
        zf.writestr("Metadata", build_metadata())
        zf.writestr("Settings", build_settings())
        zf.writestr("DiagramState", build_diagram_state())
        zf.writestr("DiagramLayout", json.dumps({"version": "1.0", "diagrams": []}))
        zf.writestr("Version", "2.140.1000.0")
        # SecurityBindings - empty
        zf.writestr("SecurityBindings", b"")

    size_kb = os.path.getsize(OUTPUT_PATH) / 1024
    print(f"Done. Size: {size_kb:.1f} KB")
    return OUTPUT_PATH


if __name__ == "__main__":
    create_pbix()
