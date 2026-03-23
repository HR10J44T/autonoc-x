from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from .config import DB_PATH, DATA_DIR


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            node_id TEXT NOT NULL,
            node_name TEXT NOT NULL,
            metric_type TEXT NOT NULL,
            status TEXT NOT NULL,
            value REAL,
            unit TEXT,
            details TEXT
        )
        '''
    )
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            node_id TEXT NOT NULL,
            node_name TEXT NOT NULL,
            severity TEXT NOT NULL,
            incident_type TEXT NOT NULL,
            title TEXT NOT NULL,
            details TEXT,
            auto_heal_status TEXT NOT NULL
        )
        '''
    )
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            node_id TEXT NOT NULL,
            node_name TEXT NOT NULL,
            action_type TEXT NOT NULL,
            command TEXT NOT NULL,
            execution_mode TEXT NOT NULL,
            result TEXT NOT NULL
        )
        '''
    )
    conn.commit()
    conn.close()


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
