import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.exceptions import AppError
from app.schemas.errors import ErrorBody, ErrorResponse

logger = logging.getLogger(__name__)

# Python's logging.LogRecord has these attributes reserved. Passing any of
# these as keys in `extra={...}` raises KeyError("Attempt to overwrite ...").
# Never use these names in `extra`.
_RESERVED_LOG_KEYS: frozenset[str] = frozenset(
    {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "message",
        "module",
        "msecs",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
    }
)


def _safe_extra(extra: dict[str, Any]) -> dict[str, Any]:
    """Drop any reserved logging keys so `extra` can never crash the logger."""
    return {k: v for k, v in extra.items() if k not in _RESERVED_LOG_KEYS}


def _error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    body = ErrorResponse(error=ErrorBody(code=code, message=message, details=details))
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(),
        headers=headers,
    )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.warning(
        "domain_error",
        extra=_safe_extra(
            {
                "path": request.url.path,
                "method": request.method,
                "error_code": exc.code,
                "error_message": exc.message,
            }
        ),
    )
    headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
    return _error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        details=exc.details,
        headers=headers,
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # exc.errors() may contain non-JSON-serializable objects in `ctx`
    # (e.g. ValueError instances from custom validators). Stringify them.
    errors = []
    for err in exc.errors():
        clean = {k: v for k, v in err.items() if k != "ctx"}
        if "ctx" in err:
            clean["ctx"] = {k: str(v) for k, v in err["ctx"].items()}
        errors.append(clean)

    return _error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="validation_error",
        message="Request validation failed",
        details=errors,
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    code_map: dict[int, str] = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        409: "conflict",
        422: "validation_error",
        429: "rate_limited",
        500: "internal_error",
    }
    code = code_map.get(exc.status_code, "http_error")
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return _error_response(
        status_code=exc.status_code,
        code=code,
        message=message,
        headers=dict(exc.headers) if exc.headers is not None else None,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "unhandled_exception",
        extra=_safe_extra({"path": request.url.path, "method": request.method}),
    )
    message = (
        f"{exc.__class__.__name__}: {exc}" if settings.debug else "Internal server error"
    )
    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="internal_error",
        message=message,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
