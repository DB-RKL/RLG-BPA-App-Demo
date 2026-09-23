#!/usr/bin/env python3
"""Simulate raw BPA scheme documents landing in cloud storage.

Synthesises a new prospect scheme's document pack (benefit spec, contribution
schedule, member data, funding update) with realistic-but-random values and
uploads them into the Unity Catalog Volume — so the Lakeflow (Auto Loader)
pipeline picks them up incrementally, exactly as it would when a sponsor adviser
emails a new pack. This is synthetic data only; no real customer content.

Usage:
    python3 scripts/simulate_document_arrivals.py --scheme halfords --display "Halfords Group Pension Scheme"
    python3 scripts/simulate_document_arrivals.py --scheme greggs   --display "Greggs plc Retirement Plan"
"""
from __future__ import annotations
import argparse, csv, io, json, random, subprocess, os

VOL = "/Volumes/serverless_stable_wx20co_catalog/bpa_rubjit/documents"
PROFILE = "fevm-serverless-stable-wx20co"
HOST = "https://fevm-serverless-stable-wx20co.cloud.databricks.com"

ACCRUAL = ["1/60th of Final Pensionable Salary", "1/80th of Final Pensionable Salary", "1/54th CARE revalued"]
INCREASE = ["CPI capped at 5% p.a.", "RPI capped at 2.5% p.a.", "CPI capped at 2.5% p.a. (min 0%)"]
INSURERS = ["Royal London", "Aviva", "Legal & General", "PIC"]


def _benefit_spec_csv(display: str, year: int) -> bytes:
    rows = [
        ["Field", "Value"],
        ["Scheme Name", display],
        ["Scheme Type", random.choice(["Defined Benefit - Final Salary (Closed)", "Defined Benefit - CARE (Closed)"])],
        ["Sponsoring Employer", display.split(" Pension")[0].split(" Retirement")[0]],
        ["Normal Retirement Age", str(random.choice([60, 63, 65]))],
        ["Benefit Accrual Rate", random.choice(ACCRUAL)],
        ["Pension Increase Basis", random.choice(INCREASE)],
        ["Revaluation Rate in Deferment", random.choice(INCREASE)],
        ["Commutation Factor", f"GBP {random.randint(12,20)} of pension for GBP {random.randint(200,300)} cash"],
        ["Spouse's Pension", f"{random.choice([50,66])}% of member's pension"],
        ["Scheme Actuary", random.choice(["Mercer Limited", "WTW", "Aon", "XPS"])],
        ["Preferred Insurer", random.choice(INSURERS)],
        ["Document Year", str(year)],
    ]
    buf = io.StringIO(); csv.writer(buf).writerows(rows); return buf.getvalue().encode()


def _contribution_csv(display: str, year: int) -> bytes:
    rows = [["Member Category", "Employer Rate", "Employee Rate", "Effective Date"]]
    for cat in ["Active - Standard", "Active - Senior", "Deferred (deficit repair)"]:
        rows.append([cat, f"{random.randint(12,26)}.{random.randint(0,9)}%",
                     f"{random.randint(4,10)}.{random.randint(0,9)}%", f"01/04/{year}"])
    buf = io.StringIO(); csv.writer(buf).writerows(rows); return buf.getvalue().encode()


def _funding_csv(display: str, year: int) -> bytes:
    assets = random.randint(180, 950)
    tp = assets + random.randint(-60, 40)
    rows = [
        ["Metric", "Value (GBPm)"],
        ["Scheme Assets", f"{assets}"],
        ["Technical Provisions", f"{tp}"],
        ["Surplus / (Deficit)", f"{assets - tp}"],
        ["Funding Level", f"{round(assets/tp*100,1)}%"],
        ["Discount Rate", f"gilts + {random.randint(30,90)}bps"],
        ["Valuation Date", f"31/12/{year}"],
    ]
    buf = io.StringIO(); csv.writer(buf).writerows(rows); return buf.getvalue().encode()


def _member_xlsx(display: str, year: int) -> bytes:
    from openpyxl import Workbook
    wb = Workbook(); ws = wb.active; ws.title = "Member Data"
    ws.append(["Member ID", "Status", "Age", "Accrued Pension (GBP p.a.)", "Sex"])
    for i in range(1, 41):
        ws.append([f"M{i:04d}", random.choice(["Pensioner", "Deferred", "Active"]),
                   random.randint(38, 88), random.randint(1200, 42000), random.choice(["M", "F"])])
    bio = io.BytesIO(); wb.save(bio); return bio.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scheme", required=True, help="folder slug, e.g. halfords")
    ap.add_argument("--display", required=True, help="scheme display name")
    ap.add_argument("--year", type=int, default=2025)
    args = ap.parse_args()

    os.environ.setdefault("SSL_CERT_FILE", os.path.expanduser("~/dg-fraud-app/combined-ca-bundle.pem"))
    os.environ.setdefault("REQUESTS_CA_BUNDLE", os.path.expanduser("~/dg-fraud-app/combined-ca-bundle.pem"))
    from databricks.sdk import WorkspaceClient
    from databricks.sdk.config import Config
    tok = json.loads(subprocess.check_output(["databricks", "auth", "token", "-p", PROFILE]))["access_token"]
    w = WorkspaceClient(config=Config(host=HOST, token=tok))

    files = {
        f"{args.scheme}_benefit_spec_{args.year}.csv": _benefit_spec_csv(args.display, args.year),
        f"{args.scheme}_contribution_schedule_{args.year}.csv": _contribution_csv(args.display, args.year),
        f"{args.scheme}_funding_update_{args.year}_12.csv": _funding_csv(args.display, args.year),
        f"{args.scheme}_member_data_{args.year}.xlsx": _member_xlsx(args.display, args.year),
    }
    for name, content in files.items():
        remote = f"{VOL}/{args.scheme}/{name}"
        w.files.upload(remote, io.BytesIO(content), overwrite=True)
        print(f"  landed {remote} ({len(content)} bytes)")
    print(f"ARRIVED: {len(files)} files for '{args.display}' -> {VOL}/{args.scheme}/")


if __name__ == "__main__":
    main()
