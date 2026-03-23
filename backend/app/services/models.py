from __future__ import annotations
from typing import Optional, Literal, List
from pydantic import BaseModel, Field


class CheckResult(BaseModel):
    node_id: str
    node_name: str
    check_type: Literal["http", "tcp", "latency", "system"]
    target: str
    status: Literal["healthy", "warning", "critical"]
    value: Optional[float] = None
    unit: Optional[str] = None
    details: str = ""


class Incident(BaseModel):
    node_id: str
    node_name: str
    severity: Literal["info", "medium", "high", "critical"]
    incident_type: str
    title: str
    details: str
    auto_heal_status: str = "pending"


class ActionResult(BaseModel):
    node_id: str
    node_name: str
    action_type: str
    command: str
    execution_mode: Literal["safe", "live"]
    result: str


class ScanSummary(BaseModel):
    checks: List[CheckResult] = Field(default_factory=list)
    incidents: List[Incident] = Field(default_factory=list)
    actions: List[ActionResult] = Field(default_factory=list)
