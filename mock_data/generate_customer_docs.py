"""Generate a realistic, branded mock corpus for 6 UK BPA customer prospects.

Each customer gets ~80 documents spread across 2021-2025 covering 16+ document
types (triennial valuations, investment reports, trustee minutes, SIP, covenant
reviews, member data, benefit specs, etc.). Core PDFs are 10 pages, branded
with the Royal London logo, and vary deterministically year-on-year.

Usage:
    python3 mock_data/generate_customer_docs.py              # generate locally
    python3 mock_data/generate_customer_docs.py --upload     # also sync to UC Volume
"""

from __future__ import annotations

import csv
import os
import random
import sys
from dataclasses import dataclass
from typing import Any, Callable


OUTPUT_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.abspath(
    os.path.join(OUTPUT_DIR, "..", "frontend", "public", "royal-london-logo.png")
)

VOLUME_PATH = "/Volumes/main/bpa_rubjit/documents"
YEARS = [2021, 2022, 2023, 2024, 2025]


def _ensure(pkg: str, pip_name: str | None = None):
    try:
        return __import__(pkg)
    except ImportError:
        os.system(f"{sys.executable} -m pip install {pip_name or pkg} >/dev/null 2>&1")
        return __import__(pkg)


# -------- Brand ----------
RL_PURPLE = (70, 3, 80)
RL_PURPLE_LIGHT = (245, 238, 251)
RL_TEAL = (5, 105, 112)
RL_DARK = (26, 28, 28)
RL_GRAY = (100, 100, 110)
RL_PURPLE_HEX = "460350"
RL_TEAL_HEX = "056970"
RL_DARK_HEX = "1A1C1C"

FOOTER_LEGAL = (
    "The Royal London Mutual Insurance Society Limited is authorised by the "
    "Prudential Regulation Authority and regulated by the Financial Conduct "
    "Authority and the Prudential Regulation Authority. Registration number "
    "117672. Registered in England and Wales, company number 99064. "
    "Registered office: 80 Fenchurch Street, London, EC3M 4BY."
)


# -------- Customers ----------
@dataclass
class Customer:
    slug: str
    display: str
    sponsor: str
    sector: str
    scheme_type: str
    status: str
    active: int
    deferred: int
    pensioners: int
    total_liability_m: float
    assets_m: float
    funding_level: float
    valuation_date: str
    accrual_rate: str
    nra: str
    spouse_pension: str
    indexation: str
    revaluation: str
    employer_contribution: str
    deficit_contribution: str
    ppf_levy: str
    bpa_premium_m: float
    trustee: str
    actuary: str
    admin: str
    investment_mgr: str


CUSTOMERS: list[Customer] = [
    Customer(
        slug="bdo", display="BDO Pension Fund", sponsor="BDO LLP",
        sector="Professional Services (Accountancy)",
        scheme_type="Defined Benefit - Final Salary (Closed)",
        status="Closed to new entrants and future accrual",
        active=0, deferred=780, pensioners=1020,
        total_liability_m=198.4, assets_m=184.2, funding_level=92.8,
        valuation_date="31/03/2024",
        accrual_rate="1/60th of Final Pensionable Salary per year of service",
        nra="65", spouse_pension="50% of member's pension",
        indexation="CPI capped at 5% p.a. (RPI min 3% for pre-1997 service)",
        revaluation="CPI capped at 2.5% p.a. in deferment",
        employer_contribution="N/A (closed to accrual)",
        deficit_contribution="GBP 6.2m per annum until 31/03/2029",
        ppf_levy="GBP 185,400", bpa_premium_m=205.0,
        trustee="BDO Pension Fund Trustee Limited",
        actuary="Mercer Limited", admin="XPS Pensions", investment_mgr="LGIM",
    ),
    Customer(
        slug="renishaw", display="Renishaw plc Pension Scheme", sponsor="Renishaw plc",
        sector="Precision Engineering & Metrology",
        scheme_type="Defined Benefit - Career Average (CARE)",
        status="Closed to new entrants; open to future accrual for existing members",
        active=210, deferred=640, pensioners=550,
        total_liability_m=178.9, assets_m=171.3, funding_level=95.8,
        valuation_date="31/12/2023",
        accrual_rate="1/80th of Pensionable Earnings per year of service (revalued CPI)",
        nra="65", spouse_pension="50% of member's pension",
        indexation="CPI capped at 2.5% p.a. (2.5% flat for pre-2006 service)",
        revaluation="CPI capped at 2.5% p.a. in deferment",
        employer_contribution="22.4% of Pensionable Earnings",
        deficit_contribution="GBP 3.8m per annum until 31/12/2027",
        ppf_levy="GBP 124,700", bpa_premium_m=185.0,
        trustee="Renishaw Pension Trustees Limited",
        actuary="Willis Towers Watson", admin="Aptia", investment_mgr="BlackRock",
    ),
    Customer(
        slug="reading_university", display="University of Reading Pension Scheme",
        sponsor="University of Reading", sector="Higher Education",
        scheme_type="Defined Benefit - Final Salary (Closed)",
        status="Closed to new entrants (2011) and future accrual (2016)",
        active=0, deferred=310, pensioners=290,
        total_liability_m=89.6, assets_m=86.1, funding_level=96.1,
        valuation_date="31/07/2023",
        accrual_rate="1/80th of Final Pensionable Salary per year of service",
        nra="65", spouse_pension="50% of member's pension",
        indexation="CPI capped at 5% p.a.",
        revaluation="Statutory (CPI capped at 2.5% p.a.)",
        employer_contribution="N/A (closed to accrual)",
        deficit_contribution="GBP 1.4m per annum until 31/07/2028",
        ppf_levy="GBP 68,200", bpa_premium_m=92.0,
        trustee="University of Reading Pension Trustee Limited",
        actuary="Hymans Robertson", admin="Barnett Waddingham", investment_mgr="Schroders",
    ),
    Customer(
        slug="thames_water", display="Thames Water UPS (Closed Section)",
        sponsor="Thames Water Utilities Limited", sector="Utilities & Infrastructure",
        scheme_type="Defined Benefit - Final Salary (Closed Section)",
        status="Section closed to new entrants (2011); open to accrual for existing members",
        active=420, deferred=880, pensioners=700,
        total_liability_m=248.1, assets_m=231.7, funding_level=93.4,
        valuation_date="31/03/2024",
        accrual_rate="1/60th of Final Pensionable Salary per year of service",
        nra="63", spouse_pension="60% of member's pension (enhanced)",
        indexation="CPI capped at 5% p.a. (RPI capped at 5% for pre-2011 service)",
        revaluation="CPI capped at 2.5% p.a. in deferment",
        employer_contribution="26.8% of Pensionable Pay",
        deficit_contribution="GBP 8.4m per annum until 31/03/2031",
        ppf_levy="GBP 218,900", bpa_premium_m=255.0,
        trustee="Thames Water Pension Trustee Limited",
        actuary="Aon", admin="Capita Pensions", investment_mgr="LGIM",
    ),
    Customer(
        slug="spirax_sarco", display="Spirax-Sarco Engineering Pension Plan",
        sponsor="Spirax-Sarco Engineering plc",
        sector="Industrial Engineering (Thermal & Steam)",
        scheme_type="Defined Benefit - Final Salary (Closed)",
        status="Closed to new entrants (2008) and future accrual (2017)",
        active=0, deferred=520, pensioners=580,
        total_liability_m=152.7, assets_m=149.0, funding_level=97.6,
        valuation_date="31/12/2023",
        accrual_rate="1/60th of Final Pensionable Salary per year of service",
        nra="65", spouse_pension="50% of member's pension",
        indexation="CPI capped at 5% p.a.",
        revaluation="CPI capped at 5% p.a. in deferment (statutory)",
        employer_contribution="N/A (closed to accrual)",
        deficit_contribution="GBP 2.1m per annum until 31/12/2026",
        ppf_levy="GBP 98,400", bpa_premium_m=154.0,
        trustee="Spirax-Sarco Pension Trustees Limited",
        actuary="Mercer Limited", admin="Aptia", investment_mgr="Insight Investment",
    ),
    Customer(
        slug="rsm_uk", display="RSM UK Pension Fund", sponsor="RSM UK Holdings Limited",
        sector="Professional Services (Accountancy)",
        scheme_type="Defined Benefit - Final Salary (Closed)",
        status="Closed to new entrants and future accrual",
        active=0, deferred=420, pensioners=480,
        total_liability_m=108.2, assets_m=101.8, funding_level=94.1,
        valuation_date="31/03/2024",
        accrual_rate="1/60th of Final Pensionable Salary per year of service",
        nra="65", spouse_pension="50% of member's pension",
        indexation="CPI capped at 5% p.a.",
        revaluation="Statutory (CPI capped at 2.5% p.a.)",
        employer_contribution="N/A (closed to accrual)",
        deficit_contribution="GBP 2.8m per annum until 31/03/2028",
        ppf_levy="GBP 74,800", bpa_premium_m=112.0,
        trustee="RSM UK Pension Trustee Limited",
        actuary="Lane Clark & Peacock", admin="XPS Pensions", investment_mgr="Schroders",
    ),
]


# ===================================================================
# Deterministic year variations
# ===================================================================

def year_snapshot(c: Customer, year: int) -> dict[str, Any]:
    """Return a deterministic per-year version of the customer's headline
    numbers so each year's documents differ slightly."""

    rng = random.Random(hash(f"{c.slug}-{year}"))
    offset = year - 2025  # 0 for 2025, -1 for 2024, etc.

    funding = max(75.0, min(104.0, c.funding_level + offset * 1.2 + rng.uniform(-0.4, 0.4)))
    assets = c.assets_m * (1 + offset * 0.018 + rng.uniform(-0.008, 0.008))
    liability = c.total_liability_m * (1 + offset * 0.012 + rng.uniform(-0.006, 0.006))
    deficit = liability - assets

    deferred = max(0, c.deferred + offset * 20 + rng.randint(-6, 6))
    pensioners = max(0, c.pensioners - offset * 18 + rng.randint(-5, 5))
    active = max(0, c.active + offset * 4 + rng.randint(-2, 2)) if c.active else 0

    bpa = c.bpa_premium_m * (1 + offset * 0.015 + rng.uniform(-0.005, 0.005))

    return {
        "year": year,
        "funding_level": round(funding, 1),
        "assets_m": round(assets, 1),
        "liability_m": round(liability, 1),
        "deficit_m": round(deficit, 1),
        "active": active,
        "deferred": deferred,
        "pensioners": pensioners,
        "total_members": active + deferred + pensioners,
        "bpa_premium_m": round(bpa, 1),
        "cpi": round(2.0 + rng.uniform(-0.6, 3.5), 2),
        "rpi": round(2.8 + rng.uniform(-0.5, 3.8), 2),
        "discount_rate": round(1.4 + offset * -0.2 + rng.uniform(-0.3, 0.3), 2),
        "ldi_pct": round(52 + offset * -1.5 + rng.uniform(-2, 2), 1),
        "credit_pct": round(22 + rng.uniform(-2, 2), 1),
        "equity_pct": round(10 + rng.uniform(-2, 2), 1),
        "property_pct": round(8 + rng.uniform(-1.5, 1.5), 1),
        "cash_pct": round(8 + rng.uniform(-1.5, 1.5), 1),
    }


# ===================================================================
# Branded 10-page PDF class
# ===================================================================

def _make_pdf_class():
    fpdf_mod = _ensure("fpdf", "fpdf2")
    FPDF = fpdf_mod.FPDF

    class BrandedPDF(FPDF):  # type: ignore
        customer_name: str = ""
        doc_title: str = ""
        doc_subtitle: str = ""

        def header(self):
            if os.path.exists(LOGO_PATH):
                try:
                    self.image(LOGO_PATH, x=10, y=8, h=12)
                except Exception:
                    pass
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(*RL_PURPLE)
            self.set_xy(35, 10)
            self.cell(0, 5, self.customer_name, new_x="LMARGIN", new_y="NEXT")
            self.set_x(35)
            self.set_font("Helvetica", "", 8)
            self.set_text_color(*RL_GRAY)
            self.cell(0, 4, self.doc_title, new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(*RL_PURPLE)
            self.set_line_width(0.4)
            self.line(10, 24, 200, 24)
            self.set_y(30)
            self.set_text_color(*RL_DARK)

        def footer(self):
            self.set_y(-18)
            self.set_draw_color(200, 200, 205)
            self.set_line_width(0.2)
            self.line(10, self.get_y(), 200, self.get_y())
            self.set_y(-15)
            self.set_font("Helvetica", "I", 7)
            self.set_text_color(*RL_GRAY)
            self.multi_cell(150, 3.2, FOOTER_LEGAL[:180] + "...")
            self.set_xy(170, -15)
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(*RL_PURPLE)
            self.cell(0, 4, f"Page {self.page_no()} of {{nb}}", align="R")

    return BrandedPDF


def _new_pdf(customer_name: str, title: str, subtitle: str = ""):
    BrandedPDF = _make_pdf_class()
    pdf = BrandedPDF()
    pdf.customer_name = customer_name
    pdf.doc_title = title
    pdf.doc_subtitle = subtitle
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=22)
    return pdf


def _section_header(pdf, text: str):
    pdf.ln(2)
    pdf.set_fill_color(*RL_PURPLE_LIGHT)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*RL_PURPLE)
    pdf.cell(0, 8, f"  {text}", new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*RL_DARK)


def _kv_rows(pdf, rows: list[tuple[str, str]]):
    for k, v in rows:
        start_y = pdf.get_y()
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*RL_GRAY)
        pdf.set_xy(10, start_y)
        pdf.cell(80, 6, f"  {k}", border=0)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*RL_DARK)
        pdf.set_xy(90, start_y)
        pdf.multi_cell(110, 6, str(v))
    pdf.ln(2)


def _paragraph(pdf, text: str):
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(*RL_DARK)
    pdf.multi_cell(0, 5.2, text)
    pdf.ln(2)


def _table(pdf, headers: list[str], rows: list[list[str]], col_widths: list[float] | None = None):
    if col_widths is None:
        page_width = 190
        col_widths = [page_width / len(headers)] * len(headers)

    pdf.set_fill_color(*RL_PURPLE)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    for w, h in zip(col_widths, headers):
        pdf.cell(w, 7, h, border=0, fill=True)
    pdf.ln(7)

    pdf.set_text_color(*RL_DARK)
    pdf.set_font("Helvetica", "", 9)
    for i, row in enumerate(rows):
        if i % 2 == 0:
            pdf.set_fill_color(250, 247, 253)
        else:
            pdf.set_fill_color(255, 255, 255)
        for w, cell in zip(col_widths, row):
            pdf.cell(w, 6, str(cell), border=0, fill=True)
        pdf.ln(6)
    pdf.ln(2)


# ===================================================================
# 10-page Triennial Valuation PDF
# ===================================================================

def create_triennial_valuation(c: Customer, year: int, out_dir: str):
    y = year_snapshot(c, year)
    pdf = _new_pdf(c.display, f"Triennial Actuarial Valuation {year}", "")

    # Page 1 - Cover
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(*RL_PURPLE)
    pdf.cell(0, 14, "Triennial Actuarial", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 14, f"Valuation {year}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(*RL_TEAL)
    pdf.cell(0, 8, c.display, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(40)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*RL_DARK)
    _kv_rows(pdf, [
        ("Sponsor Employer", c.sponsor),
        ("Scheme Actuary", c.actuary),
        ("Valuation Date", f"31/03/{year}"),
        ("Document Status", "Final - approved by Trustee"),
        ("Document Classification", "Confidential - BPA Review"),
        ("Prepared For", "Royal London BPA Origination"),
    ])

    # Page 2 - Contents + Executive Summary
    pdf.add_page()
    _section_header(pdf, "1. Executive Summary")
    _paragraph(pdf,
        f"This report sets out the actuarial valuation of the {c.display} as at "
        f"31 March {year}. The scheme is a {c.scheme_type.lower()} established by "
        f"{c.sponsor} and is currently {c.status.lower()}. The valuation has been "
        f"prepared in accordance with the Pensions Act 2004, the Scheme Funding "
        f"Regulations 2005, and the Trustee's Statement of Funding Principles.")
    _paragraph(pdf,
        f"As at the valuation date, the scheme held assets of GBP {y['assets_m']:.1f}m "
        f"against technical provisions of GBP {y['liability_m']:.1f}m, giving a funding "
        f"level of {y['funding_level']:.1f}% and a deficit of GBP {y['deficit_m']:.1f}m. "
        f"The Trustee has considered the scheme's long-term objective of securing "
        f"member benefits through a buy-out transaction, and this document forms part "
        f"of the wider BPA origination pack being prepared for Royal London.")
    _kv_rows(pdf, [
        ("Technical Provisions", f"GBP {y['liability_m']:.1f}m"),
        ("Scheme Assets", f"GBP {y['assets_m']:.1f}m"),
        ("Funding Deficit", f"GBP {y['deficit_m']:.1f}m"),
        ("Funding Level", f"{y['funding_level']:.1f}%"),
        ("Total Membership", f"{y['total_members']:,}"),
        ("Indicative BPA Premium", f"GBP {y['bpa_premium_m']:.1f}m"),
    ])

    # Page 3 - Scheme information
    pdf.add_page()
    _section_header(pdf, "2. Scheme Information")
    _kv_rows(pdf, [
        ("Scheme Name", c.display),
        ("Sponsor Employer", c.sponsor),
        ("Sector", c.sector),
        ("Scheme Type", c.scheme_type),
        ("Scheme Status", c.status),
        ("Trustee", c.trustee),
        ("Scheme Actuary", c.actuary),
        ("Administrator", c.admin),
        ("Investment Manager", c.investment_mgr),
        ("Normal Retirement Age", c.nra),
        ("Accrual Rate", c.accrual_rate),
        ("Revaluation in Deferment", c.revaluation),
        ("Indexation in Payment", c.indexation),
        ("Spouse's Pension", c.spouse_pension),
    ])

    # Page 4 - Membership
    pdf.add_page()
    _section_header(pdf, "3. Membership Summary")
    total = max(y["total_members"], 1)
    _table(pdf, ["Category", "Count", "% of Total", "Average Age"], [
        ["Active Members", f"{y['active']:,}", f"{y['active']/total*100:.1f}%", "52.4"],
        ["Deferred Members", f"{y['deferred']:,}", f"{y['deferred']/total*100:.1f}%", "56.8"],
        ["Pensioner Members", f"{y['pensioners']:,}", f"{y['pensioners']/total*100:.1f}%", "73.2"],
        ["Total Membership", f"{total:,}", "100.0%", "63.7"],
    ], col_widths=[60, 45, 45, 40])
    _paragraph(pdf,
        "Member data has been supplied by the Administrator as at the valuation "
        "date and has been subject to the standard data quality checks described in "
        "Appendix A. No material data issues were identified that would affect the "
        "valuation results. Average ages are weighted by liability.")
    _section_header(pdf, "3.1 Pensioner Age Profile")
    _table(pdf, ["Age Band", "Members", "Average Pension (GBP p.a.)"], [
        ["60-64", f"{int(y['pensioners']*0.08):,}", "14,820"],
        ["65-69", f"{int(y['pensioners']*0.18):,}", "13,210"],
        ["70-74", f"{int(y['pensioners']*0.24):,}", "12,640"],
        ["75-79", f"{int(y['pensioners']*0.22):,}", "11,480"],
        ["80-84", f"{int(y['pensioners']*0.16):,}", "10,120"],
        ["85+", f"{int(y['pensioners']*0.12):,}", "8,940"],
    ], col_widths=[60, 60, 70])

    # Page 5 - Funding position
    pdf.add_page()
    _section_header(pdf, "4. Funding Position")
    _paragraph(pdf,
        "The funding position has been calculated on the Technical Provisions basis "
        "agreed between the Trustee and Sponsor. A separate buy-out basis has been "
        "prepared for the BPA transaction pack.")
    _table(pdf, ["Measure", f"As at 31/03/{year-3}", f"As at 31/03/{year}"], [
        ["Technical Provisions (GBP m)", f"{y['liability_m']*0.94:.1f}", f"{y['liability_m']:.1f}"],
        ["Scheme Assets (GBP m)", f"{y['assets_m']*0.91:.1f}", f"{y['assets_m']:.1f}"],
        ["Surplus / (Deficit) (GBP m)", f"{y['assets_m']*0.91 - y['liability_m']*0.94:.1f}", f"{-y['deficit_m']:.1f}"],
        ["Funding Level", f"{(y['assets_m']*0.91)/(y['liability_m']*0.94)*100:.1f}%", f"{y['funding_level']:.1f}%"],
    ], col_widths=[80, 55, 55])
    _section_header(pdf, "4.1 Buy-out Basis")
    _kv_rows(pdf, [
        ("Estimated buy-out liability", f"GBP {y['liability_m']*1.15:.1f}m"),
        ("Estimated buy-out funding level", f"{(y['assets_m']/(y['liability_m']*1.15))*100:.1f}%"),
        ("Additional premium vs TP", f"GBP {y['liability_m']*0.15:.1f}m"),
    ])

    # Page 6 - Actuarial assumptions
    pdf.add_page()
    _section_header(pdf, "5. Actuarial Assumptions")
    _paragraph(pdf,
        "The assumptions below have been set by the Trustee having regard to advice "
        "from the Scheme Actuary and following consultation with the Sponsor.")
    _kv_rows(pdf, [
        ("Discount Rate (pre-retirement)", f"Gilts + {y['discount_rate']:.2f}% p.a."),
        ("Discount Rate (post-retirement)", f"Gilts + {max(0.2, y['discount_rate']-0.6):.2f}% p.a."),
        ("RPI Inflation", f"{y['rpi']:.2f}% p.a."),
        ("CPI Inflation", f"{y['cpi']:.2f}% p.a."),
        ("Salary Increase (active)", "CPI + 1.0% p.a."),
        ("Pension Increase (LPI 5%)", f"{min(5.0, y['cpi']):.2f}% p.a."),
        ("Pension Increase (LPI 2.5%)", f"{min(2.5, y['cpi']):.2f}% p.a."),
        ("Base Mortality Table", "S3PMA / S3PFA"),
        ("Mortality Improvements", f"CMI_{year-1} with 1.25% long-term rate"),
        ("Commutation Take-up", "80% of maximum tax-free cash"),
        ("Proportion Married", "85% (males), 70% (females)"),
    ])

    # Page 7 - Asset allocation
    pdf.add_page()
    _section_header(pdf, "6. Asset Allocation")
    _paragraph(pdf, f"The scheme's strategic asset allocation at 31/03/{year} is set out below.")
    allocations = [
        ("Liability-Driven Investment (LDI)", y["ldi_pct"]),
        ("Buy-and-Maintain Credit", y["credit_pct"]),
        ("Global Equities", y["equity_pct"]),
        ("Property / Real Assets", y["property_pct"]),
        ("Cash & Collateral", y["cash_pct"]),
    ]
    total_pct = sum(v for _, v in allocations)
    _table(pdf, ["Asset Class", "Allocation (%)", "Value (GBP m)"],
        [[a, f"{v:.1f}%", f"{y['assets_m']*v/total_pct:.1f}"] for a, v in allocations] +
        [["Total", f"{total_pct:.1f}%", f"{y['assets_m']:.1f}"]],
        col_widths=[90, 50, 50])
    _paragraph(pdf,
        f"The Trustee continues to run a high-hedging LDI strategy, with an estimated "
        f"hedge ratio of 95% on interest rates and 93% on inflation, measured against "
        f"the technical provisions liabilities. The Investment Manager, "
        f"{c.investment_mgr}, reports quarterly against the Statement of Investment "
        f"Principles.")

    # Page 8 - Cashflow projection
    pdf.add_page()
    _section_header(pdf, "7. Projected Benefit Cashflows")
    _paragraph(pdf,
        "The table below shows the expected benefit outgo over the next 10 years "
        "based on the valuation assumptions. Figures are nominal GBP m.")
    base_cf = y["liability_m"] / 26.0
    rng = random.Random(hash(f"{c.slug}-{year}-cashflow"))
    _table(pdf, ["Year", "Pensions in Payment", "Lump Sums", "Transfers Out", "Total"],
        [[str(year + i),
          f"{base_cf*(1 + i*0.018) + rng.uniform(-0.3, 0.3):.1f}",
          f"{base_cf*0.11 + rng.uniform(-0.1, 0.1):.1f}",
          f"{base_cf*0.05 + rng.uniform(-0.05, 0.05):.1f}",
          f"{base_cf*(1.16 + i*0.018) + rng.uniform(-0.2, 0.2):.1f}"]
         for i in range(1, 11)],
        col_widths=[25, 55, 35, 40, 35])

    # Page 9 - Covenant + recovery plan
    pdf.add_page()
    _section_header(pdf, "8. Employer Covenant")
    _paragraph(pdf,
        f"The Trustee has obtained an independent assessment of the {c.sponsor} "
        f"covenant from a specialist adviser. The covenant is assessed as tending to "
        f"Strong on the Pensions Regulator's four-point scale, reflecting the "
        f"sponsor's balance sheet strength, predictable cashflows and continued "
        f"engagement with the scheme. The Trustee reviews the covenant at least "
        f"annually.")
    _section_header(pdf, "8.1 Recovery Plan")
    _kv_rows(pdf, [
        ("Deficit Reduction Contribution", c.deficit_contribution),
        ("Recovery Plan End Date", c.deficit_contribution.split("until ")[-1] if "until" in c.deficit_contribution else "N/A"),
        ("PPF Annual Levy", c.ppf_levy),
        ("Expense Reserve", "GBP 185,000 p.a."),
    ])
    _paragraph(pdf,
        "The Trustee and Sponsor have agreed to accelerate the recovery plan in the "
        "event of a successful BPA transaction, with residual deficit contributions "
        "continuing at 50% of the current rate until wind-up is complete.")

    # Page 10 - BPA profile + appendix
    pdf.add_page()
    _section_header(pdf, "9. BPA Transaction Profile")
    _kv_rows(pdf, [
        ("Transaction Type", "Pensioner Buy-in (Phase 1)"),
        ("Target Completion", f"Q3/Q4 {year+1}"),
        ("Indicative Premium (pensioner tranche)", f"GBP {y['bpa_premium_m']*0.55:.1f}m"),
        ("Indicative Premium (deferred tranche)", f"GBP {y['bpa_premium_m']*0.45:.1f}m"),
        ("Total Indicative Premium", f"GBP {y['bpa_premium_m']:.1f}m"),
        ("Expected Insurer Price Lock", "30 days from exclusivity"),
    ])
    _section_header(pdf, "Appendix A - Data Quality")
    _paragraph(pdf,
        "Member data was supplied by the Administrator in standard CSV format. "
        "Standard checks have been performed on dates of birth, pension amounts, "
        "commencement dates and spouse data. No material issues were identified "
        "that would affect the valuation results.")
    _section_header(pdf, "Appendix B - GMP Equalisation")
    _paragraph(pdf,
        "The scheme has completed GMP equalisation in respect of service between "
        "17 May 1990 and 5 April 1997 following the High Court's Lloyds Banking "
        "Group judgment. Residual conversion work is ongoing in advance of buy-out.")

    path = os.path.join(out_dir, f"{c.slug}_triennial_valuation_{year}.pdf")
    pdf.output(path)
    return path


# ===================================================================
# Other 10-page PDFs
# ===================================================================

def create_sip(c: Customer, year: int, out_dir: str):
    y = year_snapshot(c, year)
    pdf = _new_pdf(c.display, f"Statement of Investment Principles {year}")

    # Cover
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(*RL_PURPLE)
    pdf.cell(0, 14, "Statement of", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 14, "Investment Principles", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(*RL_TEAL)
    pdf.cell(0, 8, f"{c.display} ({year})", new_x="LMARGIN", new_y="NEXT")

    # Pages 2-10: standard SIP structure
    sections = [
        ("1. Introduction", [
            "This Statement of Investment Principles has been prepared by the Trustee of the "
            f"{c.display} in accordance with Section 35 of the Pensions Act 1995 (as amended). "
            "It sets out the principles governing the investment of the scheme's assets.",
            "The Trustee has consulted the Sponsor and received written professional advice "
            "from the scheme's Investment Adviser before adopting this Statement.",
        ]),
        ("2. Investment Objectives", [
            "The Trustee's primary objective is to ensure that the scheme can meet its "
            "obligations to members as they fall due. The Trustee also has regard to the "
            "long-term objective of securing member benefits through a buy-out transaction.",
            f"At the valuation date the scheme held assets of GBP {y['assets_m']:.1f}m against "
            f"technical provisions of GBP {y['liability_m']:.1f}m.",
        ]),
        ("3. Strategic Asset Allocation", []),
        ("4. Risk Management", [
            "The Trustee monitors a range of investment risks including interest rate risk, "
            "inflation risk, credit risk, equity market risk, liquidity risk and counterparty "
            "risk. The scheme maintains high hedging ratios on interest rates (95%) and "
            "inflation (93%) measured against the technical provisions liabilities.",
        ]),
        ("5. Liquidity and Collateral", [
            "The Trustee maintains a collateral waterfall sufficient to withstand a 1-in-20 "
            "year adverse yield shock. Liquid assets are sized to cover at least 18 months of "
            "benefit outgo plus an additional collateral buffer for the LDI programme.",
        ]),
        ("6. Responsible Investment", [
            "The Trustee believes that environmental, social and governance (ESG) factors are "
            "financially material to long-term investment performance. The Investment Manager "
            "is required to incorporate ESG considerations into all investment decisions and "
            "report annually on stewardship activity.",
            "The scheme aligns its climate reporting with the Task Force on Climate-related "
            "Financial Disclosures (TCFD) recommendations.",
        ]),
        ("7. Manager Selection and Monitoring", [
            f"The scheme's assets are managed by {c.investment_mgr} under an Investment "
            "Management Agreement. The Trustee reviews manager performance quarterly against "
            "agreed benchmarks and risk limits.",
        ]),
        ("8. Reviews and Amendments", [
            "This Statement is reviewed at least every three years, and without delay following "
            "any significant change in investment policy. The Trustee will consult the Sponsor "
            "before making any material amendment.",
        ]),
        ("9. Buy-out Readiness", [
            "The Trustee has considered the investment strategy implications of a potential "
            "BPA transaction. The portfolio has been progressively de-risked to align with "
            "insurer pricing bases, with a current gilt-equivalent allocation of approximately "
            f"{y['ldi_pct'] + y['credit_pct']:.0f}% of total assets.",
        ]),
    ]

    for title, paras in sections:
        pdf.add_page()
        _section_header(pdf, title)
        for p in paras:
            _paragraph(pdf, p)
        if title.startswith("3."):
            _table(pdf, ["Asset Class", "Strategic %", "Tolerance"],
                [["LDI", f"{y['ldi_pct']:.1f}%", "+/- 5%"],
                 ["Buy-and-Maintain Credit", f"{y['credit_pct']:.1f}%", "+/- 3%"],
                 ["Global Equities", f"{y['equity_pct']:.1f}%", "+/- 2%"],
                 ["Property / Real Assets", f"{y['property_pct']:.1f}%", "+/- 2%"],
                 ["Cash & Collateral", f"{y['cash_pct']:.1f}%", "+/- 2%"]],
                col_widths=[90, 50, 50])

    path = os.path.join(out_dir, f"{c.slug}_sip_{year}.pdf")
    pdf.output(path)
    return path


def create_covenant_review(c: Customer, year: int, out_dir: str):
    y = year_snapshot(c, year)
    pdf = _new_pdf(c.display, f"Employer Covenant Review {year}")
    rng = random.Random(hash(f"{c.slug}-{year}-covenant"))

    pdf.add_page()
    pdf.ln(30)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(*RL_PURPLE)
    pdf.cell(0, 12, f"Employer Covenant Review {year}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(*RL_TEAL)
    pdf.cell(0, 8, c.display, new_x="LMARGIN", new_y="NEXT")

    sections_content = [
        ("1. Executive Summary",
         f"This report presents the Trustee's annual review of the employer covenant "
         f"provided by {c.sponsor}. The covenant is assessed as tending to Strong on "
         f"the Pensions Regulator's four-point scale (CG1-CG4). No material "
         f"deterioration has been identified during the review period."),
        ("2. Sponsor Financial Review",
         f"{c.sponsor} reported turnover of GBP {rng.uniform(220, 1800):.0f}m in its "
         f"latest audited accounts, with profit before tax of GBP "
         f"{rng.uniform(18, 140):.0f}m and net assets of GBP "
         f"{rng.uniform(80, 620):.0f}m. Cashflow from operating activities remains "
         f"robust and the sponsor holds a net cash position on the balance sheet."),
        ("3. Affordability Assessment",
         f"Contributions to the scheme represent less than {rng.uniform(4, 9):.1f}% of "
         f"free cashflow, leaving substantial capacity to support the scheme. The "
         f"sponsor has reaffirmed its commitment to the current recovery plan and to "
         f"supporting a BPA transaction subject to pricing."),
        ("4. Reliability of Covenant",
         "The sponsor's core business is well diversified across end-markets and "
         "geographies. Contracted revenues provide good visibility over the next "
         "three years. The sponsor has a conservative dividend policy and no material "
         "acquisition programme in progress."),
        ("5. Insolvency Risk",
         "A Probability of Default analysis using the Trustee's standard model "
         f"suggests a one-year default probability of c. {rng.uniform(0.18, 0.45):.2f}% "
         f"and a five-year default probability of c. {rng.uniform(1.2, 2.8):.1f}%. "
         "These are consistent with the assessed covenant strength."),
        ("6. Contingent Support",
         "The scheme benefits from a parent company guarantee capped at GBP 15m "
         "(pre-2016 commitment) and a legal charge over specified assets. The "
         "Trustee reviews these arrangements annually."),
        ("7. Covenant Monitoring",
         "The Trustee meets the sponsor's finance team on a quarterly basis. Key "
         "monitoring metrics include net debt / EBITDA, interest cover, liquidity "
         "headroom, and pension contribution as a percentage of free cashflow."),
        ("8. BPA Transaction Impact",
         f"A BPA transaction of GBP {y['bpa_premium_m']:.1f}m would materially reduce "
         f"the sponsor's exposure to the scheme. The Trustee has modelled a range of "
         f"scenarios and concludes that the transaction would be covenant-accretive."),
        ("9. Conclusion",
         "The Trustee concludes that the employer covenant remains tending to Strong. "
         "No covenant-driven changes to the funding strategy are recommended. The "
         "Trustee supports progression of the BPA origination workstream."),
    ]

    for title, body in sections_content:
        pdf.add_page()
        _section_header(pdf, title)
        _paragraph(pdf, body)
        _paragraph(pdf, body)  # pad each page with reinforcing narrative
        _kv_rows(pdf, [
            ("Review Date", f"31/12/{year}"),
            ("Next Scheduled Review", f"31/12/{year+1}"),
            ("Independent Adviser", "Penfida Partners"),
        ])

    path = os.path.join(out_dir, f"{c.slug}_covenant_review_{year}.pdf")
    pdf.output(path)
    return path


def create_bpa_data_pack(c: Customer, year: int, out_dir: str):
    y = year_snapshot(c, year)
    pdf = _new_pdf(c.display, f"BPA Origination Data Pack {year}")

    pdf.add_page()
    pdf.ln(30)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(*RL_PURPLE)
    pdf.cell(0, 12, "BPA Data Pack", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(*RL_TEAL)
    pdf.cell(0, 8, f"{c.display} - {year}", new_x="LMARGIN", new_y="NEXT")

    pages = [
        ("1. Scheme Summary", [
            ("Scheme Name", c.display),
            ("Sponsor", c.sponsor),
            ("Status", c.status),
            ("Scheme Type", c.scheme_type),
            ("Trustee", c.trustee),
        ]),
        ("2. Benefit Structure", [
            ("Accrual Rate", c.accrual_rate),
            ("Normal Retirement Age", c.nra),
            ("Spouse's Pension", c.spouse_pension),
            ("Indexation in Payment", c.indexation),
            ("Revaluation in Deferment", c.revaluation),
        ]),
        ("3. Membership", [
            ("Active Members", f"{y['active']:,}"),
            ("Deferred Members", f"{y['deferred']:,}"),
            ("Pensioner Members", f"{y['pensioners']:,}"),
            ("Total Membership", f"{y['total_members']:,}"),
        ]),
        ("4. Funding Position", [
            ("Technical Provisions", f"GBP {y['liability_m']:.1f}m"),
            ("Scheme Assets", f"GBP {y['assets_m']:.1f}m"),
            ("Funding Level (TP)", f"{y['funding_level']:.1f}%"),
            ("Buy-out Deficit (est.)", f"GBP {y['liability_m']*1.15 - y['assets_m']:.1f}m"),
        ]),
        ("5. Investment Strategy", [
            ("LDI Allocation", f"{y['ldi_pct']:.1f}%"),
            ("Credit Allocation", f"{y['credit_pct']:.1f}%"),
            ("Interest Rate Hedge Ratio", "95%"),
            ("Inflation Hedge Ratio", "93%"),
        ]),
        ("6. Transaction Profile", [
            ("Indicative Premium", f"GBP {y['bpa_premium_m']:.1f}m"),
            ("Proposed Structure", "Pensioner Buy-in (Phase 1)"),
            ("Target Completion", f"Q3/Q4 {year+1}"),
            ("Exclusive Insurer", "Royal London"),
        ]),
        ("7. Data Quality", [
            ("Data Completeness", "99.4%"),
            ("Marital Status Coverage", "96.8%"),
            ("Address Coverage", "98.1%"),
            ("Last Data Refresh", f"30/06/{year}"),
        ]),
        ("8. Timeline", [
            ("Data Cut Date", f"31/03/{year}"),
            ("Adviser Due Diligence", f"Q2 {year+1}"),
            ("Exclusivity", f"Q3 {year+1}"),
            ("Completion", f"Q4 {year+1}"),
        ]),
        ("9. Contacts & Appendices", [
            ("Scheme Actuary", c.actuary),
            ("Administrator", c.admin),
            ("Investment Manager", c.investment_mgr),
            ("Legal Adviser", "Sackers LLP"),
        ]),
    ]
    for title, rows in pages:
        pdf.add_page()
        _section_header(pdf, title)
        _kv_rows(pdf, rows)
        _paragraph(pdf,
            "This section forms part of the BPA origination data pack and is "
            "provided on a confidential basis to Royal London for the purpose of "
            "pricing a bulk purchase annuity transaction. Information has been "
            "extracted from the scheme's administration records and latest actuarial "
            "valuation and is provided without warranty.")

    path = os.path.join(out_dir, f"{c.slug}_bpa_data_pack_{year}.pdf")
    pdf.output(path)
    return path


def create_risk_register(c: Customer, year: int, out_dir: str):
    pdf = _new_pdf(c.display, f"Scheme Risk Register {year}")
    rng = random.Random(hash(f"{c.slug}-{year}-risk"))

    pdf.add_page()
    pdf.ln(30)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(*RL_PURPLE)
    pdf.cell(0, 12, f"Risk Register {year}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(*RL_TEAL)
    pdf.cell(0, 8, c.display, new_x="LMARGIN", new_y="NEXT")

    categories = [
        ("Funding Risks", [
            "Adverse investment returns relative to liabilities",
            "Interest rate and inflation movements",
            "Longevity improvements beyond assumptions",
            "Member option take-up variations",
        ]),
        ("Covenant Risks", [
            "Sponsor financial deterioration",
            "Corporate restructuring or disposal",
            "Dividend policy changes",
        ]),
        ("Investment Risks", [
            "Counterparty failure in LDI arrangements",
            "Liquidity shortfall under stress",
            "Manager underperformance",
        ]),
        ("Operational Risks", [
            "Administrator errors or delays",
            "Data quality degradation",
            "Cyber and information security",
        ]),
        ("Legal & Regulatory Risks", [
            "GMP conversion complexity",
            "Changes to tax regime for pensions",
            "New Funding Code compliance",
        ]),
        ("Member Outcomes Risks", [
            "Member communications breakdowns",
            "Complaints and IDRP escalations",
            "Safeguarding vulnerable customers",
        ]),
        ("Transaction Risks", [
            "BPA pricing volatility",
            "Insurer capacity and selection",
            "Transfer documentation errors",
        ]),
        ("Climate Risks", [
            "Transition risk on strategic allocation",
            "Physical risk on property holdings",
            "TCFD reporting completeness",
        ]),
        ("Governance Risks", [
            "Trustee board composition and skills",
            "Adviser rotation and independence",
            "Conflict of interest management",
        ]),
    ]

    for title, risks in categories:
        pdf.add_page()
        _section_header(pdf, title)
        _table(pdf,
            ["Risk", "Likelihood", "Impact", "Score", "Owner"],
            [[r,
              rng.choice(["Low", "Low-Med", "Medium", "Med-High"]),
              rng.choice(["Medium", "Med-High", "High"]),
              str(rng.randint(4, 15)),
              rng.choice(["Trustee", "Investment Ctte", "Sponsor", "Administrator"])]
             for r in risks],
            col_widths=[85, 28, 28, 20, 29])
        _paragraph(pdf,
            "Mitigating actions are documented in the Risk Appetite Statement. The "
            "Trustee reviews risks at each quarterly meeting and performs a full "
            "risk-register refresh annually.")

    path = os.path.join(out_dir, f"{c.slug}_risk_register_{year}.pdf")
    pdf.output(path)
    return path


# ===================================================================
# Short 2-3 page PDFs
# ===================================================================

def create_trustee_minutes(c: Customer, year: int, quarter: int, out_dir: str):
    pdf = _new_pdf(c.display, f"Trustee Meeting Minutes Q{quarter} {year}")
    rng = random.Random(hash(f"{c.slug}-{year}-q{quarter}-minutes"))

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*RL_PURPLE)
    pdf.cell(0, 10, f"Trustee Meeting Minutes - Q{quarter} {year}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*RL_GRAY)
    pdf.cell(0, 6, c.display, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    _section_header(pdf, "Attendees")
    _paragraph(pdf, "Trustee Directors: J. Harper (Chair), S. Khan, P. Morris, R. Ali.")
    _paragraph(pdf, f"In Attendance: Scheme Actuary ({c.actuary}), Investment Adviser, Administrator ({c.admin}), Sponsor representative.")

    _section_header(pdf, "Agenda")
    for i, item in enumerate([
        "Minutes of previous meeting",
        "Funding update",
        "Investment performance review",
        "Administration report",
        "BPA origination progress",
        "Risk register update",
        "Any other business",
    ], 1):
        _paragraph(pdf, f"{i}. {item}")

    pdf.add_page()
    _section_header(pdf, "Discussion - Funding Update")
    _paragraph(pdf,
        f"The Scheme Actuary presented the quarterly funding update. On the Technical "
        f"Provisions basis, the funding level moved by "
        f"{rng.uniform(-1.8, 1.8):+.1f}ppts during the quarter to end the period at "
        f"approximately {year_snapshot(c, year)['funding_level']:.1f}%.")
    _section_header(pdf, "Discussion - Investment Performance")
    _paragraph(pdf,
        f"The Investment Manager reported quarterly performance of "
        f"{rng.uniform(-2.1, 2.8):+.2f}% against the scheme-specific benchmark, broadly "
        f"in line with expectations. LDI hedge ratios remained within tolerance.")

    pdf.add_page()
    _section_header(pdf, "Decisions & Actions")
    _kv_rows(pdf, [
        ("BPA data pack refresh", f"Complete by end Q{(quarter % 4) + 1}"),
        ("Updated SIP - Trustee sign-off", "Approved"),
        ("Member communications review", "Scheduled for next meeting"),
        ("Covenant review commissioning", "Proceed"),
    ])

    path = os.path.join(out_dir, f"{c.slug}_trustee_minutes_{year}_q{quarter}.pdf")
    pdf.output(path)
    return path


def create_investment_report(c: Customer, year: int, quarter: int, out_dir: str):
    y = year_snapshot(c, year)
    pdf = _new_pdf(c.display, f"Investment Report Q{quarter} {year}")
    rng = random.Random(hash(f"{c.slug}-{year}-q{quarter}-inv"))

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*RL_PURPLE)
    pdf.cell(0, 10, f"Quarterly Investment Report", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*RL_TEAL)
    pdf.cell(0, 7, f"Q{quarter} {year} - {c.display}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    _section_header(pdf, "Portfolio Summary")
    _table(pdf, ["Asset Class", "Allocation", "Performance (Q)", "12m Performance"],
        [["LDI", f"{y['ldi_pct']:.1f}%", f"{rng.uniform(-3, 3):+.2f}%", f"{rng.uniform(-6, 6):+.2f}%"],
         ["Credit", f"{y['credit_pct']:.1f}%", f"{rng.uniform(-2, 2.5):+.2f}%", f"{rng.uniform(-3, 6):+.2f}%"],
         ["Equities", f"{y['equity_pct']:.1f}%", f"{rng.uniform(-4, 5):+.2f}%", f"{rng.uniform(-8, 14):+.2f}%"],
         ["Property", f"{y['property_pct']:.1f}%", f"{rng.uniform(-2, 2):+.2f}%", f"{rng.uniform(-5, 5):+.2f}%"],
         ["Cash", f"{y['cash_pct']:.1f}%", f"{rng.uniform(0.5, 1.5):+.2f}%", f"{rng.uniform(2, 5):+.2f}%"]],
        col_widths=[60, 40, 45, 45])

    pdf.add_page()
    _section_header(pdf, "Market Commentary")
    _paragraph(pdf,
        f"During Q{quarter} {year}, gilt yields moved by approximately "
        f"{rng.uniform(-45, 45):+.0f}bp across the curve. The scheme's LDI "
        f"programme continued to deliver its hedging objective with a tracking "
        f"error within the agreed tolerance band.")
    _paragraph(pdf,
        "The Investment Manager has maintained a neutral positioning against the "
        "benchmark, with a modest overweight to investment-grade credit reflecting "
        "attractive spread levels.")

    _section_header(pdf, "Compliance with SIP")
    _paragraph(pdf, "All allocations remained within the tolerance bands specified in the Statement of Investment Principles throughout the quarter.")

    path = os.path.join(out_dir, f"{c.slug}_investment_report_{year}_q{quarter}.pdf")
    pdf.output(path)
    return path


def create_funding_update(c: Customer, year: int, month: int, out_dir: str):
    y = year_snapshot(c, year)
    pdf = _new_pdf(c.display, f"Monthly Funding Update {year}-{month:02d}")
    rng = random.Random(hash(f"{c.slug}-{year}-{month}-funding"))

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*RL_PURPLE)
    pdf.cell(0, 10, f"Monthly Funding Update", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*RL_TEAL)
    pdf.cell(0, 7, f"{year}-{month:02d} - {c.display}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    funding = y["funding_level"] + rng.uniform(-1.2, 1.2)
    _section_header(pdf, "Headline Numbers")
    _kv_rows(pdf, [
        ("Report Date", f"{year}-{month:02d}-28"),
        ("Technical Provisions", f"GBP {y['liability_m'] + rng.uniform(-1, 1):.1f}m"),
        ("Scheme Assets", f"GBP {y['assets_m'] + rng.uniform(-1, 1):.1f}m"),
        ("Funding Level", f"{funding:.1f}%"),
        ("Buy-out Funding Level (est.)", f"{funding*0.87:.1f}%"),
    ])

    pdf.add_page()
    _section_header(pdf, "Monthly Movements")
    _paragraph(pdf,
        f"The scheme's funding level moved by approximately "
        f"{rng.uniform(-1.3, 1.3):+.1f}ppts during the month. The primary drivers "
        f"were changes in gilt yields and credit spreads, partially offset by "
        f"contributions received under the recovery plan.")

    path = os.path.join(out_dir, f"{c.slug}_funding_update_{year}_{month:02d}.pdf")
    pdf.output(path)
    return path


def create_ppf_submission(c: Customer, year: int, out_dir: str):
    pdf = _new_pdf(c.display, f"PPF Levy Submission {year}")
    pdf.add_page()
    _section_header(pdf, f"Pension Protection Fund - Levy Submission {year}/{year+1}")
    _kv_rows(pdf, [
        ("Scheme Name", c.display),
        ("Scheme Reference", f"PSR-{hash(c.slug) & 0xFFFFFF:07d}"),
        ("Risk-Based Levy", c.ppf_levy),
        ("Scheme-Based Levy", "GBP 32,400"),
        ("Total Levy Payable", c.ppf_levy.replace("GBP ", "GBP ").replace(",", "") and c.ppf_levy),
        ("Submission Date", f"31/03/{year}"),
        ("Confirmation Reference", f"PPF-{year}-{hash(c.slug) & 0xFFFFF:05d}"),
    ])
    pdf.add_page()
    _section_header(pdf, "D&B Score and Insolvency Probability")
    _paragraph(pdf,
        "The Trustee has reviewed the sponsor's Dun & Bradstreet failure score and "
        "confirms the score used in the PPF levy calculation. No contingent assets "
        "are currently certified for levy reduction purposes.")
    path = os.path.join(out_dir, f"{c.slug}_ppf_submission_{year}.pdf")
    pdf.output(path)
    return path


def create_smpi(c: Customer, year: int, out_dir: str):
    pdf = _new_pdf(c.display, f"Summary Funding Statement {year}")
    pdf.add_page()
    y = year_snapshot(c, year)
    _section_header(pdf, "Summary Funding Statement to Members")
    _paragraph(pdf,
        f"Dear Member,\n\nThis statement provides a summary of the funding position of "
        f"the {c.display} as at 31 March {year}. Your Trustee is required to send you "
        f"this information each year.")
    _kv_rows(pdf, [
        ("Scheme Assets", f"GBP {y['assets_m']:.1f}m"),
        ("Amount Needed to Provide Benefits", f"GBP {y['liability_m']:.1f}m"),
        ("Surplus / (Shortfall)", f"GBP {-y['deficit_m']:.1f}m"),
        ("Funding Level", f"{y['funding_level']:.1f}%"),
    ])
    pdf.add_page()
    _section_header(pdf, "Recovery Plan")
    _paragraph(pdf,
        f"Your Sponsor, {c.sponsor}, is making additional contributions to the scheme "
        f"to cover the shortfall over time. These contributions are in addition to the "
        f"normal cost of benefits being built up.")
    _section_header(pdf, "Your Questions Answered")
    _paragraph(pdf,
        "If you have any questions about your benefits or this statement please "
        f"contact the Scheme Administrator, {c.admin}. Your personal benefit details "
        "are available via the member portal.")
    path = os.path.join(out_dir, f"{c.slug}_summary_funding_{year}.pdf")
    pdf.output(path)
    return path


def create_gmp_equalisation(c: Customer, year: int, out_dir: str):
    pdf = _new_pdf(c.display, f"GMP Equalisation Report {year}")
    pdf.add_page()
    _section_header(pdf, "GMP Equalisation - Implementation Report")
    _paragraph(pdf,
        "Following the Lloyds Banking Group judgments (2018, 2020), trustees are "
        "required to equalise member benefits for the effect of unequal Guaranteed "
        "Minimum Pensions accrued between 17 May 1990 and 5 April 1997.")
    pdf.add_page()
    _section_header(pdf, "Methodology Adopted")
    _paragraph(pdf,
        "The Trustee, having taken legal and actuarial advice, has adopted Method C2 "
        "(year-by-year comparison with accumulated arrears) followed by GMP "
        "conversion at buy-out.")
    pdf.add_page()
    _section_header(pdf, "Financial Impact")
    _kv_rows(pdf, [
        ("Total Benefit Uplift", "0.8% of TPs"),
        ("Members in Scope", "Approximately 72%"),
        ("Arrears + Interest", "GBP 480,000"),
        ("Implementation Date", f"Q3 {year}"),
    ])
    path = os.path.join(out_dir, f"{c.slug}_gmp_equalisation_{year}.pdf")
    pdf.output(path)
    return path


# ===================================================================
# DOCX documents
# ===================================================================

def _add_docx_logo(doc):
    _ensure("docx", "python-docx")
    from docx.shared import Inches
    if os.path.exists(LOGO_PATH):
        try:
            section = doc.sections[0]
            header = section.header
            p = header.paragraphs[0]
            run = p.add_run()
            run.add_picture(LOGO_PATH, width=Inches(1.1))
        except Exception:
            pass


def create_benefit_spec_docx(c: Customer, year: int, out_dir: str):
    _ensure("docx", "python-docx")
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
    _add_docx_logo(doc)

    title = doc.add_paragraph()
    run = title.add_run(c.display)
    run.font.size = Pt(20); run.font.bold = True; run.font.color.rgb = RGBColor(*RL_PURPLE)
    sub = doc.add_paragraph()
    r2 = sub.add_run(f"Benefit Specification {year}/{year+1}")
    r2.font.size = Pt(12); r2.font.italic = True; r2.font.color.rgb = RGBColor(*RL_TEAL)
    doc.add_paragraph()

    def add_section(heading: str, rows: list[tuple[str, str]]):
        h = doc.add_paragraph()
        hr = h.add_run(heading)
        hr.font.size = Pt(13); hr.font.bold = True; hr.font.color.rgb = RGBColor(*RL_PURPLE)
        table = doc.add_table(rows=len(rows), cols=2)
        table.autofit = False
        table.columns[0].width = Inches(2.4); table.columns[1].width = Inches(4.0)
        for i, (k, v) in enumerate(rows):
            table.rows[i].cells[0].text = k
            table.rows[i].cells[1].text = v
            for cell in table.rows[i].cells:
                for p in cell.paragraphs:
                    for r in p.runs:
                        r.font.size = Pt(10)
        doc.add_paragraph()

    add_section("Scheme Information", [
        ("Scheme Name", c.display), ("Sponsor Employer", c.sponsor),
        ("Scheme Type", c.scheme_type), ("Scheme Status", c.status),
        ("Trustee", c.trustee), ("Administrator", c.admin),
        ("Document Year", str(year)),
    ])
    add_section("Benefit Structure", [
        ("Accrual Rate", c.accrual_rate), ("Normal Retirement Age", c.nra),
        ("Spouse's Pension", c.spouse_pension),
        ("Pension Indexation in Payment", c.indexation),
        ("Revaluation in Deferment", c.revaluation),
        ("Early Retirement Factor", "Actuarial reduction of 4% per year before NRA"),
        ("Commutation Factor", "GBP 16 of pension commuted for GBP 256 tax-free cash"),
    ])
    add_section("Death Benefits", [
        ("Lump Sum on Death in Service", "4x Final Pensionable Salary"),
        ("Death Benefit - Deferred", "Return of contributions with interest"),
        ("Death Benefit - Pensioners", "Continuation of spouse's pension; 5-year guarantee"),
    ])
    add_section("Governance", [
        ("Scheme Actuary", c.actuary), ("Investment Manager", c.investment_mgr),
        ("PPF Levy", c.ppf_levy),
    ])

    fp = doc.add_paragraph()
    fr = fp.add_run(FOOTER_LEGAL)
    fr.font.size = Pt(7); fr.font.italic = True; fr.font.color.rgb = RGBColor(*RL_GRAY)

    path = os.path.join(out_dir, f"{c.slug}_benefit_spec_{year}.docx")
    doc.save(path)
    return path


def create_member_options_pack(c: Customer, year: int, out_dir: str):
    _ensure("docx", "python-docx")
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches

    doc = Document()
    _add_docx_logo(doc)
    title = doc.add_paragraph()
    r = title.add_run(f"{c.display} - Member Options Pack {year}")
    r.font.size = Pt(18); r.font.bold = True; r.font.color.rgb = RGBColor(*RL_PURPLE)

    for heading, body in [
        ("Your Options at Retirement",
         "You have a number of options for how to take your scheme benefits. "
         "This pack explains the main choices: taking your pension with a tax-free "
         "cash sum, transferring out to another arrangement, and drawing down "
         "flexibly under an alternative vehicle."),
        ("Transferring Your Benefits",
         "The Trustee recommends that all members considering a transfer out take "
         "independent financial advice. Transfers of safeguarded benefits above the "
         "statutory threshold require regulated advice."),
        ("Taking Tax-Free Cash",
         "You may commute part of your pension for a tax-free cash lump sum, up to "
         "the lower of 25% of the capitalised value of your benefits and the lifetime "
         "allowance limit applicable to you."),
        ("Getting Help",
         f"The Scheme Administrator, {c.admin}, can answer questions about your "
         "benefits. MoneyHelper offers free impartial guidance."),
    ]:
        h = doc.add_paragraph()
        hr = h.add_run(heading)
        hr.font.size = Pt(13); hr.font.bold = True; hr.font.color.rgb = RGBColor(*RL_PURPLE)
        p = doc.add_paragraph(body)
        for run in p.runs:
            run.font.size = Pt(10)

    path = os.path.join(out_dir, f"{c.slug}_member_options_{year}.docx")
    doc.save(path)
    return path


# ===================================================================
# XLSX documents
# ===================================================================

def _add_xlsx_logo(ws):
    try:
        _ensure("openpyxl")
        from openpyxl.drawing.image import Image as XLImage
        if os.path.exists(LOGO_PATH):
            img = XLImage(LOGO_PATH)
            img.width = 110
            img.height = 28
            ws.add_image(img, "A1")
            ws.row_dimensions[1].height = 28
    except Exception:
        pass


def create_member_data_xlsx(c: Customer, year: int, out_dir: str):
    _ensure("openpyxl")
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    wb = Workbook()
    purple_fill = PatternFill(start_color=RL_PURPLE_HEX, end_color=RL_PURPLE_HEX, fill_type="solid")
    teal_fill = PatternFill(start_color=RL_TEAL_HEX, end_color=RL_TEAL_HEX, fill_type="solid")
    white_bold = Font(color="FFFFFF", bold=True, size=11)
    header_bold = Font(bold=True, size=10, color=RL_DARK_HEX)
    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    y = year_snapshot(c, year)
    total = max(y["total_members"], 1)

    ws1 = wb.active
    ws1.title = "Member Summary"
    _add_xlsx_logo(ws1)
    ws1.column_dimensions["A"].width = 34
    ws1.column_dimensions["B"].width = 28
    ws1.column_dimensions["C"].width = 20

    ws1["A2"] = f"{c.display} - Member Data Extract ({year})"
    ws1.merge_cells("A2:C2")
    ws1["A2"].font = Font(bold=True, size=13, color="FFFFFF")
    ws1["A2"].fill = purple_fill
    ws1["A2"].alignment = Alignment(horizontal="center")

    ws1.append([])
    ws1.append(["Scheme Name", c.display, ""])
    ws1.append(["Sponsor", c.sponsor, ""])
    ws1.append(["Valuation Snapshot Date", f"31/03/{year}", ""])
    ws1.append([])
    ws1.append(["Member Category", "Count", "% of Total"])
    ws1.append(["Active Members", y["active"], f"{y['active']/total*100:.1f}%"])
    ws1.append(["Deferred Members", y["deferred"], f"{y['deferred']/total*100:.1f}%"])
    ws1.append(["Pensioner Members", y["pensioners"], f"{y['pensioners']/total*100:.1f}%"])
    ws1.append(["Total Membership", total, "100.0%"])

    header_row = 8
    for col in ("A", "B", "C"):
        ws1[f"{col}{header_row}"].font = white_bold
        ws1[f"{col}{header_row}"].fill = teal_fill
        ws1[f"{col}{header_row}"].alignment = Alignment(horizontal="center")

    for row in range(header_row + 1, header_row + 5):
        for col in ("A", "B", "C"):
            ws1[f"{col}{row}"].border = border
    for col in ("A", "B", "C"):
        ws1[f"{col}{header_row + 4}"].font = header_bold

    # Sheet 2 - Liability breakdown
    ws2 = wb.create_sheet("Liability Breakdown")
    _add_xlsx_logo(ws2)
    ws2.column_dimensions["A"].width = 32
    ws2.column_dimensions["B"].width = 22
    ws2.column_dimensions["C"].width = 22

    ws2["A2"] = f"{c.display} - Liability Breakdown {year} (GBP m)"
    ws2.merge_cells("A2:C2")
    ws2["A2"].font = Font(bold=True, size=13, color="FFFFFF")
    ws2["A2"].fill = purple_fill
    ws2["A2"].alignment = Alignment(horizontal="center")
    ws2.append([])
    ws2.append(["Member Category", "Liability (GBP m)", "% of TP"])

    active_liab = y["liability_m"] * (y["active"] / total) * 1.1 if y["active"] else 0
    deferred_liab = y["liability_m"] * (y["deferred"] / total) * 0.9
    pensioner_liab = y["liability_m"] - active_liab - deferred_liab

    ws2.append(["Active Members", round(active_liab, 1), f"{active_liab/y['liability_m']*100:.1f}%"])
    ws2.append(["Deferred Members", round(deferred_liab, 1), f"{deferred_liab/y['liability_m']*100:.1f}%"])
    ws2.append(["Pensioner Members", round(pensioner_liab, 1), f"{pensioner_liab/y['liability_m']*100:.1f}%"])
    ws2.append(["Total Technical Provisions", round(y["liability_m"], 1), "100.0%"])

    path = os.path.join(out_dir, f"{c.slug}_member_data_{year}.xlsx")
    wb.save(path)
    return path


def create_asset_allocation_xlsx(c: Customer, year: int, quarter: int, out_dir: str):
    _ensure("openpyxl")
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment

    wb = Workbook()
    ws = wb.active
    ws.title = f"Q{quarter} {year}"
    _add_xlsx_logo(ws)

    purple_fill = PatternFill(start_color=RL_PURPLE_HEX, end_color=RL_PURPLE_HEX, fill_type="solid")
    teal_fill = PatternFill(start_color=RL_TEAL_HEX, end_color=RL_TEAL_HEX, fill_type="solid")
    white_bold = Font(color="FFFFFF", bold=True, size=11)

    y = year_snapshot(c, year)
    ws.column_dimensions["A"].width = 36
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 22

    ws["A2"] = f"{c.display} - Asset Allocation Q{quarter} {year}"
    ws.merge_cells("A2:C2")
    ws["A2"].font = Font(bold=True, size=12, color="FFFFFF")
    ws["A2"].fill = purple_fill
    ws["A2"].alignment = Alignment(horizontal="center")

    ws.append([])
    ws.append(["Asset Class", "Weight", "Value (GBP m)"])
    for col in ("A", "B", "C"):
        ws[f"{col}4"].font = white_bold
        ws[f"{col}4"].fill = teal_fill
        ws[f"{col}4"].alignment = Alignment(horizontal="center")

    for name, pct in [
        ("Liability-Driven Investment", y["ldi_pct"]),
        ("Buy-and-Maintain Credit", y["credit_pct"]),
        ("Global Equities", y["equity_pct"]),
        ("Property", y["property_pct"]),
        ("Cash & Collateral", y["cash_pct"]),
    ]:
        ws.append([name, f"{pct:.1f}%", round(y["assets_m"] * pct / 100, 1)])

    path = os.path.join(out_dir, f"{c.slug}_asset_allocation_{year}_q{quarter}.xlsx")
    wb.save(path)
    return path


# ===================================================================
# CSV documents
# ===================================================================

def create_contribution_schedule_csv(c: Customer, year: int, out_dir: str):
    path = os.path.join(out_dir, f"{c.slug}_contribution_schedule_{year}.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([f"{c.display} - Schedule of Contributions {year}/{year+1}"])
        w.writerow([f"Sponsor: {c.sponsor}"])
        w.writerow([f"Effective From: 06/04/{year}"])
        w.writerow([])
        w.writerow(["Category", "Rate / Amount", "Frequency", "Notes"])
        if c.active > 0:
            w.writerow(["Employer Ordinary Contribution", c.employer_contribution, "Monthly", "On pensionable payroll"])
            w.writerow(["Employee Contribution", "6.0% of Pensionable Pay", "Monthly", "Salary sacrifice available"])
        else:
            w.writerow(["Employer Ordinary Contribution", c.employer_contribution, "N/A", "Closed to accrual"])
            w.writerow(["Employee Contribution", "N/A", "N/A", "Closed to accrual"])
        w.writerow(["Deficit Reduction Contribution", c.deficit_contribution, "Annual", "Per recovery plan"])
        w.writerow(["PPF Annual Levy", c.ppf_levy, "Annual", "Risk-based pension protection"])
        w.writerow(["Expenses Allowance", "GBP 185,000", "Annual", "Trustee and administration"])
    return path


def create_cashflow_projection_csv(c: Customer, year: int, out_dir: str):
    y = year_snapshot(c, year)
    path = os.path.join(out_dir, f"{c.slug}_cashflow_projection_{year}.csv")
    rng = random.Random(hash(f"{c.slug}-{year}-cashflow-csv"))
    base = y["liability_m"] / 26.0
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([f"{c.display} - 20-year Cashflow Projection (GBP m)"])
        w.writerow([f"Projection Date: 31/03/{year}"])
        w.writerow([])
        w.writerow(["Year", "Pensions in Payment", "Lump Sums", "Transfers Out", "Total Outgo"])
        for i in range(1, 21):
            pp = base * (1 + i * 0.016) + rng.uniform(-0.2, 0.2)
            ls = base * 0.11 + rng.uniform(-0.05, 0.05)
            to = base * 0.05 + rng.uniform(-0.03, 0.03)
            w.writerow([year + i, f"{pp:.2f}", f"{ls:.2f}", f"{to:.2f}", f"{pp + ls + to:.2f}"])
    return path


# ===================================================================
# Customer pipeline
# ===================================================================

def generate_customer(c: Customer, out_dir: str) -> list[str]:
    files: list[str] = []

    # Core 10-page PDFs
    for year in YEARS:
        if year in (2021, 2024):  # triennial every 3 years
            files.append(create_triennial_valuation(c, year, out_dir))
        files.append(create_sip(c, year, out_dir))
        files.append(create_covenant_review(c, year, out_dir))
        files.append(create_bpa_data_pack(c, year, out_dir))
        files.append(create_risk_register(c, year, out_dir))

    # Quarterly / monthly short PDFs
    for year in YEARS:
        for q in (1, 2, 3, 4):
            files.append(create_trustee_minutes(c, year, q, out_dir))
            files.append(create_investment_report(c, year, q, out_dir))
        for m in (3, 6, 9, 12):
            files.append(create_funding_update(c, year, m, out_dir))
        files.append(create_ppf_submission(c, year, out_dir))
        files.append(create_smpi(c, year, out_dir))
        if year in (2022, 2023):
            files.append(create_gmp_equalisation(c, year, out_dir))

    # DOCX
    for year in YEARS:
        files.append(create_benefit_spec_docx(c, year, out_dir))
        files.append(create_member_options_pack(c, year, out_dir))

    # XLSX
    for year in YEARS:
        files.append(create_member_data_xlsx(c, year, out_dir))
        for q in (1, 2, 3, 4):
            files.append(create_asset_allocation_xlsx(c, year, q, out_dir))

    # CSV
    for year in YEARS:
        files.append(create_contribution_schedule_csv(c, year, out_dir))
        files.append(create_cashflow_projection_csv(c, year, out_dir))

    return files


# ===================================================================
# Upload to Unity Catalog Volume
# ===================================================================

def upload_to_volume(local_dir: str, customer_slug: str, profile: str | None = None) -> int:
    """Upload every file in local_dir to /Volumes/main/bpa_rubjit/documents/<slug>/.

    Uses the Databricks SDK if it can auth; falls back to shelling out to the
    `databricks` CLI with an explicit profile (required when multiple profiles
    share a host)."""

    target_root = f"{VOLUME_PATH}/{customer_slug}"

    # Try the SDK first (works cleanly in the Databricks App runtime).
    try:
        from databricks.sdk import WorkspaceClient
        client = WorkspaceClient(profile=profile) if profile else WorkspaceClient()
        try:
            client.files.create_directory(target_root)
        except Exception:
            pass
        try:
            for entry in client.files.list_directory_contents(target_root):
                try:
                    client.files.delete(entry.path)
                except Exception:
                    pass
        except Exception:
            pass
        uploaded = 0
        for name in sorted(os.listdir(local_dir)):
            local = os.path.join(local_dir, name)
            if not os.path.isfile(local):
                continue
            remote = f"{target_root}/{name}"
            with open(local, "rb") as fh:
                client.files.upload(remote, fh, overwrite=True)
            uploaded += 1
        return uploaded
    except Exception as e:
        print(f"    SDK upload failed ({e}); falling back to databricks CLI")

    # CLI fallback
    import subprocess
    env = os.environ.copy()
    env["DATABRICKS_CLI_DO_NOT_EXECUTE_NEWER_VERSION"] = "1"
    cli = "/opt/homebrew/bin/databricks"
    cli_args = [cli]
    if profile:
        cli_args += ["--profile", profile]

    # Clean remote directory
    subprocess.run(cli_args + ["fs", "rm", "-r", f"dbfs:{target_root}"],
                   env=env, capture_output=True)
    subprocess.run(cli_args + ["fs", "mkdir", f"dbfs:{target_root}"],
                   env=env, capture_output=True)

    uploaded = 0
    for name in sorted(os.listdir(local_dir)):
        local = os.path.join(local_dir, name)
        if not os.path.isfile(local):
            continue
        remote = f"dbfs:{target_root}/{name}"
        result = subprocess.run(
            cli_args + ["fs", "cp", "--overwrite", local, remote],
            env=env, capture_output=True, text=True,
        )
        if result.returncode == 0:
            uploaded += 1
        else:
            print(f"    failed {name}: {result.stderr.strip()[:120]}")
    return uploaded


# ===================================================================
# Main
# ===================================================================

def main():
    upload = "--upload" in sys.argv
    single_customer = None
    profile: str | None = None
    for arg in sys.argv[1:]:
        if arg.startswith("--only="):
            single_customer = arg.split("=", 1)[1]
        elif arg.startswith("--profile="):
            profile = arg.split("=", 1)[1]

    print("Generating branded mock corpus...\n")
    total_files = 0
    for c in CUSTOMERS:
        if single_customer and c.slug != single_customer:
            continue
        print(f"\n[{c.slug}] {c.display}")
        out_dir = os.path.join(OUTPUT_DIR, c.slug)
        os.makedirs(out_dir, exist_ok=True)
        # Wipe previous outputs for this customer so re-runs are clean
        for f in os.listdir(out_dir):
            try:
                os.remove(os.path.join(out_dir, f))
            except Exception:
                pass
        files = generate_customer(c, out_dir)
        print(f"  generated {len(files)} files")
        total_files += len(files)

        if upload:
            print("  uploading to UC Volume...")
            n = upload_to_volume(out_dir, c.slug, profile=profile)
            print(f"  uploaded {n} files to {VOLUME_PATH}/{c.slug}")

    print(f"\nDone. {total_files} files generated across {len(CUSTOMERS) if not single_customer else 1} customer(s).")


if __name__ == "__main__":
    main()
