"""
Rate limiting middleware for API protection with advanced features
"""
import time
import asyncio
from collections import defaultdict, deque
from typing import Callable, Deque, Dict, Optional, Set, Tuple
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import re


class RateLimitConfig:
    """Configuration for rate limiting rules"""
    
    def __init__(
        self,
        requests_limit: int = 100,
        time_window: int = 60,
        identifier: str = "ip",  # "ip", "header:<name>", or "path"
    ):
        self.requests_limit = requests_limit
        self.time_window = time_window
        self.identifier = identifier


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Advanced in-memory rate limiting middleware with multiple features:
    - Per-endpoint rate limiting
    - Multiple client identification methods
    - Automatic memory cleanup
    - Detailed rate limit headers
    - Optional Redis support (when available)
    
    For production with multiple servers, use Redis backend.
    """

    def __init__(
        self,
        app: ASGIApp,
        requests_limit: int = 100,
        time_window: int = 60,  # seconds
        exclude_paths: Optional[Set[str]] = None,
        per_endpoint_limits: Optional[Dict[str, RateLimitConfig]] = None,
        identifier_strategy: str = "ip",  # "ip", "header:X-API-Key", "header:X-User-ID"
        cleanup_interval: int = 300,  # Clean up stale entries every 5 minutes
        max_entries: int = 10000,  # Maximum number of tracked clients
        use_redis: bool = False,
        redis_client = None,
    ):
        super().__init__(app)
        self.default_limit = requests_limit
        self.default_window = time_window
        self.exclude_paths = exclude_paths or {"/health", "/", "/docs", "/openapi.json", "/redoc"}
        self.per_endpoint_limits = per_endpoint_limits or {}
        self.identifier_strategy = identifier_strategy
        self.cleanup_interval = cleanup_interval
        self.max_entries = max_entries
        self.use_redis = use_redis
        self.redis_client = redis_client

        # Store: {client_identifier: deque[timestamp, ...]}
        self.request_history: Dict[str, Deque[float]] = defaultdict(deque)
        # Track last access time for cleanup
        self.last_access: Dict[str, float] = {}
        # Global lock to protect request_history against concurrent access
        self._lock = asyncio.Lock()
        # Last cleanup time
        self._last_cleanup = time.time()

    def _get_client_identifier(self, request: Request) -> str:
        """Extract client identifier based on configured strategy"""
        if self.identifier_strategy == "ip":
            return request.client.host if request.client else "unknown"
        
        if self.identifier_strategy.startswith("header:"):
            header_name = self.identifier_strategy.split(":", 1)[1]
            return request.headers.get(header_name, f"no-{header_name}")
        
        # Default to IP
        return request.client.host if request.client else "unknown"

    def _get_rate_limit_config(self, path: str) -> Tuple[int, int]:
        """Get rate limit configuration for a specific path"""
        # Check for exact match
        if path in self.per_endpoint_limits:
            config = self.per_endpoint_limits[path]
            return config.requests_limit, config.time_window
        
        # Check for pattern match
        for pattern, config in self.per_endpoint_limits.items():
            if "*" in pattern or "?" in pattern:
                regex_pattern = pattern.replace("*", ".*").replace("?", ".")
                if re.match(f"^{regex_pattern}$", path):
                    return config.requests_limit, config.time_window
        
        # Return default
        return self.default_limit, self.default_window

    async def _cleanup_stale_entries(self, current_time: float):
        """Remove entries that haven't been accessed recently"""
        if current_time - self._last_cleanup < self.cleanup_interval:
            return
        
        self._last_cleanup = current_time
        stale_threshold = current_time - (self.default_window * 2)  # 2x window
        
        # Find stale entries
        stale_keys = [
            key for key, last_time in self.last_access.items()
            if last_time < stale_threshold
        ]
        
        # Remove them
        for key in stale_keys:
            self.request_history.pop(key, None)
            self.last_access.pop(key, None)

    async def _enforce_max_entries(self):
        """Ensure we don't exceed maximum tracked entries"""
        if len(self.request_history) > self.max_entries:
            # Remove oldest 10% of entries
            remove_count = self.max_entries // 10
            sorted_by_access = sorted(self.last_access.items(), key=lambda x: x[1])
            for key, _ in sorted_by_access[:remove_count]:
                self.request_history.pop(key, None)
                self.last_access.pop(key, None)

    async def _check_rate_limit_redis(
        self, 
        client_id: str, 
        requests_limit: int, 
        time_window: int,
        endpoint: str = "",
    ) -> Tuple[bool, int, int]:
        """Check rate limit using Redis backend"""
        if not self.redis_client:
            return await self._check_rate_limit_memory(client_id, requests_limit, time_window, endpoint)
        
        try:
            current_time = int(time.time())
            # Include endpoint in key for per-endpoint limits
            key = f"rate_limit:{client_id}:{endpoint}" if endpoint else f"rate_limit:{client_id}"
            
            # Use Redis sorted set with scores as timestamps
            pipe = self.redis_client.pipeline()
            # Remove old entries
            pipe.zremrangebyscore(key, 0, current_time - time_window)
            # Count current entries
            pipe.zcard(key)
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            # Set expiration
            pipe.expire(key, time_window)
            
            results = await pipe.execute() if hasattr(pipe, 'execute') else pipe.execute()
            count = results[1]
            
            if count >= requests_limit:
                # Get oldest timestamp to calculate retry-after
                oldest = await self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest:
                    oldest_time = int(oldest[0][1])
                    retry_after = max(0, time_window - (current_time - oldest_time))
                else:
                    retry_after = time_window
                return False, 0, retry_after
            
            remaining = requests_limit - count - 1
            return True, remaining, 0
            
        except Exception:
            # Fallback to memory-based limiting on Redis errors
            return await self._check_rate_limit_memory(client_id, requests_limit, time_window, endpoint)

    async def _check_rate_limit_memory(
        self, 
        client_id: str, 
        requests_limit: int, 
        time_window: int,
        endpoint: str = "",
    ) -> Tuple[bool, int, int]:
        """Check rate limit using in-memory storage"""
        current_time = time.time()
        cutoff_time = current_time - time_window
        
        # Create unique key combining client_id and endpoint for per-endpoint limits
        storage_key = f"{client_id}:{endpoint}" if endpoint else client_id

        async with self._lock:
            # Periodic cleanup
            await self._cleanup_stale_entries(current_time)
            await self._enforce_max_entries()
            
            history = self.request_history[storage_key]
            self.last_access[storage_key] = current_time
            
            # Clean old requests outside the time window
            while history and history[0] <= cutoff_time:
                history.popleft()

            if len(history) >= requests_limit:
                # Calculate accurate retry-after based on oldest request in window
                oldest = history[0] if history else current_time
                retry_after = max(0, int(time_window - (current_time - oldest)))
                return False, 0, retry_after

            # Add current request
            history.append(current_time)
            remaining = max(0, requests_limit - len(history))
            
            return True, remaining, 0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Get client identifier
        client_id = self._get_client_identifier(request)
        
        # Get rate limit configuration for this endpoint
        requests_limit, time_window = self._get_rate_limit_config(request.url.path)

        # Check rate limit (Redis or memory)
        if self.use_redis and self.redis_client:
            allowed, remaining, retry_after = await self._check_rate_limit_redis(
                client_id, requests_limit, time_window, request.url.path
            )
        else:
            allowed, remaining, retry_after = await self._check_rate_limit_memory(
                client_id, requests_limit, time_window, request.url.path
            )

        if not allowed:
            current_time = int(time.time())
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded. Maximum {requests_limit} requests per {time_window} seconds.",
                    "retry_after": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(requests_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(current_time + retry_after),
                    "X-RateLimit-Window": str(time_window),
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to successful responses
        current_time = int(time.time())
        response.headers["X-RateLimit-Limit"] = str(requests_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(current_time + time_window)
        response.headers["X-RateLimit-Window"] = str(time_window)

        return response


# Example usage configurations
def create_tiered_rate_limiter(app: ASGIApp) -> RateLimitMiddleware:
    """
    Example: Create a rate limiter with different limits per endpoint
    """
    per_endpoint_limits = {
        "/api/auth/*": RateLimitConfig(requests_limit=10, time_window=60),  # Strict for auth
        "/api/ai/*": RateLimitConfig(requests_limit=20, time_window=60),  # AI endpoints
        "/api/*": RateLimitConfig(requests_limit=100, time_window=60),  # General API
    }
    
    return RateLimitMiddleware(
        app=app,
        requests_limit=200,  # Default for non-matched paths
        time_window=60,
        per_endpoint_limits=per_endpoint_limits,
        identifier_strategy="ip",
    )


def create_api_key_rate_limiter(app: ASGIApp) -> RateLimitMiddleware:
    """
    Example: Create a rate limiter that uses API keys instead of IP
    """
    return RateLimitMiddleware(
        app=app,
        requests_limit=1000,
        time_window=3600,  # 1000 requests per hour
        identifier_strategy="header:X-API-Key",
    )
