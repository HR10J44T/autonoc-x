from __future__ import annotations
from pathlib import Path
import yaml

ROOT_DIR = Path(__file__).resolve().parents[3]
CONFIG_DIR = ROOT_DIR / "config"
DATA_DIR = ROOT_DIR / "data"
LOGS_DIR = ROOT_DIR / "logs"
DB_PATH = DATA_DIR / "autonoc.db"


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


SETTINGS = load_yaml(CONFIG_DIR / "settings.yaml")
NODES = load_yaml(CONFIG_DIR / "nodes.yaml").get("nodes", [])
