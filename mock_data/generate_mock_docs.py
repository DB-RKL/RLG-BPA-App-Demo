"""
Generate realistic Royal London benefit specification documents in mixed formats.
Run: python3 mock_data/generate_mock_docs.py

Produces PDFs, Excel (.xlsx), CSV, and Word (.docx) files.
Requires: pip install fpdf2 openpyxl python-docx
"""

import csv
import os
import sys

OUTPUT_DIR = os.path.dirname(__file__)

# ---------------------------------------------------------------------------
# Lazy-install helpers
# ---------------------------------------------------------------------------

def _ensure(pkg, pip_name=None):
    try:
        return __import__(pkg)
    except ImportError:
        os.system(f"{sys.executable} -m pip install {pip_name or pkg}")
        return __import__(pkg)


# ---------------------------------------------------------------------------
# Royal London brand constants
# ---------------------------------------------------------------------------

RL_PURPLE = (111, 54, 164)
RL_PURPLE_LIGHT = (245, 238, 251)
RL_TEAL = (0, 122, 122)
RL_DARK = (26, 26, 46)
RL_GRAY = (100, 100, 110)

RL_PURPLE_HEX = "6F36A4"
RL_TEAL_HEX = "007A7A"
RL_DARK_HEX = "1A1A2E"

FOOTER_TEXT = (
    "The Royal London Mutual Insurance Society Limited is authorised by the "
    "Prudential Regulation Authority and regulated by the Financial Conduct "
    "Authority and the Prudential Regulation Authority. Registration number "
    "117672. Registered in England and Wales, company number 99064. "
    "Registered office: 80 Fenchurch Street, London, EC3M 4BY."
)


# ===================================================================
# 1. PDFs – Group Life & Workplace Pension (kept from original set)
# ===================================================================

PDF_PLANS = [
    {
        "filename": "rl_group_life_insurance_2025.pdf",
        "title": "Royal London Group Life Insurance",
        "subtitle": "Scheme Specification & Benefit Schedule 2025/26",
        "ref": "RL-GLI-2025-8834",
        "sections": {
            "Scheme Details": {
                "Scheme Name": "Royal London Group Life Assurance",
                "Scheme Type": "Group Life (Death in Service)",
                "Underwriter": "Royal London (The Royal London Mutual Insurance Society Limited)",
                "Policy Number": "RL-GLI-2025-8834",
                "Effective Date": "01/04/2025",
                "Renewal Date": "31/03/2026",
                "Eligible Employees": "All UK permanent employees with 3+ months service",
                "FCA Registration": "117672",
            },
            "Death in Service Benefit": {
                "Benefit Multiple - Standard": "4x Annual Basic Salary",
                "Benefit Multiple - Senior Management": "6x Annual Basic Salary",
                "Maximum Benefit Cap": "£2,000,000",
                "Salary Definition": "Basic annual salary excluding bonuses, overtime and benefits-in-kind",
                "Dependants Pension": "Included - 50% of member's pension to surviving spouse/partner",
                "Lump Sum Children Benefit": "£5,000 per dependent child (under age 23 in full-time education)",
            },
            "Premium Rates": {
                "Employer Rate - Under 30": "0.18% of payroll",
                "Employer Rate - Age 30-39": "0.26% of payroll",
                "Employer Rate - Age 40-49": "0.52% of payroll",
                "Employer Rate - Age 50-59": "1.15% of payroll",
                "Employer Rate - Age 60+": "2.40% of payroll",
                "Premium Basis": "Monthly in arrears, employer funded 100%",
            },
            "Free Cover Limit": {
                "Free Cover Limit (FCL)": "£750,000",
                "Medical Evidence Required Above FCL": "Yes - Royal London health questionnaire",
                "Underwriting Method": "Medical History Disregarded (below FCL)",
            },
            "Exclusions & Conditions": {
                "Exclusion Period": "None (immediate cover from scheme entry)",
                "Active Employment Clause": "Member must be actively at work on scheme entry date",
                "Territorial Limit": "Worldwide (subject to UK tax residency)",
                "Excluded Causes": "Suicide within first 12 months; active participation in war or terrorism",
            },
        },
    },
    {
        "filename": "rl_workplace_pension_2025.pdf",
        "title": "Royal London Workplace Pension Scheme",
        "subtitle": "Pension Schedule & Contribution Rates 2025/26",
        "ref": "RL-WPS-2025-1192",
        "sections": {
            "Scheme Details": {
                "Scheme Name": "Royal London Workplace Pension",
                "Scheme Type": "Group Personal Pension (GPP) - Defined Contribution",
                "Provider": "Royal London",
                "Policy Number": "RL-WPS-2025-1192",
                "Effective Date": "01/04/2025",
                "Auto-Enrolment Staging Date": "01/06/2017",
                "Eligible Jobholders": "UK workers aged 22 to SPA earning £10,000+ per annum",
                "HMRC Reference": "PSR 12345678RL",
            },
            "Contribution Rates": {
                "Employer Contribution - Standard": "5% of qualifying earnings",
                "Employer Contribution - Senior Management": "10% of qualifying earnings",
                "Employee Contribution - Standard": "5% of qualifying earnings (minimum 3% AE)",
                "Salary Sacrifice Available": "Yes - SmartPay arrangement reducing NIC liability",
                "Qualifying Earnings Band": "£6,240 to £50,270 (2025/26 tax year)",
                "Employer Match": "Up to additional 3% matched pound-for-pound",
                "Annual Allowance": "£60,000 (2025/26 tax year)",
                "Lifetime Allowance": "Abolished from 06/04/2024",
            },
            "Investment Options": {
                "Default Fund": "Royal London Governed Portfolio 4 (Moderate)",
                "Default Fund AMC": "0.40% per annum",
                "Lifestyle Strategy": "Royal London Retirement Income Profile - de-risks from age 55",
                "Self-Select Options": "45 funds available including ESG and Shariah-compliant",
                "ProfitShare Eligible": "Yes - eligible for Royal London mutual bonus distribution",
            },
            "Retirement Options": {
                "Normal Pension Age": "State Pension Age (currently 66, rising to 67 from 2026)",
                "Flexible Access": "Full flexi-access drawdown from age 55 (rising to 57 from 2028)",
                "Tax-Free Cash": "25% of fund value (up to £268,275 under transitional rules)",
                "Annuity Purchase": "Available via Royal London or Open Market Option",
                "Small Pot Commutation": "Available if fund below £10,000",
            },
            "Charges & Governance": {
                "Annual Management Charge (AMC)": "0.40% on default fund; 0.50%-0.75% on self-select",
                "Independent Governance Committee": "Royal London IGC - annual Value for Money assessment",
                "Statement Frequency": "Annual benefit statement plus online portal access",
                "Chair's Statement": "Published annually per Pensions Act 2004 requirements",
            },
        },
    },
]


def _create_pdf(plan: dict):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    pdf.set_fill_color(*RL_PURPLE)
    pdf.rect(0, 0, 210, 45, "F")

    pdf.set_y(10)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, plan["title"], new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(220, 200, 240)
    pdf.cell(0, 7, plan["subtitle"], new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, f"Reference: {plan['ref']}", new_x="LMARGIN", new_y="NEXT")

    pdf.set_text_color(*RL_DARK)
    pdf.ln(10)

    for section_title, fields in plan["sections"].items():
        pdf.set_fill_color(*RL_PURPLE_LIGHT)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(*RL_PURPLE)
        pdf.cell(0, 8, f"  {section_title}", new_x="LMARGIN", new_y="NEXT", fill=True)
        pdf.set_text_color(*RL_DARK)
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 9)
        for key, value in fields.items():
            pdf.set_text_color(*RL_GRAY)
            pdf.cell(85, 6, f"  {key}", border=0)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*RL_DARK)
            pdf.cell(0, 6, value, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 9)
        pdf.ln(3)

    pdf.ln(8)
    pdf.set_draw_color(*RL_PURPLE)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*RL_GRAY)
    pdf.multi_cell(0, 4, FOOTER_TEXT)

    path = os.path.join(OUTPUT_DIR, plan["filename"])
    pdf.output(path)
    print(f"  [PDF]  {path}")


# ===================================================================
# 2. Excel – Income Protection & Contribution Rate Schedule
# ===================================================================

def _create_income_protection_xlsx():
    """Group Income Protection scheme as a multi-sheet workbook."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    wb = Workbook()
    purple_fill = PatternFill(start_color=RL_PURPLE_HEX, end_color=RL_PURPLE_HEX, fill_type="solid")
    teal_fill = PatternFill(start_color=RL_TEAL_HEX, end_color=RL_TEAL_HEX, fill_type="solid")
    white_font = Font(color="FFFFFF", bold=True, size=11)
    header_font = Font(bold=True, size=10, color=RL_DARK_HEX)
    thin_border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin"),
    )

    # --- Sheet 1: Scheme Overview ---
    ws1 = wb.active
    ws1.title = "Scheme Overview"
    ws1.column_dimensions["A"].width = 35
    ws1.column_dimensions["B"].width = 55

    ws1.append(["Royal London Group Income Protection – RL-GIP-2025-4421", ""])
    ws1.merge_cells("A1:B1")
    ws1["A1"].font = Font(bold=True, size=14, color="FFFFFF")
    ws1["A1"].fill = purple_fill

    details = [
        ("Scheme Name", "Royal London Group Income Protection"),
        ("Scheme Type", "Group Income Protection (GIP)"),
        ("Underwriter", "Royal London"),
        ("Policy Number", "RL-GIP-2025-4421"),
        ("Effective Date", "01/04/2025"),
        ("Renewal Date", "31/03/2026"),
        ("Eligible Employees", "All UK permanent employees with 6+ months service"),
        ("FCA Registration", "117672"),
        ("", ""),
        ("Benefit Percentage", "75% of pre-disability earnings (inclusive of state benefits)"),
        ("Income Definition", "Basic annual salary plus average of last 3 years contractual bonus"),
        ("Maximum Monthly Benefit", "£15,000 per month"),
        ("Deferred Period – Standard", "26 weeks"),
        ("Deferred Period – Senior Mgmt", "13 weeks"),
        ("Benefit Cease Age", "State Pension Age (SPA)"),
        ("Proportionate Benefit", "Yes – for phased return to work"),
        ("", ""),
        ("Early Intervention Service", "Included – vocational rehabilitation from week 4 of absence"),
        ("Employee Assistance Programme", "24/7 helpline and up to 6 counselling sessions"),
        ("Occupational Health Referral", "Available from day 1 of claim"),
    ]
    for r_idx, (k, v) in enumerate(details, start=2):
        ws1.cell(row=r_idx, column=1, value=k).font = header_font if k else Font()
        ws1.cell(row=r_idx, column=2, value=v)

    # --- Sheet 2: Premium Rate Table ---
    ws2 = wb.create_sheet("Premium Rates")
    ws2.column_dimensions["A"].width = 20
    ws2.column_dimensions["B"].width = 18
    ws2.column_dimensions["C"].width = 18
    ws2.column_dimensions["D"].width = 22

    headers = ["Age Band", "Rate (% Payroll)", "Monthly Cost (£50k salary)", "Annual Cost (£50k salary)"]
    for c_idx, h in enumerate(headers, start=1):
        cell = ws2.cell(row=1, column=c_idx, value=h)
        cell.font = white_font
        cell.fill = teal_fill
        cell.alignment = Alignment(horizontal="center")
        cell.border = thin_border

    rates = [
        ("Under 30", "0.45%", "£18.75", "£225.00"),
        ("30-39", "0.72%", "£30.00", "£360.00"),
        ("40-49", "1.35%", "£56.25", "£675.00"),
        ("50-59", "2.80%", "£116.67", "£1,400.00"),
        ("60+", "4.10%", "£170.83", "£2,050.00"),
    ]
    for r_idx, row_data in enumerate(rates, start=2):
        for c_idx, val in enumerate(row_data, start=1):
            cell = ws2.cell(row=r_idx, column=c_idx, value=val)
            cell.alignment = Alignment(horizontal="center")
            cell.border = thin_border

    ws2.cell(row=len(rates) + 3, column=1, value="Premium Basis:").font = Font(bold=True)
    ws2.cell(row=len(rates) + 3, column=2, value="Monthly in arrears, employer funded 100%")

    path = os.path.join(OUTPUT_DIR, "rl_group_income_protection_2025.xlsx")
    wb.save(path)
    print(f"  [XLSX] {path}")


def _create_contribution_schedule_xlsx():
    """Employer/employee contribution rate schedule across tiers."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    wb = Workbook()
    purple_fill = PatternFill(start_color=RL_PURPLE_HEX, end_color=RL_PURPLE_HEX, fill_type="solid")
    white_font = Font(color="FFFFFF", bold=True, size=11)
    thin_border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin"),
    )

    ws = wb.active
    ws.title = "Contribution Rates"
    ws.column_dimensions["A"].width = 30
    for col in ["B", "C", "D", "E", "F"]:
        ws.column_dimensions[col].width = 18

    ws.append(["Royal London Workplace Pension – Contribution Rate Schedule 2025/26", "", "", "", "", ""])
    ws.merge_cells("A1:F1")
    ws["A1"].font = Font(bold=True, size=13, color="FFFFFF")
    ws["A1"].fill = purple_fill

    ws.append([])

    headers = ["Employee Grade", "Employer %", "Employee %", "Employer Match", "Salary Sacrifice", "Total %"]
    for c_idx, h in enumerate(headers, start=1):
        cell = ws.cell(row=3, column=c_idx, value=h)
        cell.font = white_font
        cell.fill = PatternFill(start_color=RL_TEAL_HEX, end_color=RL_TEAL_HEX, fill_type="solid")
        cell.alignment = Alignment(horizontal="center")
        cell.border = thin_border

    rows = [
        ("Entry Level (Grade 1-3)", "3%", "3%", "N/A", "Available", "6%"),
        ("Standard (Grade 4-6)", "5%", "5%", "Up to 2%", "Available", "12%"),
        ("Senior (Grade 7-8)", "8%", "5%", "Up to 3%", "Available", "16%"),
        ("Management (Grade 9-10)", "10%", "5%", "Up to 3%", "Available", "18%"),
        ("Executive / Director", "15%", "5%", "Up to 5%", "Available", "25%"),
    ]
    for r_idx, row_data in enumerate(rows, start=4):
        for c_idx, val in enumerate(row_data, start=1):
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            cell.alignment = Alignment(horizontal="center")
            cell.border = thin_border

    notes_row = len(rows) + 5
    ws.cell(row=notes_row, column=1, value="Notes:").font = Font(bold=True)
    ws.cell(row=notes_row + 1, column=1, value="Qualifying Earnings Band: £6,240 to £50,270 (2025/26 tax year)")
    ws.cell(row=notes_row + 2, column=1, value="Annual Allowance: £60,000 (2025/26 tax year)")
    ws.cell(row=notes_row + 3, column=1, value="Salary Sacrifice (SmartPay) reduces NIC liability for employer and employee")

    path = os.path.join(OUTPUT_DIR, "rl_contribution_rate_schedule_2025.xlsx")
    wb.save(path)
    print(f"  [XLSX] {path}")


# ===================================================================
# 3. CSV – Employee Eligibility Census
# ===================================================================

def _create_eligibility_csv():
    """Employee eligibility census in CSV format."""
    path = os.path.join(OUTPUT_DIR, "rl_employee_eligibility_census_2025.csv")

    headers = [
        "Employee ID", "Full Name", "Date of Birth", "Gender",
        "Start Date", "Grade", "Department", "Annual Salary (GBP)",
        "Group Life", "Income Protection", "Pension", "Critical Illness",
        "Dental & Optical", "Salary Sacrifice",
    ]

    employees = [
        ("EMP-10021", "Sarah Thompson", "15/03/1985", "F", "01/09/2018", "7", "Finance", "72000", "Yes", "Yes", "Yes – 8%", "Yes", "Yes", "Yes"),
        ("EMP-10034", "James O'Brien", "22/11/1990", "M", "15/01/2020", "5", "IT", "55000", "Yes", "Yes", "Yes – 5%", "Yes", "No", "Yes"),
        ("EMP-10042", "Priya Patel", "08/07/1978", "F", "01/04/2015", "9", "Legal", "95000", "Yes", "Yes", "Yes – 10%", "Yes", "Yes", "Yes"),
        ("EMP-10055", "David Williams", "30/01/1992", "M", "10/06/2021", "4", "Operations", "42000", "Yes", "Yes", "Yes – 5%", "No", "Yes", "No"),
        ("EMP-10061", "Fatima Khan", "14/09/1988", "F", "01/03/2019", "6", "Marketing", "58000", "Yes", "Yes", "Yes – 5%", "Yes", "Yes", "Yes"),
        ("EMP-10078", "Robert Chen", "25/04/1982", "M", "15/08/2016", "8", "Engineering", "85000", "Yes", "Yes", "Yes – 8%", "Yes", "No", "Yes"),
        ("EMP-10083", "Emma Richardson", "12/12/1995", "F", "01/07/2022", "3", "HR", "38000", "Yes", "No", "Yes – 3%", "No", "Yes", "No"),
        ("EMP-10096", "Michael Okafor", "19/06/1987", "M", "15/11/2017", "7", "Risk", "70000", "Yes", "Yes", "Yes – 8%", "Yes", "Yes", "Yes"),
        ("EMP-10104", "Charlotte Hughes", "03/02/1980", "F", "01/01/2014", "10", "Exec", "120000", "Yes", "Yes", "Yes – 15%", "Yes", "Yes", "Yes"),
        ("EMP-10112", "Arjun Singh", "27/08/1993", "M", "01/10/2023", "2", "Customer Service", "32000", "Yes", "No", "Yes – 3%", "No", "No", "No"),
        ("EMP-10125", "Laura McGregor", "11/05/1984", "F", "15/03/2016", "8", "Compliance", "82000", "Yes", "Yes", "Yes – 8%", "Yes", "Yes", "Yes"),
        ("EMP-10131", "Thomas Brown", "29/10/1991", "M", "01/09/2020", "5", "Sales", "52000", "Yes", "Yes", "Yes – 5%", "Yes", "Yes", "No"),
    ]

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for emp in employees:
            writer.writerow(emp)

    print(f"  [CSV]  {path}")


# ===================================================================
# 4. Word (.docx) – Critical Illness Policy Wording
# ===================================================================

def _create_critical_illness_docx():
    """Group Critical Illness cover as a formatted Word document."""
    from docx import Document
    from docx.shared import Inches, Pt, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT

    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10)
    style.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)

    for level in range(1, 4):
        hs = doc.styles[f"Heading {level}"]
        hs.font.color.rgb = RGBColor(0x6F, 0x36, 0xA4)

    title = doc.add_heading("Royal London Group Critical Illness Cover", level=0)
    title.runs[0].font.color.rgb = RGBColor(0x6F, 0x36, 0xA4)
    doc.add_paragraph(
        "Benefit Specification & Conditions 2025/26\n"
        "Policy Reference: RL-GCI-2025-5567"
    )

    doc.add_heading("1. Scheme Details", level=1)
    doc.add_paragraph(
        "This Group Critical Illness (GCI) scheme is underwritten by Royal London "
        "(The Royal London Mutual Insurance Society Limited) under policy number "
        "RL-GCI-2025-5567, effective from 01 April 2025 to 31 March 2026."
    )
    doc.add_paragraph(
        "All UK permanent employees with a minimum of 3 months continuous service "
        "are eligible for cover under this scheme. The FCA registration number is 117672."
    )

    doc.add_heading("2. Benefit Structure", level=1)
    doc.add_paragraph(
        "The benefit is calculated as 3x Annual Basic Salary, subject to a maximum "
        "benefit cap of £500,000. Payment is made as a tax-free lump sum upon "
        "diagnosis of a covered condition, provided the member survives 14 days "
        "from the date of diagnosis."
    )

    doc.add_heading("2.1 Covered Conditions", level=2)
    doc.add_paragraph(
        "The scheme covers 58 specified critical illnesses plus 19 additional "
        "children's conditions. Key covered conditions include:"
    )

    conditions = [
        ("Cancer", "All invasive malignant cancers (excluding non-melanoma skin cancer and CIS)"),
        ("Heart Attack", "Of specified severity per ABI+ model wording"),
        ("Stroke", "Resulting in permanent neurological deficit lasting 24+ hours"),
        ("Multiple Sclerosis", "Definitive diagnosis by consultant neurologist"),
        ("Organ Transplant", "Heart, lung, liver, kidney, or pancreas"),
        ("Dementia / Alzheimer's", "Permanent diagnosis before age 65"),
        ("Parkinson's Disease", "Definitive diagnosis with permanent symptoms"),
        ("Major Organ Failure", "Permanent failure requiring ongoing treatment"),
    ]

    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Light Shading Accent 1"
    hdr = table.rows[0].cells
    hdr[0].text = "Condition"
    hdr[1].text = "Definition"
    for cond, defn in conditions:
        row = table.add_row().cells
        row[0].text = cond
        row[1].text = defn

    doc.add_paragraph()

    doc.add_heading("2.2 Partial Payment Conditions", level=2)
    doc.add_paragraph(
        "8 conditions are eligible for a 25% advance payment, including less "
        "advanced cancers (e.g., early-stage prostate cancer with Gleason score <7), "
        "coronary artery bypass graft, and carcinoma in situ of the breast."
    )

    doc.add_heading("3. Premium Rates", level=1)

    rate_table = doc.add_table(rows=1, cols=4)
    rate_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    rate_table.style = "Light Shading Accent 1"
    rh = rate_table.rows[0].cells
    rh[0].text = "Age Band"
    rh[1].text = "Rate (% Payroll)"
    rh[2].text = "Monthly (£50k)"
    rh[3].text = "Annual (£50k)"

    rates = [
        ("Under 30", "0.22%", "£9.17", "£110.00"),
        ("30-39", "0.48%", "£20.00", "£240.00"),
        ("40-49", "1.10%", "£45.83", "£550.00"),
        ("50-59", "2.65%", "£110.42", "£1,325.00"),
    ]
    for age, pct, monthly, annual in rates:
        row = rate_table.add_row().cells
        row[0].text = age
        row[1].text = pct
        row[2].text = monthly
        row[3].text = annual

    doc.add_paragraph("\nPremium Basis: Monthly in arrears, employer funded 100%.")

    doc.add_heading("4. Free Cover Limit", level=1)
    doc.add_paragraph(
        "The Free Cover Limit (FCL) for this scheme is £350,000. Members with a "
        "benefit amount exceeding the FCL will be required to complete a Royal London "
        "personal health declaration. Medical History Disregarded underwriting applies "
        "for benefits below the FCL."
    )

    doc.add_heading("5. Exclusions & Conditions", level=1)
    exclusions = [
        "Pre-existing conditions present within 5 years before cover start may be excluded.",
        "Members must be actively at work on the scheme entry date (Active Employment Clause).",
        "HIV/AIDS is only covered if contracted through blood transfusion, assault, or occupation.",
        "Conditions arising from deliberate self-harm or substance abuse are excluded.",
        "Worldwide coverage applies, but UK medical evidence is required for all claims.",
    ]
    for exc in exclusions:
        doc.add_paragraph(exc, style="List Bullet")

    doc.add_paragraph()
    footer = doc.add_paragraph(FOOTER_TEXT)
    footer.runs[0].font.size = Pt(7)
    footer.runs[0].font.italic = True
    footer.runs[0].font.color.rgb = RGBColor(0x64, 0x64, 0x6E)

    path = os.path.join(OUTPUT_DIR, "rl_group_critical_illness_2025.docx")
    doc.save(path)
    print(f"  [DOCX] {path}")


# ===================================================================
# 5. Word (.docx) – Dental & Optical Cash Plan
# ===================================================================

def _create_dental_optical_docx():
    """Dental & Optical cash plan as a Word document."""
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.table import WD_TABLE_ALIGNMENT

    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10)
    style.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)

    for level in range(1, 4):
        doc.styles[f"Heading {level}"].font.color.rgb = RGBColor(0x6F, 0x36, 0xA4)

    title = doc.add_heading("Royal London Dental & Optical Benefit Plan", level=0)
    title.runs[0].font.color.rgb = RGBColor(0x6F, 0x36, 0xA4)
    doc.add_paragraph(
        "Group Cash Plan Specification 2025/26\n"
        "Policy Reference: RL-DOP-2025-7712"
    )

    doc.add_heading("1. Scheme Overview", level=1)
    doc.add_paragraph(
        "This Group Cash Plan is underwritten by Royal London under policy number "
        "RL-DOP-2025-7712, effective 01 April 2025 to 31 March 2026. All UK "
        "permanent employees are eligible from date of joining."
    )

    doc.add_heading("2. Dental Benefits", level=1)
    dental_items = [
        ("NHS Dental Check-up", "100% reimbursement up to £65 per visit (2 visits per year)"),
        ("NHS Dental Treatment", "Reimbursement up to £250 per year (Band 1-3)"),
        ("Private Dental Treatment", "50% reimbursement up to £500 per year"),
        ("Dental Accident", "Up to £1,500 for emergency treatment following accidental injury"),
        ("Orthodontics (Dependants)", "50% reimbursement up to £750 for children under 18"),
    ]
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Light Shading Accent 1"
    table.rows[0].cells[0].text = "Benefit"
    table.rows[0].cells[1].text = "Coverage"
    for benefit, coverage in dental_items:
        row = table.add_row().cells
        row[0].text = benefit
        row[1].text = coverage

    doc.add_paragraph()

    doc.add_heading("3. Optical Benefits", level=1)
    optical_items = [
        ("Eye Test", "100% reimbursement up to £40 per test (1 per year)"),
        ("Prescription Glasses", "Up to £200 per pair (1 claim per 2 years)"),
        ("Contact Lenses", "Up to £200 per year"),
        ("Laser Eye Surgery", "£250 one-off contribution (lifetime limit)"),
    ]
    table2 = doc.add_table(rows=1, cols=2)
    table2.alignment = WD_TABLE_ALIGNMENT.CENTER
    table2.style = "Light Shading Accent 1"
    table2.rows[0].cells[0].text = "Benefit"
    table2.rows[0].cells[1].text = "Coverage"
    for benefit, coverage in optical_items:
        row = table2.add_row().cells
        row[0].text = benefit
        row[1].text = coverage

    doc.add_paragraph()

    doc.add_heading("4. Premium Rates", level=1)
    premiums = [
        ("Employee Only", "£12.50 per month"),
        ("Employee + Partner", "£22.00 per month"),
        ("Employee + Children", "£18.50 per month"),
        ("Family", "£28.00 per month"),
    ]
    for tier, cost in premiums:
        doc.add_paragraph(f"{tier}: {cost}", style="List Bullet")
    doc.add_paragraph(
        "Premium Basis: Monthly via payroll deduction; employee funded with "
        "employer subsidy of 50%."
    )

    doc.add_heading("5. General Conditions", level=1)
    conditions = [
        "Waiting Period: None for dental; 3 months for optical.",
        "Claims submitted via Royal London online portal or mobile app within 90 days.",
        "Maximum Annual Benefit: £2,500 aggregate across all dental and optical claims.",
        "Excluded: Cosmetic dentistry not clinically necessary; sunglasses; designer frames above £200 allowance.",
    ]
    for cond in conditions:
        doc.add_paragraph(cond, style="List Bullet")

    doc.add_paragraph()
    footer = doc.add_paragraph(FOOTER_TEXT)
    footer.runs[0].font.size = Pt(7)
    footer.runs[0].font.italic = True
    footer.runs[0].font.color.rgb = RGBColor(0x64, 0x64, 0x6E)

    path = os.path.join(OUTPUT_DIR, "rl_dental_optical_plan_2025.docx")
    doc.save(path)
    print(f"  [DOCX] {path}")


# ===================================================================
# Main
# ===================================================================

if __name__ == "__main__":
    _ensure("fpdf", "fpdf2")
    _ensure("openpyxl")
    _ensure("docx", "python-docx")

    print("Generating Royal London mock documents...\n")

    for plan in PDF_PLANS:
        _create_pdf(plan)

    _create_income_protection_xlsx()
    _create_contribution_schedule_xlsx()
    _create_eligibility_csv()
    _create_critical_illness_docx()
    _create_dental_optical_docx()

    print(f"\nDone! 7 documents created in {OUTPUT_DIR}")
    print("  2x PDF, 2x XLSX, 1x CSV, 2x DOCX")
