from __future__ import annotations
import subprocess
from backend.app.core.config import SETTINGS
from .models import Incident, ActionResult


def choose_action(incident: Incident) -> tuple[str, str]:
    itype = incident.incident_type
    if itype == "http":
        return "restart_service", "systemctl restart nginx"
    if itype == "tcp":
        return "restart_network_service", "systemctl restart networking"
    if itype == "latency":
        return "reroute_traffic_simulated", "ip route replace default via 192.168.1.254"
    if "cpu" in incident.details.lower():
        return "kill_high_cpu_process_simulated", "pkill -f stress"
    if "memory" in incident.details.lower():
        return "restart_memory_intensive_service_simulated", "systemctl restart app-worker"
    if "disk" in incident.details.lower():
        return "cleanup_logs_simulated", "find /var/log -type f -name '*.log' -delete"
    return "notify_only", "echo no-op"


def execute_actions(incidents: list[Incident]) -> list[ActionResult]:
    results: list[ActionResult] = []
    safe_mode = SETTINGS.get("safe_mode", True)

    for incident in incidents:
        action_type, command = choose_action(incident)
        execution_mode = "safe" if safe_mode else "live"
        result = "simulated_success"

        if not safe_mode:
            try:
                completed = subprocess.run(
                    command,
                    shell=True,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                result = (
                    completed.stdout.strip()
                    or completed.stderr.strip()
                    or f"returncode={completed.returncode}"
                )
            except Exception as exc:
                result = f"execution_failed: {exc}"

        incident.auto_heal_status = "completed" if result else "failed"

        results.append(
            ActionResult(
                node_id=incident.node_id,
                node_name=incident.node_name,
                action_type=action_type,
                command=command,
                execution_mode=execution_mode,  # type: ignore[arg-type]
                result=result,
            )
        )

    return results
