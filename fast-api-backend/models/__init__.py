"""
Models package for FastAPI backend.

Exports all Pydantic models for request/response validation.
"""

from models.schemas import (
    # Request Models
    LeetCodeRequest,
    ObtainedRequest,
    CacheClearRequest,
    
    # Response Models - /lc endpoint
    UserResult,
    LeetCodeResponse,
    
    # Response Models - /obtained endpoint
    ObtainedUserResult,
    
    # Generic Response Models
    ErrorResponse,
    HealthResponse,
    CacheClearResponse,
)

__all__ = [
    # Request Models
    "LeetCodeRequest",
    "ObtainedRequest",
    "CacheClearRequest",
    
    # Response Models - /lc endpoint
    "UserResult",
    "LeetCodeResponse",
    
    # Response Models - /obtained endpoint
    "ObtainedUserResult",
    
    # Generic Response Models
    "ErrorResponse",
    "HealthResponse",
    "CacheClearResponse",
]
