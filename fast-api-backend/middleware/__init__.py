"""
Middleware package for FastAPI application.

Exports CORS configuration and other middleware utilities.
"""

from middleware.cors import (
    setup_cors,
    get_allowed_origins,
    get_cors_config,
)

__all__ = [
    "setup_cors",
    "get_allowed_origins",
    "get_cors_config",
]
