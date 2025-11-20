from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent abuse"""

    def __init__(self, app, calls: int = 60, period: int = 60):
        super().__init__(app)
        self.calls = calls  # Number of calls allowed
        self.period = period  # Time period in seconds
        self.clients = defaultdict(list)
        self.cleanup_task = None

    async def dispatch(self, request: Request, call_next: Callable):
        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)

        # Get client identifier (IP address)
        client_ip = request.client.host

        # Clean up old entries periodically
        await self.cleanup_old_entries()

        # Check rate limit
        now = datetime.now()
        request_times = self.clients[client_ip]

        # Remove requests older than the time window
        request_times = [
            req_time for req_time in request_times
            if now - req_time < timedelta(seconds=self.period)
        ]
        self.clients[client_ip] = request_times

        # Check if limit exceeded
        if len(request_times) >= self.calls:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded. Max {self.calls} requests per {self.period} seconds."
                },
                headers={
                    "Retry-After": str(self.period),
                    "X-RateLimit-Limit": str(self.calls),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int((request_times[0] + timedelta(seconds=self.period)).timestamp()))
                }
            )

        # Add current request
        request_times.append(now)
        self.clients[client_ip] = request_times

        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(self.calls - len(request_times))

        return response

    async def cleanup_old_entries(self):
        """Clean up old entries to prevent memory bloat"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.period * 2)

        for client_ip in list(self.clients.keys()):
            request_times = self.clients[client_ip]
            self.clients[client_ip] = [
                req_time for req_time in request_times
                if req_time > cutoff
            ]
            # Remove client if no recent requests
            if not self.clients[client_ip]:
                del self.clients[client_ip]


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Middleware to track request timing"""

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware"""

    async def dispatch(self, request: Request, call_next: Callable):
        try:
            response = await call_next(request)
            return response
        except HTTPException as exc:
            # Let HTTPExceptions pass through
            raise exc
        except Exception as exc:
            # Log the error (in production, use proper logging)
            print(f"Unhandled error: {exc}")

            # Return generic error response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "An internal server error occurred. Please try again later."
                }
            )


class CORSCustomMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware with security headers"""

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
