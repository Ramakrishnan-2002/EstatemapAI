from contextvars import ContextVar

# Request-scoped ContextVar to track the correlation / request ID across async tasks and loggers
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """Retrieve the current request ID from ContextVar."""
    return request_id_ctx.get()


def set_request_id(req_id: str) -> None:
    """Set the current request ID in ContextVar."""
    request_id_ctx.set(req_id)
