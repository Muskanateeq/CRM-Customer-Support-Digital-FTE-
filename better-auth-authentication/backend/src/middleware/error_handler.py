"""
Error Handling Middleware

Provides centralized error handling for the FastAPI application.
Catches exceptions and returns consistent error responses.
"""

from typing import Callable
from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware:
    """
    Middleware to handle exceptions and return consistent error responses.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Can modify headers here if needed
                pass
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            # Handle the exception
            response = await self.handle_exception(exc)
            await response(scope, receive, send)

    async def handle_exception(self, exc: Exception) -> JSONResponse:
        """
        Handle different types of exceptions and return appropriate responses.

        Args:
            exc: The exception that was raised

        Returns:
            JSONResponse with error details
        """
        # Database errors
        if isinstance(exc, SQLAlchemyError):
            logger.error(f"Database error: {str(exc)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Database error occurred",
                    "error_type": "database_error"
                }
            )

        # Validation errors
        if isinstance(exc, ValidationError):
            logger.warning(f"Validation error: {str(exc)}")
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "detail": "Validation error",
                    "errors": exc.errors(),
                    "error_type": "validation_error"
                }
            )

        # Generic errors
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "error_type": "internal_error"
            }
        )


async def error_handler_middleware(request: Request, call_next: Callable):
    """
    Middleware function to catch and handle exceptions.

    Args:
        request: The incoming request
        call_next: The next middleware or route handler

    Returns:
        Response from the next handler or error response
    """
    try:
        response = await call_next(request)
        return response
    except SQLAlchemyError as exc:
        logger.error(f"Database error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Database error occurred",
                "error_type": "database_error"
            }
        )
    except ValidationError as exc:
        logger.warning(f"Validation error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Validation error",
                "errors": exc.errors(),
                "error_type": "validation_error"
            }
        )
    except Exception as exc:
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "error_type": "internal_error"
            }
        )
