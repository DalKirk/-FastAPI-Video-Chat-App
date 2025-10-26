"""
Tests for the improved RateLimitMiddleware
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from fastapi import FastAPI
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
    
    # Data endpoint has limit of 5 (should use separate counter)
    for i in range(5):
        response = client.get("/api/data")
        assert response.status_code == 200
    
    response = client.get("/api/data")
    assert response.status_code == 429  # 6th request fails


def test_wildcard_patterns():
    """Test wildcard pattern matching for endpoint configuration"""
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
    
    # Both auth endpoints get the same limit configuration (3 requests)
    # but maintain separate counters per endpoint
    
    # Login endpoint should have 3 request limit
    for i in range(3):
        response = client.get("/api/auth/login")
        assert response.status_code == 200
    response = client.get("/api/auth/login")
    assert response.status_code == 429  # 4th request fails
    
    # Register endpoint also has 3 request limit (separate counter)
    for i in range(3):
        response = client.get("/api/auth/register")
        assert response.status_code == 200
    response = client.get("/api/auth/register")
    assert response.status_code == 429  # 4th request fails
    
    # Non-auth endpoint should have default limit (100)
    response = client.get("/api/other")
    assert response.status_code == 200
    assert response.headers["X-RateLimit-Limit"] == "100"


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
    client.get("/test")
    client.get("/test")
    
    # 3rd request should be rate limited
    response = client.get("/test")
    assert response.status_code == 429
    
    retry_after = int(response.headers["Retry-After"])
    assert retry_after <= 5  # Should be within the window
    assert retry_after > 0  # Should be positive


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
