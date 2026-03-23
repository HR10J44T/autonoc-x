from __future__ import annotations
from .models import ScanSummary
from .monitor import run_all_checks
from .detection import detect_incidents
from .recovery_engine import execute_actions
from .repository import insert_metrics, insert_incidents, insert_actions


def run_scan_pipeline() -> ScanSummary:
    checks = run_all_checks()
    incidents = detect_incidents(checks)
    actions = execute_actions(incidents)
    insert_metrics(checks)
    insert_incidents(incidents)
    insert_actions(actions)
    return ScanSummary(checks=checks, incidents=incidents, actions=actions)
