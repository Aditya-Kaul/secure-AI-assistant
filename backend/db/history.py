"""
Query history — persists every chat query + tool trace to SQLite.
Separate table from the analytics data, same DB file.
"""
from __future__ import annotations
import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path

log = logging.getLogger(__name__)
DB_PATH = Path(__file__).resolve().parent / "cineverse.db"


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_table() -> None:
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS query_history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                question    TEXT NOT NULL,
                answer      TEXT,
                sources     TEXT,   -- JSON array
                tool_calls  TEXT,   -- JSON array
                duration_ms INTEGER,
                created_at  TEXT DEFAULT (datetime('now'))
            )
        """)


def save_query(
    question:    str,
    answer:      str,
    sources:     list,
    tool_calls:  list,
    duration_ms: int,
) -> None:
    _ensure_table()
    with _conn() as conn:
        conn.execute(
            """INSERT INTO query_history
               (question, answer, sources, tool_calls, duration_ms)
               VALUES (?, ?, ?, ?, ?)""",
            (
                question,
                answer,
                json.dumps(sources),
                json.dumps(tool_calls),
                duration_ms,
            ),
        )
    log.info("[history] Saved query: %s", question[:60])


def get_history(limit: int = 20) -> list[dict]:
    _ensure_table()
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM query_history ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()

    result = []
    for row in rows:
        r = dict(row)
        # Deserialize JSON fields
        r["sources"]    = json.loads(r["sources"]    or "[]")
        r["tool_calls"] = json.loads(r["tool_calls"] or "[]")
        result.append(r)
    return result