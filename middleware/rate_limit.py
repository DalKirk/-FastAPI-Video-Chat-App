"""
Rate limiting middleware for API protection
"""
import time
import asyncio
from collections import defaultdict, deque
from typing import Callable, Deque, Dict, Optional, Set
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    For production, use Redis-based rate limiting (e.g., slowapi library).
    """

    def __init__(
        self,
        app: ASGIApp,
        requests_limit: int = 100,
        time_window: int = 60,  # seconds
        exclude_paths: Optional[Set[str]] = None,
    ):
        super().__init__(app)
        self.requests_limit = requests_limit
        self.time_window = time_window
        self.exclude_paths = exclude_paths or {"/health", "/", "/docs", "/openapi.json", "/redoc"}

        # Store: {client_ip: deque[timestamp, ...]}
        self.request_history: Dict[str, Deque[float]] = defaultdict(deque)
        # Global lock to protect request_history against concurrent access
        self._lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        current_time = time.time()
        cutoff_time = current_time - self.time_window

        # Manage counters under a lock, then release before awaiting downstream
        async with self._lock:
            history = self.request_history[client_ip]
            # Clean old requests outside the time window (pop from left for efficiency)
            while history and history[0] <= cutoff_time:
                history.popleft()

            if len(history) >= self.requests_limit:
                # Calculate accurate retry-after based on oldest request in window
                oldest = history[0] if history else current_time
                retry_after = max(0, int(self.time_window - (current_time - oldest)))
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": f"Rate limit exceeded. Maximum {self.requests_limit} requests per {self.time_window} seconds."
                    },
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(self.requests_limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(current_time + retry_after)),
                    },
                )

            # Add current request
            history.append(current_time)
            remaining = max(0, self.requests_limit - len(history))

        # Process request (lock released)
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response
