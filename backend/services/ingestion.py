# Data Ingestion Service
# usage: python -m backend.services.ingestion

import sqlite3
import csv
import os
import logging
from pathlib import Path
import json
from pypdf import PdfReader

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

# Paths  and constants
BASE_DIR  = Path(__file__).resolve().parent.parent          # backend/
DB_PATH   = BASE_DIR / "db" / "cineverse.db"
SCHEMA    = BASE_DIR / "db" / "schema.sql"
CSV_DIR   = BASE_DIR / "data" / "csvs"

PDF_DIR     = BASE_DIR / "data" / "pdfs"
CHUNKS_PATH = BASE_DIR / "db" / "pdf_chunks.json"
CHUNK_SIZE  = 400  

# Maps CSV filename → table name
CSV_TABLE_MAP = {
    "movies.csv":               "movies",
    "viewers.csv":              "viewers",
    "watch_activity.csv":       "watch_activity",
    "reviews.csv":              "reviews",
    "marketing_spend.csv":      "marketing_spend",
    "regional_performance.csv": "regional_performance",
}


def get_connection() -> sqlite3.Connection:
    """Return a connection with FK enforcement and row_factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")   # better concurrent reads
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """Create tables, indexes, and views from schema.sql."""
    log.info("Applying schema from %s", SCHEMA)
    with open(SCHEMA, "r") as f:
        sql = f.read()
    conn.executescript(sql)
    conn.commit()
    log.info("Schema ready ✓")


def load_csv(conn: sqlite3.Connection, csv_path: Path, table: str) -> int:
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        log.warning("  %s — empty file, skipping", csv_path.name)
        return 0

    VIRTUAL_COLS = {"release_year", "roi"}
    columns     = [c for c in rows[0].keys() if c not in VIRTUAL_COLS]
    placeholders = ", ".join(["?" for _ in columns])
    col_names    = ", ".join(columns)
    sql = f"INSERT OR REPLACE INTO {table} ({col_names}) VALUES ({placeholders})"

    good, skipped = [], []
    for i, row in enumerate(rows, start=2):   # start=2 → row 1 is header
        # ── Guard: skip rows where the primary key looks like a header repeat
        pk_col = columns[0]
        if row[pk_col] == pk_col:
            log.warning("  %s row %d looks like a duplicate header — skipped", csv_path.name, i)
            skipped.append(i)
            continue
        good.append(tuple(row[c] if row[c] != "" else None for c in columns))

    if skipped:
        log.warning("  %s — skipped %d bad rows: %s", csv_path.name, len(skipped), skipped)

    with conn:
        conn.executemany(sql, good)

    log.info("  %-30s → %d rows loaded into [%s]", csv_path.name, len(good), table)
    return len(good)

def chunk_pdfs() -> int:
    all_chunks = []
    chunk_index = 0

    for pdf_path in sorted(PDF_DIR.glob("*.pdf")):
        log.info("  Chunking %s", pdf_path.name)
        try:
            reader = PdfReader(str(pdf_path))
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                # Slide a window with 50-char overlap for context continuity
                start = 0
                while start < len(text):
                    chunk_text = text[start: start + CHUNK_SIZE].strip()
                    if len(chunk_text) > 50:   # skip tiny fragments
                        all_chunks.append({
                            "chunk_index": chunk_index,
                            "source":      pdf_path.name,
                            "page":        page_num,
                            "text":        chunk_text,
                        })
                        chunk_index += 1
                    start += CHUNK_SIZE - 50   # 50-char overlap

        except Exception as e:
            log.error("  Failed to chunk %s: %s", pdf_path.name, e)

    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    log.info("  PDF chunking complete — %d chunks from %d files",
             len(all_chunks), len(list(PDF_DIR.glob("*.pdf"))))
    return len(all_chunks)



def ingest_all() -> dict:
    # main fubction
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    init_schema(conn)

    summary = {}
    total = 0
    for filename, table in CSV_TABLE_MAP.items():
        csv_path = CSV_DIR / filename
        if not csv_path.exists():
            log.error("  MISSING: %s", csv_path)
            summary[table] = {"status": "missing", "rows": 0}
            continue
        try:
            n = load_csv(conn, csv_path, table)
            summary[table] = {"status": "ok", "rows": n}
            total += n
        except Exception as e:
            log.error("  FAILED loading %s: %s", filename, e)
            summary[table] = {"status": "error", "message": str(e), "rows": 0}

    conn.close()

    pdf_chunks = chunk_pdfs()
    summary["pdf_chunks"] = {"status": "ok", "chunks": pdf_chunks}

    log.info(" Ingestion complete — %d rows, %d PDF chunks", total, pdf_chunks)
    return {"tables": summary, "total_rows": total, "pdf_chunks": pdf_chunks}


def verify_ingestion() -> None:
    """Quick sanity check — prints row counts for all tables."""
    conn = get_connection()
    print("\n── Row counts")
    for table in CSV_TABLE_MAP.values():
        cur = conn.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"  {table:<30} {count:>5} rows")
    print()

    print("── Views check ")
    views = ["vw_movie_performance", "vw_city_engagement",
             "vw_marketing_performance", "vw_genre_summary"]
    for v in views:
        cur = conn.execute(f"SELECT COUNT(*) FROM {v}")
        count = cur.fetchone()[0]
        print(f"  {v:<35} {count:>5} rows")
    print()
    conn.close()


#  Run directly to ingest and verify
if __name__ == "__main__":
    ingest_all()
    verify_ingestion()