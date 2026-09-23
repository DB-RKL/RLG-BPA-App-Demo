#!/usr/bin/env python3
"""Deploy the BPA AI/BI (Lakeview) reporting dashboard.

Steps:
  1. Run the DDL in sql/reporting_dashboard_views.sql on the SQL warehouse.
  2. Create or update the Lakeview dashboard (using dashboards/bpa_reporting.lvdash.json).
  3. Publish it.
  4. Print the embed URL to paste into app.yaml as DATABRICKS_DASHBOARD_URL.

Usage:
    python3 scripts/deploy_dashboard.py --profile e2-demo-west
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DASHBOARD_JSON = REPO / "dashboards" / "bpa_reporting.lvdash.json"
DASHBOARD_ID_FILE = REPO / "dashboards" / "bpa_reporting.dashboard_id"
# vw_portfolio_overview (in reporting_dashboard_views.sql) depends on the base
# views in powerbi_views.sql, so both files are run in order.
BASE_VIEW_SQL = REPO / "sql" / "powerbi_views.sql"
VIEW_SQL = REPO / "sql" / "reporting_dashboard_views.sql"

DISPLAY_NAME = "BPA Portfolio Insights"
WAREHOUSE_ID = "ced20c73f16a2915"
PARENT_PATH = "/Workspace/Users/rubjit.lalli@databricks.com"


def _client(profile: str | None):
    """Build a WorkspaceClient that survives the multi-profile .databrickscfg setup.

    The host in e2-demo-field-eng matches several profiles, which breaks the
    SDK's default databricks-cli auth mode. We work around it by asking the
    CLI for a PAT up-front using the explicit profile and feeding it to the
    SDK as a bearer token.
    """
    import os
    import subprocess

    for key in ("DATABRICKS_HOST", "DATABRICKS_TOKEN", "DATABRICKS_CONFIG_PROFILE"):
        os.environ.pop(key, None)

    from databricks.sdk import WorkspaceClient
    from databricks.sdk.config import Config

    if profile:
        cli = shutil.which("databricks") or "/opt/homebrew/bin/databricks"
        env = os.environ.copy()
        env["DATABRICKS_CLI_DO_NOT_EXECUTE_NEWER_VERSION"] = "1"
        host_result = subprocess.run(
            [cli, "auth", "env", "--profile", profile],
            check=True, capture_output=True, text=True, env=env,
        )
        host = (
            json.loads(host_result.stdout)
            .get("env", {})
            .get("DATABRICKS_HOST", "")
            .rstrip("/")
        )
        if not host:
            raise SystemExit(
                f"Could not determine host for profile {profile} (output: {host_result.stdout})"
            )
        tok_result = subprocess.run(
            [cli, "auth", "token", "--profile", profile],
            check=True, capture_output=True, text=True, env=env,
        )
        token = json.loads(tok_result.stdout)["access_token"]
        return WorkspaceClient(config=Config(host=host, token=token))

    return WorkspaceClient()


def _split_statements(sql: str) -> list[str]:
    return [s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")]


def run_view_ddl(client) -> None:
    # The Statement Execution API runs one statement per call, so we split each
    # file and run the base views (powerbi_views.sql) before the dashboard view.
    for path in (BASE_VIEW_SQL, VIEW_SQL):
        print(f"[1/4] Running {path.name} on warehouse {WAREHOUSE_ID}")
        for stmt in _split_statements(path.read_text()):
            resp = client.statement_execution.execute_statement(
                statement=stmt,
                warehouse_id=WAREHOUSE_ID,
                wait_timeout="30s",
            )
            state = getattr(resp.status, "state", None) if resp.status else None
            if state and str(state).upper() not in {"SUCCEEDED", "STATEMENTSTATE.SUCCEEDED"}:
                err = getattr(resp.status, "error", None)
                raise SystemExit(f"DDL failed: {err}\n  stmt: {stmt[:160]}")
    print("       -> views created")


def load_cached_id() -> str | None:
    if DASHBOARD_ID_FILE.exists():
        cached = DASHBOARD_ID_FILE.read_text().strip()
        return cached or None
    return None


def create_or_update(client) -> str:
    serialized = DASHBOARD_JSON.read_text()
    cached = load_cached_id()

    from databricks.sdk.service.dashboards import Dashboard

    if cached:
        print(f"[2/4] Updating existing dashboard {cached}")
        try:
            dashboard = client.lakeview.update(
                dashboard_id=cached,
                dashboard=Dashboard(
                    display_name=DISPLAY_NAME,
                    warehouse_id=WAREHOUSE_ID,
                    serialized_dashboard=serialized,
                ),
            )
            return dashboard.dashboard_id
        except Exception as e:
            print(f"       -> update failed ({e}); creating a new dashboard")

    print(f"[2/4] Creating new dashboard under {PARENT_PATH}")
    dashboard = client.lakeview.create(
        dashboard=Dashboard(
            display_name=DISPLAY_NAME,
            warehouse_id=WAREHOUSE_ID,
            parent_path=PARENT_PATH,
            serialized_dashboard=serialized,
        )
    )
    DASHBOARD_ID_FILE.write_text(dashboard.dashboard_id)
    print(f"       -> cached id in {DASHBOARD_ID_FILE.name}")
    return dashboard.dashboard_id


def publish(client, dashboard_id: str) -> None:
    print(f"[3/4] Publishing dashboard {dashboard_id}")
    client.lakeview.publish(
        dashboard_id=dashboard_id,
        warehouse_id=WAREHOUSE_ID,
        embed_credentials=True,
    )


def print_embed_url(client, dashboard_id: str) -> None:
    host = client.config.host.rstrip("/")
    embed = f"{host}/embed/dashboardsv3/{dashboard_id}"
    print(f"[4/4] Embed URL (paste into app.yaml as DATABRICKS_DASHBOARD_URL):")
    print(f"       {embed}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default=None, help="Databricks CLI profile name")
    args = parser.parse_args()

    if not DASHBOARD_JSON.exists():
        raise SystemExit(
            f"Missing {DASHBOARD_JSON}. Run scripts/build_dashboard_json.py first."
        )

    client = _client(args.profile)
    run_view_ddl(client)
    dashboard_id = create_or_update(client)
    # Give the control plane a moment before publishing a newly created draft.
    time.sleep(1)
    publish(client, dashboard_id)
    print_embed_url(client, dashboard_id)


if __name__ == "__main__":
    main()
