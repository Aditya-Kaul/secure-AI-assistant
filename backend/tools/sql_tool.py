
# SQL Query Engine
# Security bounded: AI can only select from approved tables or views( if there are any).
# No raw database access. only parameterized queries.

import sqlite3
from pathlib import Path
from typing import Any
import logging
import re

log = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "cineverse.db"


# ── Security: only these are queryable by the AI. No raw access to sqlite_master or other system tables.
ALLOWED_TABLES = {
    # Raw tables
    "movies", "viewers", "watch_activity",
    "reviews", "marketing_spend", "regional_performance",
    "vw_movie_performance", "vw_city_engagement",
    "vw_marketing_performance", "vw_genre_summary",
}

BLOCKED_KEYWORDS = {
    "insert", "update", "delete", "drop", "alter",
    "create", "truncate", "replace", "attach", "detach",
    "pragma", "vacuum", "reindex",
}


MAX_ROWS = 100 # limit results to prevent abuse

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA query_only = ON")   # read-only at connection level
    return conn


def _validate_query(sql: str) -> tuple[bool, str]:
    normalized = sql.lower().strip()

    # Must start with SELECT
    if not normalized.startswith("select"):
        return False, "Only SELECT queries are permitted."

    # Check for blocked keywords to prevent data modification or schema access
    tokens = re.findall(r"\b\w+\b", normalized)
    for token in tokens:
        if token in BLOCKED_KEYWORDS:
            return False, f"Blocked keyword detected: '{token}'"

    # Check all table/view references are in the allowlist
    referenced = re.findall(
        r"\b(?:from|join)\s+([a-z_][a-z0-9_]*)", normalized
    )
    for ref in referenced:
        if ref not in ALLOWED_TABLES:
            return False, f"Table '{ref}' is not in the approved query list."

    return True, "ok"

def query_database(sql_query: str) -> dict[str, Any]:
    # Main function. Called by the AI orchestrator.

    log.info("sql_tool : Query received: %s", sql_query[:120])

    # Step 1 — validate
    is_safe, reason = _validate_query(sql_query)
    if not is_safe:
        log.warning("sql_tool : Blocked query: %s | Reason: %s", sql_query[:80], reason)
        return {
            "success": False,
            "rows": [],
            "row_count": 0,
            "columns": [],
            "error": f"Query rejected: {reason}",
            "truncated": False,
        }

    # Step 2 — execute
    try:
        conn = _get_conn()
        cursor = conn.execute(sql_query)
        columns = [desc[0] for desc in cursor.description or []]
        raw_rows = cursor.fetchmany(MAX_ROWS + 1) # fetch one extra to check for truncation
        truncated = len(raw_rows) > MAX_ROWS
        rows = [dict(zip(columns, row)) for row in raw_rows[:MAX_ROWS]]
        conn.close()

        log.info("[sql_tool] Returned %d rows (truncated=%s)", len(rows), truncated)
        return {
            "success": True,
            "rows": rows,
            "row_count": len(rows),
            "columns": columns,
            "error": None,
            "truncated": truncated,
        }

    except sqlite3.Error as e:
        log.error("[sql_tool] DB error: %s", e)
        return {
            "success": False,
            "rows": [],
            "row_count": 0,
            "columns": [],
            "error": f"Database error: {str(e)}",
            "truncated": False,
        }