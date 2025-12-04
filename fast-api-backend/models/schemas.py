"""
Pydantic models for FastAPI request/response validation.

This module defines all the data models used in the LeetCode rating prediction API.
Models are based on the API specification and example responses.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Request Models
# ============================================================================

class LeetCodeRequest(BaseModel):
    """
    Request model for the /lc endpoint.
    
    Query Parameters:
    - contestType: Type of contest (e.g., "weekly-contest-" or "biweekly-contest-")
    - contestNo: Contest number (e.g., "476")
    - channelNo: Optional Discord channel ID to fetch users from Firebase
    - username: Optional single LeetCode username (comma-separated for multiple)
    
    Note: Either channelNo or username must be provided.
    """
    contestType: str = Field(
        ..., 
        description="Contest type prefix (e.g., 'weekly-contest-' or 'biweekly-contest-')",
        examples=["weekly-contest-", "biweekly-contest-"]
    )
    contestNo: str = Field(
        ..., 
        description="Contest number",
        examples=["476", "102"]
    )
    channelNo: Optional[str] = Field(
        None, 
        description="Discord channel ID to fetch users from Firebase"
    )
    username: Optional[str] = Field(
        None, 
        description="LeetCode username(s), comma-separated for multiple users"
    )

    @field_validator('contestType')
    @classmethod
    def validate_contest_type(cls, v: str) -> str:
        """Ensure contestType ends with a hyphen."""
        if not v.endswith('-'):
            return f"{v}-"
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "contestType": "weekly-contest-",
                "contestNo": "476",
                "channelNo": "102",
                "username": "deekshith06"
            }
        }


class ObtainedRequest(BaseModel):
    """
    Request model for the /obtained endpoint.
    
    Query Parameters:
    - name: Full contest name (e.g., "weekly-contest-476")
    - usernames: Comma-separated usernames
    - channelNo: Optional Discord channel ID
    """
    name: str = Field(
        ..., 
        description="Full contest name",
        examples=["weekly-contest-476"]
    )
    usernames: Optional[str] = Field(
        None, 
        description="Comma-separated LeetCode usernames"
    )
    channelNo: Optional[str] = Field(
        None, 
        description="Discord channel ID to fetch users from Firebase"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "weekly-contest-476",
                "usernames": "deekshith06,S_Sarim",
                "channelNo": "102"
            }
        }


class CacheClearRequest(BaseModel):
    """Request model for cache clearing endpoint."""
    cache_type: str = Field(
        default="all",
        description="Type of cache to clear: 'all', 'user', or 'channel'",
        examples=["all", "user", "channel"]
    )

    @field_validator('cache_type')
    @classmethod
    def validate_cache_type(cls, v: str) -> str:
        """Validate cache_type is one of the allowed values."""
        allowed = {"all", "user", "channel"}
        if v not in allowed:
            raise ValueError(f"cache_type must be one of {allowed}")
        return v


# ============================================================================
# Response Models - /lc endpoint
# ============================================================================

class UserResult(BaseModel):
    """
    Individual user result for the /lc endpoint.
    
    For users who attended the contest, includes rating changes.
    For users who didn't attend or had errors, includes error message.
    """
    username: str = Field(..., description="LeetCode username")
    link: str = Field(..., description="Link to user's LeetCode profile")
    attended: bool = Field(..., description="Whether user attended the contest")
    
    # Fields for attended users
    rank: Optional[int] = Field(None, description="Contest rank")
    old_rating: Optional[float] = Field(None, description="Rating before contest")
    new_rating: Optional[float] = Field(None, description="Rating after contest")
    delta_rating: Optional[float] = Field(None, description="Rating change")
    attendedContestsCount: Optional[int] = Field(None, description="Total contests attended")
    
    # Field for non-attended users or errors
    error: Optional[str] = Field(None, description="Error message if any")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "username": "deekshith06",
                    "link": "https://leetcode.com/u/deekshith06/",
                    "attended": True,
                    "rank": 6623,
                    "old_rating": 1785.84,
                    "new_rating": 1771.76,
                    "delta_rating": -14.08,
                    "attendedContestsCount": 42
                },
                {
                    "username": "Ram000",
                    "link": "https://leetcode.com/u/Ram000/",
                    "attended": False,
                    "error": "❌ Not Participated"
                }
            ]
        }


class LeetCodeResponse(BaseModel):
    """
    Complete response for the /lc endpoint.
    
    Contains contest name and list of user results.
    May include an error field if the contest is not found.
    """
    contestName: str = Field(..., description="Full contest name")
    users: List[UserResult] = Field(
        default_factory=list, 
        description="List of user results"
    )
    error: Optional[str] = Field(
        None, 
        description="Error message if contest not found or other issues"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "contestName": "weekly-contest-476",
                "users": [
                    {
                        "username": "deekshith06",
                        "link": "https://leetcode.com/u/deekshith06/",
                        "attended": True,
                        "rank": 6623,
                        "old_rating": 1785.84,
                        "new_rating": 1771.76,
                        "delta_rating": -14.08,
                        "attendedContestsCount": 42
                    }
                ]
            }
        }


# ============================================================================
# Response Models - /obtained endpoint
# ============================================================================

class ObtainedUserResult(BaseModel):
    """
    Individual user result for the /obtained endpoint.
    
    Shows actual contest performance (problems solved, ranking, etc.)
    """
    problemsSolved: Optional[int] = Field(None, description="Number of problems solved")
    totalProblems: Optional[int] = Field(None, description="Total problems in contest")
    ranking: Optional[int] = Field(None, description="User's ranking in contest")
    rating: Optional[float] = Field(None, description="User's rating after contest")
    error: Optional[str] = Field(None, description="Error message if any")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "problemsSolved": 3,
                    "totalProblems": 4,
                    "ranking": 2790,
                    "rating": 1766.448
                },
                {
                    "error": "Username is required"
                }
            ]
        }


# ============================================================================
# Generic Response Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response format."""
    detail: str = Field(..., description="Error message")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Contest not found"
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="healthy", description="Service status")
    message: str = Field(default="Service is running", description="Status message")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "message": "Service is running"
            }
        }


class CacheClearResponse(BaseModel):
    """Response for cache clear operation."""
    success: bool = Field(..., description="Whether cache was cleared successfully")
    message: str = Field(..., description="Status message")
    cache_type: str = Field(..., description="Type of cache that was cleared")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Cache cleared successfully",
                "cache_type": "all"
            }
        }