"""
Generate realistic Royal London benefit specification PDFs for demo.
Run: python mock_data/generate_mock_pdfs.py

Requires: pip install fpdf2
"""

import os
import sys

try:
    from fpdf import FPDF
except ImportError:
    print("Installing fpdf2...")
    os.system(f"{sys.executable} -m pip install fpdf2")
    from fpdf import FPDF

OUTPUT_DIR = os.path.dirname(__file__)

RL_PURPLE = (111, 54, 164)
RL_PURPLE_LIGHT = (245, 238, 251)
RL_TEAL = (0, 122, 122)
RL_DARK = (26, 26, 46)
RL_GRAY = (100, 100, 110)

PLANS = [
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
                "Excluded Causes": "Suicide within first 12 months of cover; active participation in war or terrorism",
            },
        },
    },
    {
        "filename": "rl_group_income_protection_2025.pdf",
        "title": "Royal London Group Income Protection",
        "subtitle": "Income Protection Scheme Specification 2025/26",
        "ref": "RL-GIP-2025-4421",
        "sections": {
            "Scheme Details": {
                "Scheme Name": "Royal London Group Income Protection",
                "Scheme Type": "Group Income Protection (GIP)",
                "Underwriter": "Royal London",
                "Policy Number": "RL-GIP-2025-4421",
                "Effective Date": "01/04/2025",
                "Renewal Date": "31/03/2026",
                "Eligible Employees": "All UK permanent employees with 6+ months service",
                "FCA Registration": "117672",
            },
            "Benefit Structure": {
                "Benefit Percentage": "75% of pre-disability earnings (inclusive of state benefits)",
                "Income Definition": "Basic annual salary plus average of last 3 years' contractual bonus",
                "Maximum Monthly Benefit": "£15,000 per month",
                "Deferred Period - Standard": "26 weeks",
                "Deferred Period - Senior Management": "13 weeks",
                "Benefit Cease Age": "State Pension Age (SPA)",
                "Proportionate Benefit": "Yes - for phased return to work",
            },
            "Premium Rates": {
                "Employer Rate - Under 30": "0.45% of payroll",
                "Employer Rate - Age 30-39": "0.72% of payroll",
                "Employer Rate - Age 40-49": "1.35% of payroll",
                "Employer Rate - Age 50-59": "2.80% of payroll",
                "Premium Basis": "Monthly in arrears, employer funded 100%",
            },
            "Rehabilitation & Support": {
                "Early Intervention Service": "Included - vocational rehabilitation from week 4 of absence",
                "Employee Assistance Programme (EAP)": "Included - 24/7 confidential helpline and up to 6 counselling sessions",
                "Occupational Health Referral": "Available from day 1 of claim",
                "NHS Excess Waiver": "Included - benefit not reduced by NHS waiting times",
            },
            "Exclusions & Conditions": {
                "Pre-existing Condition Limitation": "Conditions disclosed and accepted at underwriting",
                "Active Employment Clause": "Member must be actively at work on scheme entry date",
                "Excluded Conditions": "Self-inflicted injuries; cosmetic procedures; normal pregnancy",
                "Linked Claims": "Same or related disability within 6 months treated as one claim",
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
                "Annual Management Charge (AMC)": "0.40% on default fund; 0.50% - 0.75% on self-select",
                "Independent Governance Committee (IGC)": "Royal London IGC provides annual Value for Money assessment",
                "Statement Frequency": "Annual benefit statement plus online portal access",
                "Chair's Statement": "Published annually per Pensions Act 2004 requirements",
            },
        },
    },
    {
        "filename": "rl_group_critical_illness_2025.pdf",
        "title": "Royal London Group Critical Illness Cover",
        "subtitle": "Benefit Specification & Conditions 2025/26",
        "ref": "RL-GCI-2025-5567",
        "sections": {
            "Scheme Details": {
                "Scheme Name": "Royal London Group Critical Illness",
                "Scheme Type": "Group Critical Illness (GCI)",
                "Underwriter": "Royal London",
                "Policy Number": "RL-GCI-2025-5567",
                "Effective Date": "01/04/2025",
                "Renewal Date": "31/03/2026",
                "Eligible Employees": "All UK permanent employees with 3+ months service",
            },
            "Benefit Structure": {
                "Benefit Multiple": "3x Annual Basic Salary",
                "Maximum Benefit Cap": "£500,000",
                "Number of Conditions Covered": "58 specified critical illnesses + 19 children's conditions",
                "Payment Type": "Lump sum on diagnosis and survival 14 days",
                "Partial Payment Conditions": "8 conditions eligible for 25% advance payment",
            },
            "Key Covered Conditions": {
                "Cancer": "Covered - all invasive malignant cancers (excluding non-melanoma skin cancer and CIS)",
                "Heart Attack": "Covered - of specified severity per ABI model wording",
                "Stroke": "Covered - resulting in permanent neurological deficit lasting 24+ hours",
                "Multiple Sclerosis": "Covered - definitive diagnosis by consultant neurologist",
                "Organ Transplant": "Covered - transplant of heart, lung, liver, kidney or pancreas",
                "Dementia / Alzheimer's": "Covered - permanent diagnosis before age 65",
            },
            "Premium Rates": {
                "Employer Rate - Under 30": "0.22% of payroll",
                "Employer Rate - Age 30-39": "0.48% of payroll",
                "Employer Rate - Age 40-49": "1.10% of payroll",
                "Employer Rate - Age 50-59": "2.65% of payroll",
                "Premium Basis": "Monthly in arrears, employer funded 100%",
            },
            "Exclusions & Conditions": {
                "Pre-existing Condition Exclusion": "Conditions present within 5 years before cover start may be excluded",
                "Active Employment Clause": "Member must be actively at work on scheme entry date",
                "HIV/AIDS": "Only covered if contracted through blood transfusion, assault or occupation",
                "Self-inflicted Conditions": "Excluded - conditions arising from deliberate self-harm or substance abuse",
                "Territorial Limit": "Worldwide coverage, UK medical evidence required for claims",
            },
        },
    },
    {
        "filename": "rl_dental_optical_plan_2025.pdf",
        "title": "Royal London Dental & Optical Benefit Plan",
        "subtitle": "Group Cash Plan Specification 2025/26",
        "ref": "RL-DOP-2025-7712",
        "sections": {
            "Scheme Details": {
                "Scheme Name": "Royal London Dental & Optical Cash Plan",
                "Scheme Type": "Group Cash Plan",
                "Underwriter": "Royal London",
                "Policy Number": "RL-DOP-2025-7712",
                "Effective Date": "01/04/2025",
                "Renewal Date": "31/03/2026",
                "Eligible Employees": "All UK permanent employees from date of joining",
            },
            "Dental Benefits": {
                "NHS Dental Check-up": "100% reimbursement up to £65 per visit (2 visits per year)",
                "NHS Dental Treatment": "Reimbursement up to £250 per year (Band 1-3)",
                "Private Dental Treatment": "50% reimbursement up to £500 per year",
                "Dental Accident Benefit": "Up to £1,500 for emergency treatment following accidental injury",
                "Orthodontics (Dependants)": "50% reimbursement up to £750 for dependent children under 18",
            },
            "Optical Benefits": {
                "Eye Test": "100% reimbursement up to £40 per test (1 per year)",
                "Prescription Glasses": "Up to £200 per pair (1 claim per 2 years)",
                "Contact Lenses": "Up to £200 per year",
                "Laser Eye Surgery Contribution": "£250 one-off contribution (lifetime limit)",
            },
            "Premium Rates": {
                "Employee Only": "£12.50 per month",
                "Employee + Partner": "£22.00 per month",
                "Employee + Children": "£18.50 per month",
                "Family (Employee + Partner + Children)": "£28.00 per month",
                "Premium Basis": "Monthly via payroll deduction; employee funded with employer subsidy of 50%",
            },
            "General Conditions": {
                "Waiting Period": "None for dental; 3 months for optical",
                "Claims Submission": "Via Royal London online portal or mobile app within 90 days of treatment",
                "Moratorium Period": "None - immediate cover from scheme entry",
                "Excluded Treatments": "Cosmetic dentistry not clinically necessary; sunglasses; designer frames above £200 allowance",
                "Maximum Annual Benefit": "£2,500 aggregate across all dental and optical claims",
            },
        },
    },
]


def create_pdf(plan: dict):
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
        pdf.cell(
            0, 8, f"  {section_title}",
            new_x="LMARGIN", new_y="NEXT", fill=True,
        )
        pdf.set_text_color(*RL_DARK)
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 9)
        for key, value in fields.items():
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*RL_GRAY)
            pdf.cell(85, 6, f"  {key}", border=0)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*RL_DARK)
            pdf.cell(0, 6, value, new_x="LMARGIN", new_y="NEXT")

        pdf.ln(3)

    pdf.ln(8)
    pdf.set_draw_color(*RL_PURPLE)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*RL_GRAY)
    pdf.multi_cell(
        0, 4,
        "The Royal London Mutual Insurance Society Limited is authorised by the "
        "Prudential Regulation Authority and regulated by the Financial Conduct "
        "Authority and the Prudential Regulation Authority. Registration number "
        "117672. Registered in England and Wales, company number 99064. "
        "Registered office: 80 Fenchurch Street, London, EC3M 4BY.\n\n"
        "This is a summary of benefits only. Please refer to the full scheme "
        "documentation for complete details, terms, conditions and exclusions. "
        "This summary does not constitute a contract of insurance.",
    )

    path = os.path.join(OUTPUT_DIR, plan["filename"])
    pdf.output(path)
    print(f"Created: {path}")


if __name__ == "__main__":
    for plan in PLANS:
        create_pdf(plan)
    print(f"\nDone! {len(PLANS)} Royal London mock PDFs created in {OUTPUT_DIR}")
