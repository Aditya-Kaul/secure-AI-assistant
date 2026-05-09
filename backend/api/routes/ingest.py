"""POST /ingest — reload CSVs and PDFs into the system."""

import logging
from fastapi import APIRouter, HTTPException, Depends
from backend.api.utils import rate_limit
from backend.services.ingestion import ingest_all

log = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ingest", tags=["Data"])
async def ingest(_=Depends(rate_limit)):
    """
    Reload all CSVs into SQLite and re-chunk all PDFs.
    Idempotent — safe to call multiple times.
    """
    try:
        result = ingest_all()
        return {"status": "ok", "detail": result}
    except Exception as e:
        log.error("Ingestion error: %s", e)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")