# " CineVerse Analytics "

A secure AI-powered internal analytics assistant for cineverse Entertainment (an example business name).
Answers business questions by pulling from SQL, PDFs, and CSV files simultaneously
using tool-calling — the AI never touches raw data directly.

---

## Architecture

```
User (Browser)
     │
     ▼
Frontend — React + Recharts          :3000
     │
     ▼  HTTP
Backend — FastAPI + Python           :8000
     │
     ▼  Tool Calls
AI Orchestrator — Grok (xAI)
     │
     ├── Tool A: SQL Query Engine     → SQLite (structured data)
     ├── Tool B: PDF Retriever        → TF-IDF search over PDF chunks
     └── Tool C: CSV Analyzer         → Filtered aggregations on CSV files
```

**Security boundary:** The AI only calls curated tools with strict input
validation. It never receives raw DB access, file system paths, or API keys.

---

## Project Structure

```
cineverse/
├── backend/
│   ├── main.py                  # App factory — mounts routers only
│   ├── core/
│   │   └── config.py            # All env vars and constants
│   ├── api/
│   │   ├── utils.py      # Rate limiter (shared via Depends)
│   │   └── routes/
│   │       ├── chat.py          # POST /chat
│   │       ├── ingest.py        # POST /ingest
│   │       ├── analytics.py     # GET  /analytics
│   │       ├── query.py         # POST /query/sql, /query/docs, /query/csv
│   │       └── history.py       # GET  /history
│   ├── tools/
│   │   ├── sql_tool.py          # SELECT-only, approved tables, 100-row cap
│   │   ├── pdf_tool.py          # TF-IDF search over chunked PDFs
│   │   └── csv_tool.py          # Filtered aggregations, approved files only
│   ├── services/
│   │   ├── ai_orchestrator.py   # Agentic loop — Grok tool-calling
│   │   └── ingestion.py         # CSV loader + PDF chunker
│   ├── db/
│   │   ├── schema.sql           # Tables, indexes, views
│   │   └── history.py           # Query history persistence
│   └── data/
│       ├── csvs/                # 6 CSV files
│       └── pdfs/                # 5 PDF documents
├── frontend/
│   └── src/
│       ├── api.js               # All backend calls
│       ├── App.jsx              # Layout + routing
│       └── components/
│           ├── Sidebar.jsx      # Nav + film-strip motif
│           ├── ChatPanel.jsx    # Conversation + demo questions
│           ├── SourcePanel.jsx  # Tool trace drawer
│           ├── ChartView.jsx    # 4 charts + 2025 table
│           └── HistoryPanel.jsx # Expandable query history
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Quick Start

### Prerequisites
- Docker + Docker Compose
- A Grok API key from [https://console.groq.com/](https://api.groq.com/openai/v1)

### 1. Clone and configure

```bash
git clone https://github.com/your-username/secure-AI-assistant.git
cd secure-AI-assistant

cp .env.example .env
# Open .env and set your GROK_API_KEY
```

### 2. Add your data files

```bash
# CSVs go here
backend/data/csvs/
  movies.csv
  viewers.csv
  watch_activity.csv
  reviews.csv
  marketing_spend.csv
  regional_performance.csv

# PDFs go here (generate with generate_pdfs.py)
backend/data/pdfs/
  quarterly_executive_report.pdf
  campaign_performance_summary.pdf
  content_roadmap.pdf
  policy_guidelines.pdf
  audience_behavior_report.pdf
```

Generate PDFs:
```bash
pip install reportlab
python generate_pdfs.py
```

### 3. Run with Docker

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

Data is ingested automatically on startup.

---

### Run without Docker (development)

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm start
```

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/ingest` | Reload CSVs + re-chunk PDFs |
| POST | `/chat` | Main AI chat endpoint |
| GET | `/analytics` | Pre-built dashboard data |
| POST | `/query/sql` | Direct SQL query |
| POST | `/query/docs` | Direct document search |
| POST | `/query/csv` | Direct CSV analysis |
| GET | `/history` | Past queries + tool traces |
| GET | `/health` | Health check |

---

## Demo Questions

The system is built to answer these out of the box:

| # | Question | Tools Used |
|---|----------|------------|
| 1 | Which titles performed best in 2025? | SQL |
| 2 | Why is Stellar Run trending? | SQL + PDF |
| 3 | Compare Dark Orbit vs Last Kingdom | SQL |
| 4 | Which city had strongest engagement last month? | SQL + CSV |
| 5 | What explains weak comedy performance? | SQL + PDF + CSV |
| 6 | What recommendations for leadership next quarter? | SQL + PDF |

---

## Security Design

**SQL injection prevention**
Only SELECT statements are accepted. A keyword blocklist (`insert`, `update`,
`delete`, `drop`, etc.) runs before execution. SQLite connection opens with
`PRAGMA query_only = ON` as a second lock. All table references are checked
against an approved allowlist.

**No raw file system access**
The CSV tool accepts a logical name (`regional_performance`) not a file path.
The PDF tool reads from pre-processed chunks only — no live file access during
queries.

**API key management**
Keys live in `.env` only. Never logged, never returned in API responses,
never committed to version control.

**Input validation**
All endpoints use Pydantic models with length limits. The chat endpoint has a
1000-character message cap. SQL queries are capped at 2000 characters.

**Rate limiting**
20 requests per 60 seconds per IP on all endpoints. Implemented as a FastAPI
dependency — applied consistently across all routes via `Depends(rate_limit)`.

**No sensitive data in logs**
The request logger records only method, path, status code, and duration.
Query content is logged at INFO level without user PII or API keys.

---

## Assumptions & Tradeoffs

**SQLite over PostgreSQL**
Chosen for zero-dependency local setup. The connection layer is abstracted
in `ingestion.py` — swapping to PostgreSQL requires changing one connection
string and the schema's virtual column syntax.

**TF-IDF over vector embeddings**
5 business PDFs with specific film names and numbers, keyword overlap
scoring works well and requires no external API or vector DB. The pdf_tool
is self-contained and swappable  and replacing `_tfidf_score` with
`sentence-transformers` is a single function change.

**In-memory rate limiting**
Simple and dependency-free. The rate limiter is isolated in
`api/utils.py` for exactly this reason.

**Grok over OpenAI/Anthropic**
Firstly the cost factor and 
Secondly,
Grok exposes an OpenAI-compatible API, so the orchestrator uses the `openai`
SDK pointed at `api.groq.com`. Also switching providers means changing the `base_url`,
`api_key`, and `MODEL` constant in `ai_orchestrator.py` which is pretty easy.

**Single DB file**
Both analytics data and query history live in `cineverse.db`. In production
these would be separate — analytics in a read-replica, history in a
write-optimized store.
