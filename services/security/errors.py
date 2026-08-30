"""
FinResolve AI — Standardized Error Handling

Sanitized API error responses without leaking internal filesystem paths or stack traces.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

logger = logging.getLogger("finresolve.api.errors")


def register_error_handlers(app: FastAPI) -> None:
    """Register sanitized global error handlers on the FastAPI application."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Categorize code based on HTTP status
        code_map = {
            400: "BAD_REQUEST",
            401: "AUTHENTICATION_REQUIRED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            413: "PAYLOAD_TOO_LARGE",
            422: "VALIDATION_ERROR",
            429: "RATE_LIMITED",
            500: "INTERNAL_ERROR",
        }
        error_code = code_map.get(exc.status_code, "ERROR")

        return JSONResponse(
            status_code=exc.status_code,
            headers=getattr(exc, "headers", None) or {},
            content={
                "error": {
                    "code": error_code,
                    "message": str(exc.detail),
                    "request_id": request_id,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Sanitize error detail list
        sanitized_errors = []
        for err in exc.errors():
            sanitized_errors.append({
                "field": ".".join(str(loc) for loc in err.get("loc", [])),
                "message": err.get("msg", "Invalid field"),
                "type": err.get("type", "value_error"),
            })

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request payload validation failed",
                    "details": sanitized_errors,
                    "request_id": request_id,
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Internal log contains full exception for server diagnostics
        logger.error(
            "Unhandled server error during request [%s]: %s",
            request_id,
            str(exc),
            exc_info=True,
        )

        # External client response is STRICTLY sanitized (zero stack trace, zero internal path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An internal server error occurred. Please contact support with the request ID.",
                    "request_id": request_id,
                }
            },
        )
