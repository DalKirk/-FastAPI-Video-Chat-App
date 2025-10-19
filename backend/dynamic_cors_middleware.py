"""
Dynamic CORS Middleware for FastAPI
Handles CORS with whitelist validation and proper preflight support
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class DynamicCORSMiddleware(BaseHTTPMiddleware):
    """
    CORS middleware that validates origins against a whitelist.
    Properly handles preflight OPTIONS requests and adds CORS headers.
    """
    
    def __init__(self, app, whitelist: set):
        super().__init__(app)
        self.whitelist = whitelist
    
    async def dispatch(self, request, call_next):
        origin = request.headers.get("origin")
        
        # Handle preflight OPTIONS requests
        if request.method == "OPTIONS":
            if origin in self.whitelist:
                return Response(
                    status_code=200,
                    headers={
                        "Access-Control-Allow-Origin": origin,
                        "Access-Control-Allow-Credentials": "true",
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization",
                        "Access-Control-Max-Age": "600",
                    }
                )
            return Response(status_code=403)
        
        # Process the actual request
        response = await call_next(request)
        
        # Add CORS headers if origin is whitelisted
        if origin in self.whitelist:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        
        return response