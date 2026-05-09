"""GET /history — past queries and tool traces."""

import logging
from fastapi import APIRouter, HTTPException, Depends
from backend.api.utils import rate_limit
from backend.db.history import get_history

log = logging.getLogger(__name__)
router = APIRouter()


@router.get("/history", tags=["History"])
async def history(limit: int = 20, _=Depends(rate_limit)):
    """Returns past chat queries with sources and tool traces."""
    try:
        rows = get_history(limit=min(limit, 50))
        return {"history": rows, "count": len(rows)}
    except Exception as e:
        log.error("History error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))