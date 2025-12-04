"""
CORS middleware configuration for FastAPI.

Configures Cross-Origin Resource Sharing (CORS) to allow the React frontend
to communicate with the FastAPI backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import List


def get_allowed_origins() -> List[str]:
    """
    Get allowed origins from environment variable.
    
    Returns:
        List of allowed origin URLs
    """
    origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
    # Split by comma and strip whitespace
    origins = [origin.strip() for origin in origins_env.split(",")]
    return origins


def setup_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    
    This allows:
    - Requests from specified origins (React frontend)
    - All HTTP methods (GET, POST, PUT, DELETE, etc.)
    - Credentials (cookies, authorization headers)
    - All headers
    """
    allowed_origins = get_allowed_origins()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # List of allowed origins
        allow_credentials=True,          # Allow cookies and auth headers
        allow_methods=["*"],             # Allow all HTTP methods
        allow_headers=["*"],             # Allow all headers
        expose_headers=["*"],            # Expose all headers to the client
        max_age=600,                     # Cache preflight requests for 10 minutes
    )
    
    print(f"✅ CORS configured for origins: {', '.join(allowed_origins)}")


def get_cors_config() -> dict:
    """
    Get CORS configuration as a dictionary.
    
    Useful for debugging or displaying current CORS settings.
    
    Returns:
        Dictionary with CORS configuration
    """
    return {
        "allowed_origins": get_allowed_origins(),
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
        "expose_headers": ["*"],
        "max_age": 600,
    }
