"""Small read-only config endpoints used by the frontend."""

import os

from fastapi import APIRouter

router = APIRouter(tags=["config"])


def _workspace_host() -> str:
    host = os.getenv("DATABRICKS_HOST", "")
    if host and not host.startswith("http"):
        host = f"https://{host}"
    return host.rstrip("/")


@router.get("/config/dashboard")
async def dashboard_config() -> dict:
    """Return the embed URL for the BPA Portfolio Insights Lakeview dashboard.

    The URL is injected via the `DATABRICKS_DASHBOARD_URL` env var (see
    app.yaml). Returning an empty string lets the frontend degrade gracefully
    during local dev where the env var isn't set.
    """
    return {"url": os.getenv("DATABRICKS_DASHBOARD_URL", "")}


@router.get("/config/powerbi")
async def powerbi_config() -> dict:
    """Return the embed URL for a Power BI dashboard (if one has been wired up).

    Accepts either a Power BI "Publish to web" URL or a secure embed URL. The
    value comes from ``POWERBI_EMBED_URL`` (see app.yaml). Returning an empty
    string lets the frontend hide the Power BI tab gracefully when unset.
    """
    return {"url": os.getenv("POWERBI_EMBED_URL", "").strip()}


@router.get("/config/genie")
async def genie_config() -> dict:
    """Return the embed URL for the Genie space (if one has been wired up).

    Preference order:
    1. ``DATABRICKS_GENIE_URL`` — full pre-built embed URL.
    2. ``DATABRICKS_GENIE_SPACE_ID`` + current workspace host — we assemble the
       standard ``/embed/genie/<space_id>`` URL.
    """
    explicit = os.getenv("DATABRICKS_GENIE_URL", "").strip()
    if explicit:
        return {"url": explicit}

    space_id = os.getenv("DATABRICKS_GENIE_SPACE_ID", "").strip()
    host = _workspace_host()
    if space_id and host:
        return {"url": f"{host}/embed/genie/rooms/{space_id}"}

    return {"url": ""}
