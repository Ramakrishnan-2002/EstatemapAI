from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.context import get_request_id
from app.core.exceptions import AppException
from app.core.logging import logger


def _get_request_id(request: Request) -> str:
    """Safely extract request ID from context or request state."""
    ctx_id = get_request_id()
    if ctx_id:
        return ctx_id
    return getattr(request.state, "request_id", "unknown")


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    request_id = _get_request_id(request)
    logger.warning(
        "Application exception [%s]: %s | request_id=%s path=%s",
        exc.code,
        exc.message,
        request_id,
        request.url.path,
    )
    headers = {"X-Request-ID": request_id}
    if getattr(exc, "retry_after", None) is not None:
        headers["Retry-After"] = str(exc.retry_after)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "request_id": request_id,
            }
        },
        headers=headers,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    request_id = _get_request_id(request)
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
    }
    code = code_map.get(exc.status_code, "HTTP_ERROR")

    # If detail is already a dict, use it
    message = str(exc.detail) if exc.detail else "An HTTP error occurred."
    details: Any = None
    if isinstance(exc.detail, dict):
        message = exc.detail.get("message", message)
        details = exc.detail.get("details", None)
        code = exc.detail.get("code", code)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": request_id,
            }
        },
        headers={"X-Request-ID": request_id},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    request_id = _get_request_id(request)
    formatted_errors = []
    for err in exc.errors():
        field_loc = " -> ".join(str(loc) for loc in err.get("loc", []))
        formatted_errors.append(
            {
                "field": field_loc,
                "message": err.get("msg", ""),
                "type": err.get("type", ""),
            }
        )

    logger.info(
        "Request validation error | request_id=%s path=%s errors=%d",
        request_id,
        request.url.path,
        len(formatted_errors),
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameters or payload.",
                "details": formatted_errors,
                "request_id": request_id,
            }
        },
        headers={"X-Request-ID": request_id},
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    request_id = _get_request_id(request)
    logger.exception(
        "Database error encountered | request_id=%s path=%s: %s",
        request_id,
        request.url.path,
        str(exc),
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "DATABASE_ERROR",
                "message": "A database error occurred while processing the request.",
                "details": None,
                "request_id": request_id,
            }
        },
        headers={"X-Request-ID": request_id},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = _get_request_id(request)
    logger.exception(
        "Unhandled internal error | request_id=%s path=%s: %s",
        request_id,
        request.url.path,
        str(exc),
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Please try again later.",
                "details": None,
                "request_id": request_id,
            }
        },
        headers={"X-Request-ID": request_id},
    )
