# Rate Limit Middleware - Usage Guide

## Overview
The improved `RateLimitMiddleware` provides advanced rate limiting features for your FastAPI application.

## Key Improvements

### 1. **Memory Leak Prevention**
- Automatic cleanup of stale entries every 5 minutes
- Maximum tracked clients limit (default: 10,000)
- Removes oldest entries when limit is exceeded

### 2. **Per-Endpoint Rate Limiting**
```python
from middleware.rate_limit import RateLimitMiddleware, RateLimitConfig

per_endpoint_limits = {
    "/api/auth/login": RateLimitConfig(requests_limit=5, time_window=60),
    "/api/auth/*": RateLimitConfig(requests_limit=10, time_window=60),
    "/api/ai/*": RateLimitConfig(requests_limit=20, time_window=60),
    "/api/*": RateLimitConfig(requests_limit=100, time_window=60),
}

app.add_middleware(
    RateLimitMiddleware,
    per_endpoint_limits=per_endpoint_limits,
)
```

### 3. **Multiple Client Identification Strategies**

**By IP Address (default):**
```python
app.add_middleware(
    RateLimitMiddleware,
    identifier_strategy="ip",
)
```

**By API Key:**
```python
app.add_middleware(
    RateLimitMiddleware,
    identifier_strategy="header:X-API-Key",
    requests_limit=1000,
    time_window=3600,
)
```

**By User ID:**
```python
app.add_middleware(
    RateLimitMiddleware,
    identifier_strategy="header:X-User-ID",
)
```

### 4. **Redis Support** (Optional)
```python
import redis.asyncio as redis

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

app.add_middleware(
    RateLimitMiddleware,
    use_redis=True,
    redis_client=redis_client,
)
```

### 5. **Enhanced Rate Limit Headers**
All responses now include:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in window
- `X-RateLimit-Reset`: Timestamp when limit resets
- `X-RateLimit-Window`: Duration of the rate limit window
- `Retry-After`: Seconds until you can retry (429 responses only)

## Example Configurations

### Basic Usage
```python
from fastapi import FastAPI
from middleware.rate_limit import RateLimitMiddleware

app = FastAPI()

app.add_middleware(
    RateLimitMiddleware,
    requests_limit=100,
    time_window=60,
)
```

### Tiered Rate Limiting
```python
from middleware.rate_limit import create_tiered_rate_limiter

app = FastAPI()
app.add_middleware(create_tiered_rate_limiter)
```

### API Key Based
```python
from middleware.rate_limit import create_api_key_rate_limiter

app = FastAPI()
app.add_middleware(create_api_key_rate_limiter)
```

### Custom Configuration
```python
app.add_middleware(
    RateLimitMiddleware,
    requests_limit=500,
    time_window=300,  # 5 minutes
    exclude_paths={"/health", "/metrics", "/docs"},
    cleanup_interval=600,  # Clean up every 10 minutes
    max_entries=50000,  # Track up to 50k clients
)
```

## Performance Considerations

### In-Memory vs Redis
- **In-Memory**: Fast, but doesn't work across multiple server instances
- **Redis**: Slightly slower, but works across distributed deployments

### Memory Management
- Default max entries: 10,000 clients
- Automatic cleanup every 5 minutes
- LRU-style eviction when max is exceeded

### Lock Contention
- Fine-grained locking only during rate check
- Lock released before processing request
- No lock needed for Redis backend (uses atomic operations)

## Testing Rate Limits

```python
import httpx
import asyncio

async def test_rate_limit():
    async with httpx.AsyncClient() as client:
        # Make 101 requests (assuming limit is 100)
        for i in range(101):
            response = await client.get("http://localhost:8000/api/test")
            print(f"Request {i+1}: {response.status_code}")
            print(f"Remaining: {response.headers.get('X-RateLimit-Remaining')}")
            
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After')
                print(f"Rate limited! Retry after {retry_after} seconds")
                break

asyncio.run(test_rate_limit())
```

## Migration from Old Version

The new middleware is **backward compatible**. Your existing code will work without changes:

```python
# Old usage - still works!
app.add_middleware(
    RateLimitMiddleware,
    requests_limit=100,
    time_window=60,
)
```

## Production Recommendations

1. **Use Redis** for multi-server deployments:
   ```bash
   pip install redis
   ```

2. **Configure per-endpoint limits** for sensitive endpoints:
   - Authentication: 5-10 req/min
   - AI/Heavy operations: 20-30 req/min
   - General API: 100-200 req/min

3. **Monitor rate limit headers** to understand usage patterns

4. **Set appropriate max_entries** based on your user base:
   - Small app: 10,000 (default)
   - Medium app: 50,000
   - Large app: Use Redis

5. **Adjust cleanup_interval** based on memory constraints:
   - More memory: 600 seconds (10 min)
   - Less memory: 180 seconds (3 min)

## Troubleshooting

### High Memory Usage
- Reduce `max_entries`
- Reduce `cleanup_interval`
- Switch to Redis backend

### Rate Limits Not Working Across Servers
- Enable Redis backend
- Ensure all servers use same Redis instance

### False Positives Behind Load Balancer
- Change identifier strategy to use custom header:
  ```python
  identifier_strategy="header:X-Forwarded-For"
  ```

## Security Notes

- Rate limiting is per-identifier, not global
- Excluded paths bypass rate limiting completely
- Consider using WAF/CDN rate limiting for DDoS protection
- Monitor for distributed attacks across many IPs
