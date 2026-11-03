from typing import Any


class AppError(Exception):
    """Base class for all application domain errors.

    Carries a machine-readable `code`, a human-readable `message`, an HTTP
    status code, and optional structured `details`. Does not import FastAPI;
    the handler layer translates these into HTTP responses.
    """

    code: str = "internal_error"
    status_code: int = 500
    message: str = "An unexpected error occurred"

    def __init__(
        self,
        message: str | None = None,
        *,
        details: Any = None,
    ) -> None:
        self.message = message or self.__class__.message
        self.details = details
        super().__init__(self.message)


class NotFoundError(AppError):
    code = "not_found"
    status_code = 404
    message = "Resource not found"


class ConflictError(AppError):
    code = "conflict"
    status_code = 409
    message = "Resource conflict"


class ValidationError(AppError):
    code = "validation_error"
    status_code = 422
    message = "Validation failed"


class UnauthorizedError(AppError):
    code = "unauthorized"
    status_code = 401
    message = "Authentication required"


class ForbiddenError(AppError):
    code = "forbidden"
    status_code = 403
    message = "Permission denied"


class RateLimitError(AppError):
    code = "rate_limited"
    status_code = 429
    message = "Too many requests"
