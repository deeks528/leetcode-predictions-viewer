"""
LeetCode API Router

This module defines the API endpoints for LeetCode rating predictions.
Endpoints:
- GET /lc - Get rating predictions for a contest
- POST /cache/clear - Clear the cache (optional)
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional, List, Dict
import logging

from models.schemas import (
    LeetCodeResponse,
    UserResult,
    ErrorResponse,
    CacheClearResponse,
    ObtainedUserResult,
)
from helpers import lc, clear_cache, get_user_contest_ratings
from db_config import get_users

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="",
    tags=["leetcode"],
    responses={
        404: {"model": ErrorResponse, "description": "Not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)


@router.get(
    "/lc",
    response_model=LeetCodeResponse,
    summary="Get LeetCode rating predictions",
    description="""
    Get rating predictions for users in a specific LeetCode contest.
    
    You must provide either:
    - `channelNo` to fetch users from Firebase, OR
    - `username` for a single user or comma-separated usernames
    
    The endpoint will return predicted ratings based on contest performance.
    """,
    responses={
        200: {
            "description": "Successful response with user predictions",
            "model": LeetCodeResponse,
        },
        400: {
            "description": "Bad request - missing or invalid parameters",
            "model": ErrorResponse,
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse,
        },
    },
)
async def get_leetcode_predictions(
    contestType: str = Query(
        ...,
        description="Contest type (e.g., 'weekly-contest-' or 'biweekly-contest-')",
        example="weekly-contest-",
    ),
    contestNo: str = Query(
        ...,
        description="Contest number",
        example="476",
    ),
    channelNo: Optional[str] = Query(
        None,
        description="Discord channel ID to fetch users from Firebase",
        example="",
    ),
    username: Optional[str] = Query(
        None,
        description="LeetCode username(s), comma-separated for multiple users",
        example="",
    ),
) -> LeetCodeResponse:
    """
    Get LeetCode rating predictions for a contest.
    
    Args:
        contestType: Contest type prefix (e.g., "weekly-contest-")
        contestNo: Contest number
        channelNo: Optional Discord channel ID
        username: Optional username(s)
    
    Returns:
        LeetCodeResponse with contest name and user results
    
    Raises:
        HTTPException: If validation fails or an error occurs
    """
    try:
        # Validate that at least one of channelNo or username is provided
        if not channelNo and not username:
            logger.warning("Request missing both channelNo and username")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either 'channelNo' or 'username' must be provided",
            )
        
        # Ensure contestType ends with hyphen
        if not contestType.endswith('-'):
            contestType = f"{contestType}-"
        
        # Build contest name
        contest_name = f"{contestType}{contestNo}"
        logger.info(f"Processing request for contest: {contest_name}")
        
        # Get users list
        users_list: List[str] = []
        
        if channelNo:
            # Fetch users from Firebase
            logger.info(f"Fetching users from Firebase channel: {channelNo}")
            try:
                users_set = get_users(channelNo)
                if not users_set:
                    logger.warning(f"No users found for channel: {channelNo}")
                    # Return empty response if no users in channel
                    return LeetCodeResponse(
                        contestName=contest_name,
                        users=[],
                    )
                users_list = list(users_set)
                logger.info(f"Found {len(users_list)} users in channel {channelNo}")
            except Exception as e:
                logger.error(f"Error fetching users from Firebase: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch users from Firebase: {str(e)}",
                )
        
        if username:
            # Parse comma-separated usernames
            username_list = [u.strip() for u in username.split(',') if u.strip()]
            users_list.extend(username_list)
            logger.info(f"Added {len(username_list)} usernames from query parameter")
        
        # Remove duplicates and filter invalid values
        users_list = [u for u in dict.fromkeys(users_list) if u and isinstance(u, str) and u.strip()]
        
        if not users_list:
            logger.warning("No valid users to process")
            return LeetCodeResponse(
                contestName=contest_name,
                users=[],
            )
        
        logger.info(f"Processing {len(users_list)} users for contest {contest_name}")
        
        # Call helper function to get predictions
        try:
            results, is_future_contest = lc(contest_name, tuple(users_list))
            
            # Check if this is a future contest (all users didn't participate)
            if is_future_contest:
                logger.info(f"Contest {contest_name} appears to be a future contest")
                return LeetCodeResponse(
                    contestName=contest_name,
                    users=[],
                )
            
            # Check if there's a global error (contest not found)
            if results and len(results) > 0:
                first_result = results[0]
                if hasattr(first_result, 'error') and first_result.error and first_result.username == "":
                    # This is a contest-level error
                    logger.warning(f"Contest error: {first_result.error}")
                    return LeetCodeResponse(
                        contestName=contest_name,
                        users=[],
                        error=first_result.error,
                    )
            
            logger.info(f"Successfully processed {len(results)} user results")
            
            return LeetCodeResponse(
                contestName=contest_name,
                users=results,
            )
            
        except Exception as e:
            logger.error(f"Error calling lc helper: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing contest data: {str(e)}",
            )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error in get_leetcode_predictions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


@router.post(
    "/cache/clear",
    response_model=CacheClearResponse,
    summary="Clear cache",
    description="""
    Clear the LRU cache for LeetCode data.
    
    Cache types:
    - `all`: Clear all caches (user and channel)
    - `user`: Clear only user response cache
    - `channel`: Clear only channel/contest cache
    """,
    responses={
        200: {
            "description": "Cache cleared successfully",
            "model": CacheClearResponse,
        },
        400: {
            "description": "Invalid cache type",
            "model": ErrorResponse,
        },
    },
)
async def clear_cache_endpoint(
    cache_type: str = Query(
        "all",
        description="Type of cache to clear: 'all', 'user', or 'channel'",
        example="all",
    ),
) -> CacheClearResponse:
    """
    Clear the cache.
    
    Args:
        cache_type: Type of cache to clear (all/user/channel)
    
    Returns:
        CacheClearResponse with success status
    
    Raises:
        HTTPException: If cache_type is invalid
    """
    try:
        # Validate cache_type
        valid_types = {"all", "user", "channel"}
        if cache_type not in valid_types:
            logger.warning(f"Invalid cache_type requested: {cache_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid cache_type. Must be one of: {', '.join(valid_types)}",
            )
        
        logger.info(f"Clearing cache: {cache_type}")
        clear_cache(cache_type)
        
        return CacheClearResponse(
            success=True,
            message=f"Cache cleared successfully",
            cache_type=cache_type,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}",
        )


@router.get(
    "/obtained",
    response_model=Dict[str, ObtainedUserResult],
    summary="Get actual contest performance",
    description="""
    Get actual contest performance data for users (problems solved, ranking, rating).
    
    This endpoint fetches real contest results from LeetCode's GraphQL API,
    showing how users actually performed in a specific contest.
    
    You must provide either:
    - `channelNo` to fetch users from Firebase, OR
    - `usernames` for comma-separated usernames
    
    Returns a dictionary where keys are usernames and values are performance data.
    """,
    responses={
        200: {
            "description": "Dictionary of user contest performance results",
            "model": Dict[str, ObtainedUserResult],
        },
        400: {
            "description": "Bad request - missing or invalid parameters",
            "model": ErrorResponse,
        },
    },
)
async def get_obtained_ratings(
    name: str = Query(
        ...,
        description="Full contest name (e.g., 'weekly-contest-476')",
        example="weekly-contest-476",
    ),
    username: Optional[str] = Query(
        None,
        description="Comma-separated LeetCode usernames",
        example="",
    ),
    channelNo: Optional[str] = Query(
        None,
        description="Discord channel ID to fetch users from Firebase",
        example="",
    ),
) -> Dict[str, ObtainedUserResult]:
    """
    Get actual contest performance data for users.
    
    Args:
        name: Full contest name
        usernames: Optional comma-separated usernames
        channelNo: Optional Discord channel ID
    
    Returns:
        Dictionary of ObtainedUserResult with actual contest performance
    
    Raises:
        HTTPException: If validation fails or an error occurs
    """
    try:
        # Validate contest name is provided
        if not name:
            logger.warning("Contest name is required but not provided")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contest name is required",
            )
        
        # Validate that at least one of channelNo or usernames is provided
        if not channelNo and not username:
            logger.warning("Request missing both channelNo and usernames")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either 'channelNo' or 'usernames' must be provided",
            )
        
        logger.info(f"Processing /obtained request for contest: {name}")
        
        # Get users list
        users_list: List[str] = []
        
        if channelNo:
            # Fetch users from Firebase
            logger.info(f"Fetching users from Firebase channel: {channelNo}")
            try:
                users_set = get_users(channelNo)
                if users_set:
                    users_list.extend(list(users_set))
                    logger.info(f"Found {len(users_set)} users in channel {channelNo}")
            except Exception as e:
                logger.error(f"Error fetching users from Firebase: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch users from Firebase: {str(e)}",
                )
        
        if username:
            # Parse comma-separated usernames
            username_list = [u.strip() for u in username.split(',') if u.strip()]
            users_list.extend(username_list)
            logger.info(f"Added {len(username_list)} usernames from query parameter")
        
        # Remove duplicates while preserving order
        users_list = list(dict.fromkeys(users_list))
        
        if not users_list:
            logger.warning("No valid users to process")
            return {}
        
        logger.info(f"Fetching contest data for {len(users_list)} users")
        
        # Fetch contest data for each user
        results: Dict[str, ObtainedUserResult] = {}
        
        for user in users_list:
            if not user:
                continue
            
            try:
                # Call GraphQL helper to get user's contest performance
                user_data = get_user_contest_ratings(name, user)
                
                # Convert to ObtainedUserResult
                results[user] = ObtainedUserResult(**user_data)
                
            except Exception as e:
                logger.error(f"Error fetching data for user '{user}': {str(e)}")
                results[user] = ObtainedUserResult(
                        error=f"Error: {str(e)}"
                    )
        
        logger.info(f"Successfully processed {len(results)} user results")
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_obtained_ratings: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )