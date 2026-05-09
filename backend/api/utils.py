"""
Shared FastAPI dependencies — injected into routes via Depends().
Rate limiter lives here and nowhere else.
"""

import time
import logging
from collections import defaultdict
from fastapi import Request, HTTPException

from backend.api.core.config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW

log = logging.getLogger(__name__)

_rate_store: dict[str, list[float]] = defaultdict(list)


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    return forwarded.split(",")[0].strip() if forwarded else request.client.host


def rate_limit(request: Request) -> None:
    """
    FastAPI dependency — inject into any route that needs rate limiting.
    Usage: router.get("/endpoint", dependencies=[Depends(rate_limit)])
    """
    ip  = get_client_ip(request)
    now = time.time()

    _rate_store[ip] = [
        t for t in _rate_store[ip]
        if now - t < RATE_LIMIT_WINDOW
    ]

    if len(_rate_store[ip]) >= RATE_LIMIT_REQUESTS:
        log.warning("[rate_limit] IP %s exceeded limit", ip)
        raise HTTPException(
            status_code=429,
            detail=(
                f"Rate limit exceeded. "
                f"Max {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW}s."
            ),
        )

    _rate_store[ip].append(now)