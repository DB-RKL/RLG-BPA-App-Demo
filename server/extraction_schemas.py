"""Per-document-kind extraction schemas for BPA pricing.

The previous single global field list was written in group-risk-insurance
language (premium bands, free cover limit, rehabilitation) and asked the
same 40+ questions of every document regardless of type. This module
replaces it with BPA/DB-pension shaped schemas that are routed per document:

* ``classify_document_kind(filename)`` — substring classifier driven by the
  naming convention in ``mock_data/generate_customer_docs.py``.
* ``EXTRACTION_FIELDS_BY_KIND`` — per-kind subsets of BPA-shaped categories,
  each 8-15 fields so the extraction stays fast and relevant.
* ``get_category_for_field(field_name)`` — resolves any field name in any
  kind's schema back to its canonical category.

The kind-specific categories (``funding_position``, ``actuarial_assumptions``,
``membership``, ``performance``, ``governance``, ``ppf``,
``gmp_equalisation``, ``cashflows``) live here and are referenced by the
frontend for heading labels.
"""

from __future__ import annotations


DEFAULT_DOCUMENT_KIND = "default"


# Classifier patterns. Order matters — more specific patterns must be
# checked first (e.g. ``summary_funding`` before ``funding_update``;
# ``ppf_submission`` before ``sip``).
_KIND_PATTERNS: list[tuple[str, str]] = [
    ("benefit_spec", "benefit_spec"),
    ("bpa_data_pack", "bpa_data_pack"),
    ("summary_funding", "summary_funding"),
    ("triennial_valuation", "triennial_valuation"),
    ("funding_update", "funding_update"),
    ("covenant_review", "covenant_review"),
    ("trustee_minutes", "trustee_minutes"),
    ("risk_register", "risk_register"),
    ("investment_report", "investment_report"),
    ("asset_allocation", "asset_allocation"),
    ("ppf_submission", "ppf_submission"),
    ("gmp_equalisation", "gmp_equalisation"),
    ("cashflow_projection", "cashflow_projection"),
    ("member_data", "member_data"),
    ("member_options", "member_options"),
    ("contribution_schedule", "contribution_schedule"),
    ("sip", "sip"),
    # Legacy fallbacks for older filename conventions.
    ("actuarial", "triennial_valuation"),
    ("contribution", "contribution_schedule"),
]


def classify_document_kind(filename: str | None) -> str:
    """Return a document kind based on substring matching the filename."""
    if not filename:
        return DEFAULT_DOCUMENT_KIND
    name = filename.lower()
    for pattern, kind in _KIND_PATTERNS:
        if pattern in name:
            return kind
    return DEFAULT_DOCUMENT_KIND


# Full field registry. Every field name appears in exactly one category so
# ``get_category_for_field`` is unambiguous. Per-kind schemas below pick
# subsets of these by referring to the same strings.
_FIELD_REGISTRY: dict[str, list[str]] = {
    "scheme_info": [
        "Scheme Name",
        "Scheme Type",
        "Sponsoring Employer",
        "Scheme Year End",
        "Scheme Reference",
        "Effective Date",
        "Report Date",
    ],
    "benefits": [
        "Benefit Accrual Rate",
        "Salary Definition",
        "Normal Retirement Age",
        "Dependants Pension",
        "Pension Increase Basis",
        "Revaluation Rate in Deferment",
        "Commutation Factor",
        "Early Retirement Factor",
        "Late Retirement Factor",
    ],
    "contributions": [
        "Employer Contribution Rate",
        "Member Contribution Rate",
        "Salary Sacrifice Available",
        "Deficit Recovery Contribution",
        "Contribution Review Date",
    ],
    "funding_position": [
        "Valuation Date",
        "Technical Provisions",
        "Scheme Assets",
        "Funding Level",
        "Buy-out Funding Level",
        "Self-Sufficiency Funding Level",
        "Surplus / Deficit",
    ],
    "actuarial_assumptions": [
        "Discount Rate (Pre-Retirement)",
        "Discount Rate (Post-Retirement)",
        "CPI Inflation Assumption",
        "RPI Inflation Assumption",
        "Salary Growth Assumption",
        "Mortality Base Table",
        "CMI Improvement Model",
        "Long-Term Rate of Improvement",
    ],
    "membership": [
        "Active Members Count",
        "Deferred Members Count",
        "Pensioner Members Count",
        "Average Age (Active)",
        "Average Age (Deferred)",
        "Average Age (Pensioner)",
        "Average Pensionable Salary",
        "Total Pensions in Payment",
    ],
    "investment": [
        "Investment Strategy",
        "Default Fund / Growth Portfolio",
        "LDI Interest Rate Hedge Ratio",
        "LDI Inflation Hedge Ratio",
        "Allocation to Growth Assets",
        "Allocation to Matching Assets",
    ],
    "performance": [
        "Total Return QTD",
        "Total Return YTD",
        "Benchmark Return",
        "Excess Return",
        "Top Holding",
    ],
    "governance": [
        "Meeting Date",
        "Quorum Met",
        "Key Decisions",
        "Action Items",
        "Covenant Rating",
        "Sponsor EBITDA",
        "Top Risk",
        "Risk Mitigation",
    ],
    "exclusions": [
        "Trust Deed Reference",
        "Amending Deed Date",
        "Barber Equalisation Date",
        "Benefit Caveats / Discretions",
    ],
    "ppf": [
        "s179 Valuation",
        "PPF Funding Ratio",
        "PPF Levy Band",
        "PPF Levy Amount",
    ],
    "gmp_equalisation": [
        "Equalisation Methodology",
        "Affected Members Count",
        "Benefit Adjustment Range",
        "Implementation Date",
        "Back-Payments Approach",
    ],
    "cashflows": [
        "Projection Horizon",
        "Gross Cashflow Year 1",
        "Gross Cashflow Year 5",
        "Gross Cashflow Year 10",
        "Net Cashflow Year 1",
        "Duration of Liabilities",
    ],
}


# Flat field -> category lookup used by extract.py when persisting rows.
FIELD_TO_CATEGORY: dict[str, str] = {
    field: category
    for category, fields in _FIELD_REGISTRY.items()
    for field in fields
}


def get_category_for_field(field_name: str) -> str:
    return FIELD_TO_CATEGORY.get(field_name, "general")


def _pick(category: str, *names: str) -> list[str]:
    """Return a subset of a category's fields in a stable order, validated
    against the registry so typos fail loudly at import time."""
    available = _FIELD_REGISTRY[category]
    missing = [n for n in names if n not in available]
    if missing:
        raise AssertionError(
            f"Unknown field(s) for category {category!r}: {missing}"
        )
    return list(names)


EXTRACTION_FIELDS_BY_KIND: dict[str, dict[str, list[str]]] = {
    "benefit_spec": {
        "scheme_info": _pick(
            "scheme_info",
            "Scheme Name",
            "Scheme Type",
            "Sponsoring Employer",
            "Effective Date",
        ),
        "benefits": _FIELD_REGISTRY["benefits"],
        "exclusions": _FIELD_REGISTRY["exclusions"],
    },
    "bpa_data_pack": {
        "scheme_info": _pick(
            "scheme_info",
            "Scheme Name",
            "Scheme Type",
            "Sponsoring Employer",
            "Scheme Reference",
        ),
        "benefits": _pick(
            "benefits",
            "Benefit Accrual Rate",
            "Normal Retirement Age",
            "Pension Increase Basis",
            "Revaluation Rate in Deferment",
        ),
        "membership": _FIELD_REGISTRY["membership"],
        "funding_position": _pick(
            "funding_position",
            "Valuation Date",
            "Technical Provisions",
            "Scheme Assets",
            "Funding Level",
            "Buy-out Funding Level",
        ),
    },
    "triennial_valuation": {
        "scheme_info": _pick(
            "scheme_info",
            "Scheme Name",
            "Sponsoring Employer",
            "Scheme Year End",
        ),
        "funding_position": _FIELD_REGISTRY["funding_position"],
        "actuarial_assumptions": _FIELD_REGISTRY["actuarial_assumptions"],
    },
    "summary_funding": {
        "scheme_info": _pick(
            "scheme_info",
            "Scheme Name",
            "Sponsoring Employer",
            "Report Date",
        ),
        "funding_position": _pick(
            "funding_position",
            "Valuation Date",
            "Technical Provisions",
            "Scheme Assets",
            "Funding Level",
            "Surplus / Deficit",
        ),
    },
    "funding_update": {
        "scheme_info": _pick(
            "scheme_info",
            "Scheme Name",
            "Scheme Type",
            "Report Date",
        ),
        "funding_position": _FIELD_REGISTRY["funding_position"],
    },
    "contribution_schedule": {
        "scheme_info": _pick(
            "scheme_info",
            "Scheme Name",
            "Sponsoring Employer",
            "Effective Date",
        ),
        "contributions": _FIELD_REGISTRY["contributions"],
        "membership": _pick(
            "membership",
            "Active Members Count",
            "Deferred Members Count",
            "Pensioner Members Count",
        ),
    },
    "member_data": {
        "scheme_info": _pick(
            "scheme_info",
            "Scheme Name",
            "Report Date",
        ),
        "membership": _FIELD_REGISTRY["membership"],
    },
    "member_options": {
        "scheme_info": _pick(
            "scheme_info",
            "Scheme Name",
            "Effective Date",
        ),
        "benefits": _pick(
            "benefits",
            "Commutation Factor",
            "Early Retirement Factor",
            "Late Retirement Factor",
            "Pension Increase Basis",
            "Revaluation Rate in Deferment",
        ),
    },
    "sip": {
        "scheme_info": _pick(
            "scheme_info",
            "Scheme Name",
            "Scheme Year End",
            "Effective Date",
        ),
        "investment": _FIELD_REGISTRY["investment"],
    },
    "investment_report": {
        "scheme_info": _pick(
            "scheme_info",
            "Scheme Name",
            "Report Date",
        ),
        "investment": _pick(
            "investment",
            "Investment Strategy",
            "Allocation to Growth Assets",
            "Allocation to Matching Assets",
        ),
        "performance": _FIELD_REGISTRY["performance"],
    },
    "asset_allocation": {
        "scheme_info": _pick(
            "scheme_info",
            "Scheme Name",
            "Report Date",
        ),
        "investment": _FIELD_REGISTRY["investment"],
    },
    "trustee_minutes": {
        "scheme_info": _pick(
            "scheme_info",
            "Scheme Name",
            "Sponsoring Employer",
        ),
        "governance": _pick(
            "governance",
            "Meeting Date",
            "Quorum Met",
            "Key Decisions",
            "Action Items",
        ),
    },
    "risk_register": {
        "scheme_info": _pick(
            "scheme_info",
            "Scheme Name",
            "Report Date",
        ),
        "governance": _pick(
            "governance",
            "Top Risk",
            "Risk Mitigation",
            "Action Items",
        ),
    },
    "covenant_review": {
        "scheme_info": _pick(
            "scheme_info",
            "Scheme Name",
            "Sponsoring Employer",
            "Report Date",
        ),
        "governance": _pick(
            "governance",
            "Covenant Rating",
            "Sponsor EBITDA",
            "Key Decisions",
        ),
    },
    "ppf_submission": {
        "scheme_info": _pick(
            "scheme_info",
            "Scheme Name",
            "Sponsoring Employer",
            "Scheme Year End",
        ),
        "funding_position": _pick(
            "funding_position",
            "Valuation Date",
            "Technical Provisions",
            "Scheme Assets",
        ),
        "ppf": _FIELD_REGISTRY["ppf"],
    },
    "gmp_equalisation": {
        "scheme_info": _pick(
            "scheme_info",
            "Scheme Name",
            "Sponsoring Employer",
        ),
        "gmp_equalisation": _FIELD_REGISTRY["gmp_equalisation"],
        "benefits": _pick(
            "benefits",
            "Pension Increase Basis",
            "Revaluation Rate in Deferment",
        ),
    },
    "cashflow_projection": {
        "scheme_info": _pick(
            "scheme_info",
            "Scheme Name",
            "Report Date",
        ),
        "cashflows": _FIELD_REGISTRY["cashflows"],
    },
    # Safety-net fallback for anything the classifier doesn't recognise.
    DEFAULT_DOCUMENT_KIND: {
        "scheme_info": _pick(
            "scheme_info",
            "Scheme Name",
            "Scheme Type",
            "Sponsoring Employer",
            "Effective Date",
        ),
        "benefits": _pick(
            "benefits",
            "Benefit Accrual Rate",
            "Normal Retirement Age",
            "Pension Increase Basis",
            "Commutation Factor",
        ),
    },
}


def field_names_for_kind(kind: str) -> list[str]:
    schema = EXTRACTION_FIELDS_BY_KIND.get(
        kind, EXTRACTION_FIELDS_BY_KIND[DEFAULT_DOCUMENT_KIND]
    )
    out: list[str] = []
    for fields in schema.values():
        out.extend(fields)
    return out
