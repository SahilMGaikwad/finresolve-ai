"""
FinResolve AI — Rate Limiting Service

Provides sliding-window in-memory rate limiting with Redis-ready interface.
Protects sensitive and computationally heavy endpoints against DoS.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable

from fastapi import HTTPException, Request, status


class SlidingWindowRateLimiter:
    """
    In-memory sliding window rate limiter.
    In production, this interface connects to Redis or API Gateway token buckets.
    """

    def __init__(self, requests_per_minute: int = 120, burst: int = 30):
        self.limit = requests_per_minute
        self.burst = burst
        self.window_seconds = 60.0
        # Maps client_key -> list of timestamp floats
        self._history: dict[str, list[float]] = defaultdict(list)

    def is_rate_limited(self, key: str) -> tuple[bool, int]:
        """
        Check if key has exceeded its quota.

        Returns:
            (is_limited: bool, retry_after_seconds: int)
        """
        now = time.monotonic()
        cutoff = now - self.window_seconds
        
        # Clean expired timestamps
        timestamps = [t for t in self._history[key] if t > cutoff]
        self._history[key] = timestamps

        if len(timestamps) >= self.limit:
            oldest = timestamps[0]
            retry_after = int(max(1.0, self.window_seconds - (now - oldest)))
            return True, retry_after

        # Record this request
        self._history[key].append(now)
        return False, 0

    def reset(self) -> None:
        """Reset rate limiter state (useful in tests)."""
        self._history.clear()


# Default rate limiter instance
_global_rate_limiter = SlidingWindowRateLimiter(requests_per_minute=120)


def rate_limit(requests_per_minute: int = 120) -> Callable[[Request], None]:
    """FastAPI dependency to rate limit endpoints based on client IP or user."""
    limiter = SlidingWindowRateLimiter(requests_per_minute=requests_per_minute)

    def dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        user_key = request.headers.get("Authorization") or client_ip

        is_limited, retry_after = limiter.is_rate_limited(user_key)
        if is_limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too Many Requests: Rate limit exceeded. Please retry later.",
                headers={"Retry-After": str(retry_after)},
            )

    return dependency
