from __future__ import annotations
from backend.app.core.config import SETTINGS
from .models import CheckResult, Incident


def to_incident(check: CheckResult) -> Incident:
    severity = "medium"
    incident_type = check.check_type
    title = f"{check.node_name} {check.check_type.upper()} issue"

    if check.status == "critical":
        if check.check_type == "http":
            severity = SETTINGS["rules"].get("http_down_severity", "critical")
        elif check.check_type == "tcp":
            severity = SETTINGS["rules"].get("tcp_down_severity", "high")
        elif check.check_type == "latency":
            severity = "high"
        elif check.target in {"cpu", "memory", "disk"}:
            severity = "high"
    else:
        severity = "medium"

    return Incident(
        node_id=check.node_id,
        node_name=check.node_name,
        severity=severity,  # type: ignore[arg-type]
        incident_type=incident_type,
        title=title,
        details=f"Target={check.target}; details={check.details}; value={check.value} {check.unit or ''}".strip(),
    )


def detect_incidents(checks: list[CheckResult]) -> list[Incident]:
    incidents = []
    for check in checks:
        if check.status in {"warning", "critical"}:
            incidents.append(to_incident(check))
    return incidents
