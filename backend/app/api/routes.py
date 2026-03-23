from __future__ import annotations
from fastapi import APIRouter
from backend.app.services.orchestrator import run_scan_pipeline
from backend.app.services.repository import fetch_dashboard_data

router = APIRouter()


@router.get("/healthz")
def healthz() -> dict:
    return {"status": "ok", "service": "AutoNOC-X backend"}


@router.get("/dashboard-data")
def dashboard_data() -> dict:
    return fetch_dashboard_data()


@router.post("/scan")
def scan() -> dict:
    summary = run_scan_pipeline()
    return summary.model_dump()
