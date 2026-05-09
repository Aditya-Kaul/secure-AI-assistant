"""
All configuration and constants in one place.
Every other module imports from here — never from os.environ directly.
"""

import os
from dotenv import load_dotenv

load_dotenv()


GROQ_API_KEY: str = os.environ["GROQ_API_KEY"]
MODEL:        str = os.getenv("MODEL", "llama-3.1-8b-instant")


RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", 20))
RATE_LIMIT_WINDOW:   int = int(os.getenv("RATE_LIMIT_WINDOW",   60))


from pathlib import Path

BASE_DIR    = Path(__file__).resolve().parent.parent   
DB_PATH     = BASE_DIR / "db"    / "cineverse.db"
CHUNKS_PATH = BASE_DIR / "db"    / "pdf_chunks.json"
CSV_DIR     = BASE_DIR / "data"  / "csvs"
PDF_DIR     = BASE_DIR / "data"  / "pdfs"
SCHEMA_PATH = BASE_DIR / "db"    / "schema.sql"


SQL_MAX_ROWS:     int = 100
PDF_MAX_RESULTS:  int = 5
CSV_MAX_PREVIEW:  int = 20
MAX_TOOL_ROUNDS:  int = 4


ALLOWED_ORIGINS: list[str] = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000"
).split(",")