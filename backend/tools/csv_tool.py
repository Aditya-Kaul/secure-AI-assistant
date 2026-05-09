
# Csv or excel analyzer
# Runs filtered aggregations on CSV files directly.
# The AI never sees raw file paths — it picks from an approved registry., cool isnt it?


from __future__ import annotations

import csv
import logging
import statistics
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

CSV_DIR = Path(__file__).resolve().parent.parent / "data" / "csvs"

# ── Approved files only — AI cannot request arbitrary paths ──
APPROVED_FILES = {
    "movies":               "movies.csv",
    "viewers":              "viewers.csv",
    "watch_activity":       "watch_activity.csv",
    "reviews":              "reviews.csv",
    "marketing_spend":      "marketing_spend.csv",
    "regional_performance": "regional_performance.csv",
}

ALLOWED_AGGREGATIONS = {"count", "sum", "avg", "min", "max", "list"}


def _read_csv(filename: str) -> tuple[list[dict], list[str]]:
    """Returns (rows, columns)."""
    path = CSV_DIR / filename
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    columns = list(rows[0].keys()) if rows else []
    return rows, columns


def _apply_filters(rows: list[dict], filters: dict) -> list[dict]:
    """
    Filter rows by column equality.
    filters = {"genre": "Comedy", "year": "2025"}
    Supports simple equality and case-insensitive string match.
    """
    for col, val in filters.items():
        rows = [
            r for r in rows
            if col in r and str(r[col]).strip().lower() == str(val).strip().lower()
        ]
    return rows


def _aggregate(rows: list[dict], column: str, aggregation: str) -> Any:
    """Run a single aggregation on a column across filtered rows."""
    values = [r.get(column, "") for r in rows]

    # Try numeric conversion
    numeric = []
    for v in values:
        try:
            numeric.append(float(v))
        except (ValueError, TypeError):
            pass

    agg = aggregation.lower()

    if agg == "count":
        return len(rows)
    if agg == "list":
        return values[:20]  # cap list output
    if not numeric:
        return {"error": f"Column '{column}' has no numeric values for '{agg}'"}
    if agg == "sum":
        return round(sum(numeric), 2)
    if agg == "avg":
        return round(statistics.mean(numeric), 2)
    if agg == "min":
        return round(min(numeric), 2)
    if agg == "max":
        return round(max(numeric), 2)

    return {"error": f"Unknown aggregation: {aggregation}"}


def analyze_csv(
    file: str,
    filters: dict | None = None,
    aggregation: str | None = None,
    column: str | None = None,
    group_by: str | None = None,
) -> dict[str, Any]:

    log.info("[csv_tool] file=%s filters=%s agg=%s col=%s group_by=%s",
             file, filters, aggregation, column, group_by)

    if file not in APPROVED_FILES:
        return {
            "success": False,
            "error": f"File '{file}' not in approved list: {list(APPROVED_FILES.keys())}",
        }

    if aggregation and aggregation.lower() not in ALLOWED_AGGREGATIONS:
        return {
            "success": False,
            "error": f"Aggregation '{aggregation}' not allowed. Use: {ALLOWED_AGGREGATIONS}",
        }

    try:
        rows, columns = _read_csv(APPROVED_FILES[file])
    except FileNotFoundError:
        return {"success": False, "error": f"CSV file not found for '{file}'"}
    except Exception as e:
        return {"success": False, "error": f"Failed to read CSV: {str(e)}"}

    
    filtered = _apply_filters(rows, filters or {})

    if column and column not in columns:
        return {
            "success": False,
            "error": f"Column '{column}' not found. Available: {columns}",
        }

    grouped_result = None
    if group_by:
        if group_by not in columns:
            return {"success": False, "error": f"group_by column '{group_by}' not found."}
        groups: dict[str, list] = {}
        for row in filtered:
            key = row.get(group_by, "unknown")
            groups.setdefault(key, []).append(row)

        if aggregation and column:
            grouped_result = {
                k: _aggregate(v, column, aggregation)
                for k, v in groups.items()
            }
        else:
            grouped_result = {k: len(v) for k, v in groups.items()}

  
    simple_result = None
    if aggregation and column and not group_by:
        simple_result = _aggregate(filtered, column, aggregation)
    elif not aggregation:
        simple_result = filtered[:20]

    log.info("[csv_tool] Done. rows_after_filter=%d", len(filtered))
    return {
        "success":         True,
        "file":            file,
        "filters_applied": filters or {},
        "row_count":       len(filtered),
        "columns":         columns,
        "result":          simple_result,
        "grouped":         grouped_result,
        "error":           None,
    }