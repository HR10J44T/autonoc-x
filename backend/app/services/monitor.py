from __future__ import annotations
import socket
import time
from urllib.parse import urlparse
import psutil
import requests
from backend.app.core.config import SETTINGS, NODES
from .models import CheckResult


def http_check(node: dict, check: dict) -> CheckResult:
    target = check["target"]
    start = time.perf_counter()
    try:
        response = requests.get(target, timeout=SETTINGS.get("http_timeout_seconds", 3))
        elapsed_ms = (time.perf_counter() - start) * 1000
        if 200 <= response.status_code < 400:
            return CheckResult(
                node_id=node["node_id"],
                node_name=node["name"],
                check_type="http",
                target=target,
                status="healthy",
                value=elapsed_ms,
                unit="ms",
                details=f"HTTP {response.status_code}",
            )
        return CheckResult(
            node_id=node["node_id"],
            node_name=node["name"],
            check_type="http",
            target=target,
            status="critical",
            value=elapsed_ms,
            unit="ms",
            details=f"HTTP {response.status_code}",
        )
    except Exception as exc:
        return CheckResult(
            node_id=node["node_id"],
            node_name=node["name"],
            check_type="http",
            target=target,
            status="critical",
            details=f"HTTP check failed: {exc}",
        )


def tcp_check(node: dict, check: dict) -> CheckResult:
    target = check["target"]
    host, port = target.split(":")
    start = time.perf_counter()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(SETTINGS.get("tcp_timeout_seconds", 2))
    try:
        sock.connect((host, int(port)))
        elapsed_ms = (time.perf_counter() - start) * 1000
        return CheckResult(
            node_id=node["node_id"],
            node_name=node["name"],
            check_type="tcp",
            target=target,
            status="healthy",
            value=elapsed_ms,
            unit="ms",
            details="TCP reachable",
        )
    except Exception as exc:
        return CheckResult(
            node_id=node["node_id"],
            node_name=node["name"],
            check_type="tcp",
            target=target,
            status="critical",
            details=f"TCP check failed: {exc}",
        )
    finally:
        sock.close()


def latency_check(node: dict, check: dict) -> CheckResult:
    target = check["target"]
    port = 53
    start = time.perf_counter()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(SETTINGS.get("latency_timeout_seconds", 2))
    try:
        sock.connect((target, port))
        elapsed_ms = (time.perf_counter() - start) * 1000
        warn = SETTINGS["rules"].get("latency_warning_ms", 120)
        crit = SETTINGS["rules"].get("latency_critical_ms", 250)
        status = "healthy"
        if elapsed_ms >= crit:
            status = "critical"
        elif elapsed_ms >= warn:
            status = "warning"
        return CheckResult(
            node_id=node["node_id"],
            node_name=node["name"],
            check_type="latency",
            target=target,
            status=status,
            value=elapsed_ms,
            unit="ms",
            details="Latency estimated via TCP connect:53",
        )
    except Exception as exc:
        return CheckResult(
            node_id=node["node_id"],
            node_name=node["name"],
            check_type="latency",
            target=target,
            status="critical",
            details=f"Latency check failed: {exc}",
        )
    finally:
        sock.close()


def system_check() -> list[CheckResult]:
    cpu = psutil.cpu_percent(interval=0.2)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    out = []
    rules = SETTINGS.get("rules", {})
    for metric_name, value, threshold in [
        ("cpu", cpu, rules.get("cpu_critical_threshold", 90)),
        ("memory", mem, rules.get("memory_critical_threshold", 90)),
        ("disk", disk, rules.get("disk_critical_threshold", 90)),
    ]:
        out.append(
            CheckResult(
                node_id="local-system",
                node_name="Local Host",
                check_type="system",
                target=metric_name,
                status="critical" if value >= threshold else "healthy",
                value=value,
                unit="%",
                details=f"{metric_name.upper()} utilization",
            )
        )
    return out


def run_all_checks() -> list[CheckResult]:
    results: list[CheckResult] = []
    for node in NODES:
        for check in node.get("checks", []):
            check_type = check.get("type")
            if check_type == "http":
                results.append(http_check(node, check))
            elif check_type == "tcp":
                results.append(tcp_check(node, check))
            elif check_type == "latency":
                results.append(latency_check(node, check))
    results.extend(system_check())
    return results
