import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.context import set_request_id
from app.core.exceptions import AppException
from app.core.logging import logger


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that ensures every incoming HTTP request has a correlation ID.
    - Preserves incoming 'X-Request-ID' header if present.
    - Generates a UUID4 if missing.
    - Stores the ID in contextvars for logging and error reporting.
    - Injects 'X-Request-ID' into response headers.
    - Logs request duration and status.
    - Formats unhandled exceptions into unified JSON error responses.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        incoming_req_id = request.headers.get("X-Request-ID")
        request_id = incoming_req_id if incoming_req_id else str(uuid.uuid4())
        set_request_id(request_id)

        # Store in request state for easy access in handlers
        request.state.request_id = request_id

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
        except AppException as app_exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.warning(
                "AppException handled in middleware [%s]: %s (%.2fms) | request_id=%s",
                app_exc.code,
                app_exc.message,
                duration_ms,
                request_id,
            )
            from app.core.exception_handlers import app_exception_handler

            return await app_exception_handler(request, app_exc)
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.exception(
                "Unhandled exception during request processing | request_id=%s method=%s path=%s duration=%.2fms",
                request_id,
                request.method,
                request.url.path,
                duration_ms,
            )
            from app.core.exception_handlers import unhandled_exception_handler

            return await unhandled_exception_handler(request, exc)

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        response.headers["X-Request-ID"] = request_id

        # Structured log for HTTP access (skip noisy liveness probe)
        if not request.url.path.startswith("/health/live"):
            logger.info(
                "HTTP %s %s -> %d (%.2fms) | request_id=%s",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
                request_id,
            )

        return response
