from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error description")
    details: Any = Field(
        default=None, description="Optional extra error context or field-level validation errors"
    )
    request_id: str = Field(..., description="Correlation request ID")


class ErrorResponse(BaseModel):
    error: ErrorDetail
