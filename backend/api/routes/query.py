"""
POST /query/sql  — direct SQL access
POST /query/docs — direct document search
Both bypass AI — useful for debugging and the frontend filter bar.
"""
from __future__ import annotations
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from backend.api.utils import rate_limit
from backend.tools.sql_tool  import query_database
from backend.tools.pdf_tool  import search_documents
from backend.tools.csv_tool  import analyze_csv

log = logging.getLogger(__name__)
router = APIRouter(prefix="/query")


class SQLRequest(BaseModel):
    sql_query: str = Field(..., min_length=1, max_length=2000)


class DocSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=3, ge=1, le=5)


class CSVRequest(BaseModel):
    file:        str
    filters:     dict       = Field(default_factory=dict)
    aggregation: Optional[str] = None
    column:      Optional[str] = None
    group_by:    Optional[str] = None


@router.post("/sql", tags=["Query"])
async def sql_query(body: SQLRequest, _=Depends(rate_limit)):
    """Direct SQL — same security rules as the AI tool."""
    result = query_database(body.sql_query)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/docs", tags=["Query"])
async def doc_search(body: DocSearchRequest, _=Depends(rate_limit)):
    """Direct document search — returns raw PDF chunks."""
    result = search_documents(query=body.query, top_k=body.top_k)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/csv", tags=["Query"])
async def csv_query(body: CSVRequest, _=Depends(rate_limit)):
    """Direct CSV analysis — bypasses AI."""
    result = analyze_csv(
        file=body.file,
        filters=body.filters,
        aggregation=body.aggregation,
        column=body.column,
        group_by=body.group_by,
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result