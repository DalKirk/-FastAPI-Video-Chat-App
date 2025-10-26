"""
Tests for the improved RateLimitMiddleware
"""
import asyncio
import time
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from middleware.rate_limit import RateLimitMiddleware, RateLimitConfig


def test_basic_rate_limiting():
    """Test basic rate limiting functionality"""
    app = FastAPI()
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}
    
    app.add_middleware(
        RateLimitMiddleware,
        requests_limit=5,
        time_window=60,
        exclude_paths=set(),
    )
    
    client = TestClient(app)
    
    # Make 5 requests - should all succeed
    for i in range(5):
        response = client.get("/test")
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert response.headers["X-RateLimit-Limit"] == "5"
    
    # 6th request should fail
    response = client.get("/test")
    assert response.status_code == 429
    assert "Retry-After" in response.headers
    assert response.headers["X-RateLimit-Remaining"] == "0"
    print("? Basic rate limiting works")


def test_per_endpoint_limits():
    """Test per-endpoint rate limiting"""
    app = FastAPI()
    
    @app.get("/api/auth/login")
    async def login():
        return {"message": "login"}
    
    @app.get("/api/data")
    async def data():
        return {"message": "data"}
    
    per_endpoint_limits = {
        "/api/auth/login": RateLimitConfig(requests_limit=2, time_window=60),
        "/api/data": RateLimitConfig(requests_limit=5, time_window=60),
    }
    
    app.add_middleware(
        RateLimitMiddleware,
        requests_limit=10,
        time_window=60,
        per_endpoint_limits=per_endpoint_limits,
        exclude_paths=set(),
    )
    
    client = TestClient(app)
    
    # Login endpoint has limit of 2
    response = client.get("/api/auth/login")
    assert response.status_code == 200
    response = client.get("/api/auth/login")
    assert response.status_code == 200
    response = client.get("/api/auth/login")
    assert response.status_code == 429  # 3rd request fails
    
    # Data endpoint has limit of 5 (and shares different counter)
    for i in range(5):
        response = client.get("/api/data")
        assert response.status_code == 200
    
    response = client.get("/api/data")
    assert response.status_code == 429  # 6th request fails
    
    print("? Per-endpoint rate limiting works")


def test_wildcard_patterns():
    """Test wildcard pattern matching for endpoints"""
    app = FastAPI()
    
    @app.get("/api/auth/login")
    async def login():
        return {"message": "login"}
    
    @app.get("/api/auth/register")
    async def register():
        return {"message": "register"}
    
    @app.get("/api/other")
    async def other():
        return {"message": "other"}
    
    per_endpoint_limits = {
        "/api/auth/*": RateLimitConfig(requests_limit=3, time_window=60),
    }
    
    app.add_middleware(
        RateLimitMiddleware,
        requests_limit=100,
        time_window=60,
        per_endpoint_limits=per_endpoint_limits,
        exclude_paths=set(),
    )
    
    client = TestClient(app)
    
    # Both auth endpoints should share the limit
    response = client.get("/api/auth/login")
    assert response.status_code == 200
    response = client.get("/api/auth/register")
    assert response.status_code == 200
    response = client.get("/api/auth/login")
    assert response.status_code == 200
    
    # 4th auth request should fail
    response = client.get("/api/auth/register")
    assert response.status_code == 429
    
    # Non-auth endpoint should have default limit
    response = client.get("/api/other")
    assert response.status_code == 200
    
    print("? Wildcard pattern matching works")


def test_rate_limit_headers():
    """Test that rate limit headers are properly set"""
    app = FastAPI()
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}
    
    app.add_middleware(
        RateLimitMiddleware,
        requests_limit=10,
        time_window=60,
        exclude_paths=set(),
    )
    
    client = TestClient(app)
    
    response = client.get("/test")
    assert response.status_code == 200
    
    # Check all headers are present
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers
    assert "X-RateLimit-Window" in response.headers
    
    assert response.headers["X-RateLimit-Limit"] == "10"
    assert response.headers["X-RateLimit-Window"] == "60"
    
    # Remaining should decrease
    remaining = int(response.headers["X-RateLimit-Remaining"])
    response = client.get("/test")
    new_remaining = int(response.headers["X-RateLimit-Remaining"])
    assert new_remaining == remaining - 1
    
    print("? Rate limit headers are correct")


def test_excluded_paths():
    """Test that excluded paths bypass rate limiting"""
    app = FastAPI()
    
    @app.get("/health")
    async def health():
        return {"status": "ok"}
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}
    
    app.add_middleware(
        RateLimitMiddleware,
        requests_limit=2,
        time_window=60,
        exclude_paths={"/health"},
    )
    
    client = TestClient(app)
    
    # Health endpoint should never be rate limited
    for i in range(10):
        response = client.get("/health")
        assert response.status_code == 200
        assert "X-RateLimit-Limit" not in response.headers
    
    # Test endpoint should be rate limited
    response = client.get("/test")
    assert response.status_code == 200
    response = client.get("/test")
    assert response.status_code == 200
    response = client.get("/test")
    assert response.status_code == 429
    
    print("? Excluded paths work correctly")


def test_retry_after_accuracy():
    """Test that Retry-After header is accurate"""
    app = FastAPI()
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}
    
    app.add_middleware(
        RateLimitMiddleware,
        requests_limit=2,
        time_window=5,  # Short window for testing
        exclude_paths=set(),
    )
    
    client = TestClient(app)
    
    # Make 2 requests
    start_time = time.time()
    client.get("/test")
    client.get("/test")
    
    # 3rd request should be rate limited
    response = client.get("/test")
    assert response.status_code == 429
    
    retry_after = int(response.headers["Retry-After"])
    assert retry_after <= 5  # Should be within the window
    assert retry_after > 0  # Should be positive
    
    print(f"? Retry-After header is accurate: {retry_after}s")


def test_memory_cleanup():
    """Test that memory cleanup works"""
    app = FastAPI()
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}
    
    middleware = RateLimitMiddleware(
        app=app,
        requests_limit=100,
        time_window=1,  # Short window
        cleanup_interval=1,  # Frequent cleanup
        max_entries=5,
    )
    
    # Simulate requests from different clients
    for i in range(10):
        client_id = f"client_{i}"
        middleware.last_access[client_id] = time.time() - 10  # Old access
        middleware.request_history[client_id].append(time.time() - 10)
    
    # Trigger cleanup
    import asyncio
    asyncio.run(middleware._cleanup_stale_entries(time.time()))
    
    # Should have cleaned up stale entries
    assert len(middleware.request_history) == 0
    assert len(middleware.last_access) == 0
    
    print("? Memory cleanup works")


def test_max_entries_enforcement():
    """Test that max entries limit is enforced"""
    app = FastAPI()
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}
    
    middleware = RateLimitMiddleware(
        app=app,
        requests_limit=100,
        time_window=60,
        max_entries=5,
    )
    
    # Add more entries than max
    current_time = time.time()
    for i in range(10):
        client_id = f"client_{i}"
        middleware.request_history[client_id].append(current_time)
        middleware.last_access[client_id] = current_time
    
    # Enforce max entries
    import asyncio
    asyncio.run(middleware._enforce_max_entries())
    
    # Should have removed oldest entries
    assert len(middleware.request_history) <= 5
    assert len(middleware.last_access) <= 5
    
    print("? Max entries enforcement works")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*50)
    print("Testing Improved RateLimitMiddleware")
    print("="*50 + "\n")
    
    test_basic_rate_limiting()
    test_per_endpoint_limits()
    test_wildcard_patterns()
    test_rate_limit_headers()
    test_excluded_paths()
    test_retry_after_accuracy()
    test_memory_cleanup()
    test_max_entries_enforcement()
    
    print("\n" + "="*50)
    print("All tests passed! ?")
    print("="*50 + "\n")


if __name__ == "__main__":
    run_all_tests()
