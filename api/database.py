"""SQLite setup: connection factory and schema initialisation."""
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv("DB_PATH", "users.db"))


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create tables if they don't exist yet."""
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT    NOT NULL,
                email   TEXT    NOT NULL UNIQUE,
                status  TEXT    NOT NULL DEFAULT 'active'
                            CHECK(status IN ('active', 'inactive', 'banned')),
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)
    print(f"[DB] Initialised — {DB_PATH.resolve()}")
