"""
Rate limiting middleware for API protection
"""
import time
from collections import defaultdict
from typing import Callable
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
        exclude_paths: set = None
    ):
        super().__init__(app)
        self.requests_limit = requests_limit
        self.time_window = time_window
        self.exclude_paths = exclude_paths or {"/health", "/", "/docs", "/openapi.json"}
        
        # Store: {client_ip: [(timestamp1, timestamp2, ...)]}
        self.request_history: dict = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Clean old requests outside the time window
        current_time = time.time()
        cutoff_time = current_time - self.time_window
        self.request_history[client_ip] = [
            timestamp for timestamp in self.request_history[client_ip]
            if timestamp > cutoff_time
        ]
        
        # Check if limit exceeded
        if len(self.request_history[client_ip]) >= self.requests_limit:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded. Maximum {self.requests_limit} requests per {self.time_window} seconds."
                },
                headers={
                    "Retry-After": str(self.time_window),
                    "X-RateLimit-Limit": str(self.requests_limit),
                    "X-RateLimit-Remaining": "0",
                }
            )
        
        # Add current request
        self.request_history[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.requests_limit - len(self.request_history[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.requests_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
