from __future__ import annotations
from datetime import datetime, timezone
import json
from typing import Iterable
from backend.app.core.database import get_conn
from .models import CheckResult, Incident, ActionResult


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def insert_metrics(results: Iterable[CheckResult]) -> None:
    with get_conn() as conn:
        conn.executemany(
            '''
            INSERT INTO metrics (created_at, node_id, node_name, metric_type, status, value, unit, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            [
                (
                    utc_now(),
                    r.node_id,
                    r.node_name,
                    r.check_type,
                    r.status,
                    r.value,
                    r.unit,
                    r.details,
                )
                for r in results
            ],
        )


def insert_incidents(incidents: Iterable[Incident]) -> None:
    with get_conn() as conn:
        conn.executemany(
            '''
            INSERT INTO incidents (created_at, node_id, node_name, severity, incident_type, title, details, auto_heal_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            [
                (
                    utc_now(),
                    i.node_id,
                    i.node_name,
                    i.severity,
                    i.incident_type,
                    i.title,
                    i.details,
                    i.auto_heal_status,
                )
                for i in incidents
            ],
        )


def insert_actions(actions: Iterable[ActionResult]) -> None:
    with get_conn() as conn:
        conn.executemany(
            '''
            INSERT INTO actions (created_at, node_id, node_name, action_type, command, execution_mode, result)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            [
                (
                    utc_now(),
                    a.node_id,
                    a.node_name,
                    a.action_type,
                    a.command,
                    a.execution_mode,
                    a.result,
                )
                for a in actions
            ],
        )


def fetch_dashboard_data(limit: int = 100) -> dict:
    with get_conn() as conn:
        metrics = conn.execute(
            "SELECT * FROM metrics ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        incidents = conn.execute(
            "SELECT * FROM incidents ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        actions = conn.execute(
            "SELECT * FROM actions ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return {
            "metrics": [dict(row) for row in metrics],
            "incidents": [dict(row) for row in incidents],
            "actions": [dict(row) for row in actions],
        }
