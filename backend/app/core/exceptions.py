from typing import Any


class AppException(Exception):
    """Base application domain exception."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = 500,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class ResourceNotFoundException(AppException):
    """Raised when a requested entity does not exist."""

    def __init__(
        self,
        resource: str = "Resource",
        identifier: Any = None,
        message: str | None = None,
    ) -> None:
        msg = message or (
            f"{resource} '{identifier}' was not found."
            if identifier
            else f"{resource} was not found."
        )
        super().__init__(
            message=msg,
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"resource": resource, "identifier": identifier}
            if identifier
            else {"resource": resource},
        )


EntityNotFoundException = ResourceNotFoundException


class AuthenticationException(AppException):
    """Raised on failed authentication (invalid credentials, expired token)."""

    def __init__(self, message: str = "Could not validate credentials.") -> None:
        super().__init__(
            message=message,
            code="AUTHENTICATION_FAILED",
            status_code=401,
        )


class AuthorizationException(AppException):
    """Raised when the user lacks required permissions."""

    def __init__(self, message: str = "You do not have permission to perform this action.") -> None:
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403,
        )


class ValidationException(AppException):
    """Raised when domain-level validation fails."""

    def __init__(self, message: str = "Validation failed.", details: Any = None) -> None:
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class ExternalServiceException(AppException):
    """Raised when a third-party service (e.g. Gemini, Ollama, Routing API) fails."""

    def __init__(self, service_name: str, message: str = "External service unavailable.") -> None:
        super().__init__(
            message=f"[{service_name}] {message}",
            code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details={"service": service_name},
        )


class DatabaseException(AppException):
    """Raised when a database error occurs."""

    def __init__(self, message: str = "A database error occurred.", details: Any = None) -> None:
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=500,
            details=details,
        )


class RateLimitExceededException(AppException):
    """Raised when rate limit is exceeded on an endpoint or resource."""

    def __init__(
        self,
        message: str = "Too many requests. Please try again shortly.",
        retry_after: int | None = None,
        details: Any = None,
    ) -> None:
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details or ({"retry_after_seconds": retry_after} if retry_after else None),
        )
        self.retry_after = retry_after


class AIDisabledException(AppException):
    """Raised when an AI endpoint is called while AI functionality is globally disabled."""

    def __init__(self, message: str = "AI features are currently disabled.") -> None:
        super().__init__(
            message=message,
            code="AI_DISABLED",
            status_code=503,
        )


class AIProviderUnavailableException(AppException):
    """Raised when the configured AI provider (e.g. Ollama daemon) cannot be reached."""

    def __init__(
        self,
        provider: str = "ollama",
        message: str = "AI service provider is currently unreachable.",
        details: Any = None,
    ) -> None:
        super().__init__(
            message=message,
            code="AI_PROVIDER_UNAVAILABLE",
            status_code=503,
            details=details or {"provider": provider},
        )


class AIProviderTimeoutException(AppException):
    """Raised when the AI provider times out during generation."""

    def __init__(
        self,
        provider: str = "ollama",
        timeout_seconds: float = 30.0,
        message: str = "AI service request timed out.",
    ) -> None:
        super().__init__(
            message=message,
            code="AI_PROVIDER_TIMEOUT",
            status_code=504,
            details={"provider": provider, "timeout_seconds": timeout_seconds},
        )


class AIModelNotAvailableException(AppException):
    """Raised when the requested AI model is not downloaded or available on the provider."""

    def __init__(
        self,
        model: str = "llama3.2:3b",
        provider: str = "ollama",
        message: str = "Configured AI model is not installed or available on provider.",
    ) -> None:
        super().__init__(
            message=message,
            code="AI_MODEL_NOT_AVAILABLE",
            status_code=503,
            details={"model": model, "provider": provider},
        )


class AIInvalidResponseException(AppException):
    """Raised when the AI model returns malformed JSON or unparseable text."""

    def __init__(
        self,
        message: str = "AI provider returned an invalid or unparseable response.",
        details: Any = None,
    ) -> None:
        super().__init__(
            message=message,
            code="AI_INVALID_RESPONSE",
            status_code=502,
            details=details,
        )


class AIOutputValidationException(AppException):
    """Raised when AI structured output fails Pydantic schema validation."""

    def __init__(
        self,
        message: str = "AI-generated structured output failed domain validation.",
        details: Any = None,
    ) -> None:
        super().__init__(
            message=message,
            code="AI_OUTPUT_VALIDATION_FAILED",
            status_code=422,
            details=details,
        )


class AIProviderRateLimitedException(AppException):
    """Raised when an upstream hosted AI provider (e.g. Gemini) returns a 429 rate limit error."""

    def __init__(
        self,
        provider: str = "gemini",
        message: str = "Upstream AI provider rate limit exceeded. Please retry shortly.",
        details: Any = None,
    ) -> None:
        super().__init__(
            message=message,
            code="AI_PROVIDER_RATE_LIMITED",
            status_code=429,
            details=details or {"provider": provider},
        )


class AIProviderAuthFailedException(AppException):
    """Raised when the hosted AI provider API key is missing or invalid."""

    def __init__(
        self,
        provider: str = "gemini",
        message: str = "AI provider authentication failed. Check configured API key.",
        details: Any = None,
    ) -> None:
        super().__init__(
            message=message,
            code="AI_PROVIDER_AUTH_FAILED",
            status_code=502,
            details=details or {"provider": provider},
        )


class AIQuotaExceededException(AppException):
    """Raised when the hosted AI provider quota or credits have been exhausted."""

    def __init__(
        self,
        provider: str = "gemini",
        message: str = "AI provider quota exhausted. Check provider account tier.",
        details: Any = None,
    ) -> None:
        super().__init__(
            message=message,
            code="AI_QUOTA_EXCEEDED",
            status_code=503,
            details=details or {"provider": provider},
        )


class AIProviderConfigurationException(AppException):
    """Raised when an invalid or unsupported AI provider is configured."""

    def __init__(
        self,
        message: str = "Invalid or unsupported AI provider configured.",
        details: Any = None,
    ) -> None:
        super().__init__(
            message=message,
            code="AI_PROVIDER_CONFIGURATION_ERROR",
            status_code=500,
            details=details,
        )
