"""GET /analytics — pre-built dashboard summary queries."""

import logging
from fastapi import APIRouter, HTTPException, Depends
from backend.api.utils import rate_limit
from backend.tools.sql_tool import query_database

log = logging.getLogger(__name__)
router = APIRouter()


def _run(sql: str) -> list[dict]:
    """Run a query and return rows, raising on failure."""
    result = query_database(sql)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return result["rows"]


@router.get("/analytics", tags=["Analytics"])
async def analytics(_=Depends(rate_limit)):
    """
    Pre-built analytics for the frontend dashboard.
    Runs 4 fixed queries — no AI involved, fast and predictable.
    """
    try:
        return {
            "top_movies": _run(
                "SELECT title, genre, revenue_inr, imdb_rating, avg_completion_pct "
                "FROM vw_movie_performance "
                "ORDER BY revenue_inr DESC LIMIT 5"
            ),
            "genre_summary": _run(
                "SELECT genre, total_titles, avg_rating, avg_completion_pct, "
                "avg_marketing_roi, total_revenue_inr "
                "FROM vw_genre_summary "
                "ORDER BY total_revenue_inr DESC"
            ),
            "city_engagement": _run(
                "SELECT city, region, MAX(engagement_score) as peak_engagement, "
                "SUM(views) as total_views "
                "FROM vw_city_engagement "
                "GROUP BY city "
                "ORDER BY peak_engagement DESC LIMIT 8"
            ),
            "releases_2025": _run(
                "SELECT title, genre, revenue_inr, imdb_rating, avg_completion_pct, roi "
                "FROM vw_movie_performance "
                "WHERE release_year = 2025 "
                "ORDER BY revenue_inr DESC"
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error("Analytics error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))