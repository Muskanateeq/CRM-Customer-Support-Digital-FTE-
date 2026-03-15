"""
CORS Middleware Configuration

Configures Cross-Origin Resource Sharing (CORS) for the FastAPI application.
Note: CORS is already configured in main.py, this module provides additional utilities.
"""

from fastapi.middleware.cors import CORSMiddleware
from src.config import settings


def get_cors_config() -> dict:
    """
    Get CORS configuration dictionary.

    Returns:
        Dictionary with CORS configuration parameters
    """
    return {
        "allow_origins": settings.CORS_ORIGINS,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }


def add_cors_middleware(app):
    """
    Add CORS middleware to FastAPI application.

    Args:
        app: FastAPI application instance

    Example:
        from fastapi import FastAPI
        from src.middleware.cors import add_cors_middleware

        app = FastAPI()
        add_cors_middleware(app)
    """
    app.add_middleware(
        CORSMiddleware,
        **get_cors_config()
    )
