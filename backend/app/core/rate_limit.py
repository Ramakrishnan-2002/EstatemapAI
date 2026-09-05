import time
import uuid

from fastapi import Request

from app.cache.redis import get_redis
from app.core.config import settings
from app.core.exceptions import RateLimitExceededException
from app.core.logging import logger


class RateLimiter:
    """
    Sliding-window rate limiter using Redis sorted sets.
    Accurately limits request frequency per identity (user_id or client IP)
    without fixed-window border spikes.
    """

    def __init__(
        self,
        requests_limit: int = 100,
        window_seconds: int = 60,
        scope: str = "default",
        fail_open: bool | None = None,
    ) -> None:
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.scope = scope
        self.fail_open = fail_open if fail_open is not None else settings.RATE_LIMIT_FAIL_OPEN

    def _resolve_identity(self, request: Request) -> str:
        """
        Identify caller by authenticated user ID if present, otherwise by client IP.
        """
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"

        # Check authorization header if user_id wasn't on request.state yet
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from app.core.security import decode_access_token

                token = auth_header.split(" ")[1]
                payload = decode_access_token(token)
                sub = payload.get("sub")
                if sub:
                    return f"user:{sub}"
            except Exception:
                pass

        # Fallback to client IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        elif request.client:
            client_ip = request.client.host
        else:
            client_ip = "127.0.0.1"

        return f"ip:{client_ip}"

    async def __call__(self, request: Request) -> None:
        """
        FastAPI dependency evaluation.
        Throws RateLimitExceededException (HTTP 429) if threshold is breached.
        """
        if not settings.RATE_LIMIT_ENABLED:
            return

        identity = self._resolve_identity(request)
        key = f"estatemap:ratelimit:v1:{self.scope}:{identity}"
        now = time.time()
        window_start = now - self.window_seconds
        member_id = f"{now:.6f}_{uuid.uuid4().hex[:6]}"

        try:
            client = await get_redis()
            if client is None:
                if not self.fail_open:
                    raise RateLimitExceededException(
                        message="Rate limit verification unavailable.",
                        retry_after=self.window_seconds,
                    )
                return

            # Pipeline sliding window check and addition
            pipe = client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zrange(key, 0, 0, withscores=True)
            pipe.zadd(key, {member_id: now})
            pipe.expire(key, self.window_seconds + 5)
            results = await pipe.execute()

            # results: [rem_count, current_count_before_add, oldest_items, zadd_count, expire_result]
            current_count = results[1]
            oldest_items = results[2]

            if current_count >= self.requests_limit:
                # Remove the added member since request is rejected
                await client.zrem(key, member_id)

                # Calculate remaining seconds until oldest request expires
                if oldest_items and len(oldest_items) > 0:
                    oldest_ts = float(oldest_items[0][1])
                    retry_after = max(1, int(self.window_seconds - (now - oldest_ts)))
                else:
                    retry_after = self.window_seconds

                logger.warning(
                    "Rate limit exceeded | scope=%s identity=%s count=%d limit=%d retry_after=%ds",
                    self.scope,
                    identity,
                    current_count + 1,
                    self.requests_limit,
                    retry_after,
                )
                raise RateLimitExceededException(
                    message="Too many requests. Please try again shortly.",
                    retry_after=retry_after,
                    details={
                        "scope": self.scope,
                        "limit": self.requests_limit,
                        "window_seconds": self.window_seconds,
                    },
                )
        except RateLimitExceededException:
            raise
        except Exception as e:
            logger.warning("Rate limiter Redis check failed: %s (fail_open=%s)", e, self.fail_open)
            if not self.fail_open:
                raise RateLimitExceededException(
                    message="Rate limiting service unavailable.",
                    retry_after=self.window_seconds,
                ) from e
