"""
CineVerse — FastAPI app factory.
This file only does three things:
  1. Creates the app
  2. Registers middleware
  3. Mounts routers
thats it. All the real logic lives in the services/ and api/routes/ modules.
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.api.core.config import ALLOWED_ORIGINS
from backend.services.ingestion import ingest_all

from backend.api.routes import chat, ingest, analytics, query, hist

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("CineVerse starting — running ingestion...")
    try:
        ingest_all()
        log.info("Ingestion complete ✓")
    except Exception as e:
        log.error("Ingestion failed on startup: %s", e)
    yield
    log.info("CineVerse shutting down.")


app = FastAPI(
    title="CineVerse Analytics API",
    version="1.0.0",
    description="Secure AI-powered analytics assistant for CineVerse Entertainment.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start    = time.time()
    response = await call_next(request)
    ms       = int((time.time() - start) * 1000)
    log.info("%s %s → %d (%dms)",
             request.method, request.url.path, response.status_code, ms)
    return response

# Mount routers
app.include_router(ingest.router)
app.include_router(chat.router)
app.include_router(analytics.router)
app.include_router(query.router)
app.include_router(hist.router)

@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "service": "cineverse-api"}