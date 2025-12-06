"""
LeetCode GraphQL Helper

This module provides functions to query LeetCode's GraphQL API
for user contest performance data.
"""

import requests
from typing import Dict, Any, Optional
import logging
from helpers.cache import LRUCache

logger = logging.getLogger(__name__)

# HTTP headers for LeetCode GraphQL requests
LEETCODE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Content-Type": "application/json",
    "Accept": "application/json"
}

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql/"


# Global cache for GraphQL requests
graphql_cache = LRUCache(capacity=43)


def get_user_contest_ratings(contest_name: str, username: str) -> Dict[str, Any]:
    """
    Fetch a user's performance data for a specific contest from LeetCode GraphQL API.
    
    Args:
        contest_name: Full contest name (e.g., "weekly-contest-476")
        username: LeetCode username
    
    Returns:
        Dictionary containing:
        - On success: username, rating, ranking, problemsSolved, totalProblems
        - On error: error message
    
    Examples:
        >>> get_user_contest_ratings("weekly-contest-476", "abcd")
        {
            "username": "abcd",
            "rating": 1766.448,
            "ranking": 2790,
            "problemsSolved": 3,
            "totalProblems": 4
        }
        
        >>> get_user_contest_ratings("weekly-contest-476", "")
        {"error": "Username is required"}
    """
    # Check cache first
    cache_key = (contest_name, username)
    cached_result = graphql_cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    # Validate contest name
    if not contest_name or not (
        contest_name.startswith("weekly-contest-") or 
        contest_name.startswith("biweekly-contest-")
    ):
        logger.warning(f"Invalid contest name: {contest_name}")
        return {"error": "Invalid contest name"}

    if not username:
        logger.warning("Username is required but not provided")
        return {"error": "Username is required"}
    
    # Convert contest name to LeetCode's format (spaces instead of hyphens, lowercase)
    # e.g., "weekly-contest-476" -> "weekly contest 476"
    contest_title = contest_name.replace("-", " ").lower()
    
    # GraphQL query to fetch user contest ranking history
    graphql_body = {
        "operationName": "userContestRankingInfo",
        "variables": {"username": username},
        "query": """
            query userContestRankingInfo($username: String!) {
              userContestRanking(username: $username) {
                attendedContestsCount
                rating
                globalRanking
                totalParticipants
                topPercentage
                badge {
                  name
                }
              }
              userContestRankingHistory(username: $username) {
                attended
                problemsSolved
                totalProblems
                rating
                ranking
                contest {
                  title
                }
              }
            }
        """
    }

    try:
        logger.info(f"Fetching contest data for user '{username}' in contest '{contest_name}'")
        
        response = requests.post(
            LEETCODE_GRAPHQL_URL,
            json=graphql_body,
            headers=LEETCODE_HEADERS,
            timeout=10
        )
        
        # Check if response is JSON (not HTML/Cloudflare block)
        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            logger.error(f"Non-JSON response received (likely Cloudflare block): {content_type}")
            logger.debug(f"Response preview: {response.text[:200]}")
            return {"error": "Cloudflare blocked the request"}

        data = response.json()
        
        # Check for GraphQL errors
        if "errors" in data:
            error_msg = data["errors"][0].get("message", "Unknown GraphQL error")
            logger.error(f"GraphQL error for user '{username}': {error_msg}")
            return {"error": error_msg}

        # Extract contest ranking history
        contest_history = data.get("data", {}).get("userContestRankingHistory", [])
        if not contest_history:
            logger.warning(f"No contest history found for user '{username}'")
            return {"error": "No contest history found for user","contest_history_found": False}
        
        # Search for the specific contest in reverse order (most recent first)
        for contest_entry in range(len(contest_history)-1,-1,-1):
            contest_entry = contest_history[contest_entry]
            contest = contest_entry.get("contest", {})
            entry_title = contest.get("title", "").lower()
            
            if entry_title == contest_title:
                result = {
                    "username": username,
                    "rating": contest_entry.get("rating"),
                    "ranking": contest_entry.get("ranking"),
                    "problemsSolved": contest_entry.get("problemsSolved"),
                    "totalProblems": contest_entry.get("totalProblems"),
                    "contest_history_found": True
                }
                logger.info(f"Found contest data for '{username}': rank {result['ranking']}")
                
                # Cache successful result
                graphql_cache.put(cache_key, result)
                return result

        # Contest not found in user's history
        logger.warning(f"Contest '{contest_name}' not found in history for user '{username}'")
        return {"error": "Contest not found in user's history","contest_history_found": False}

    except requests.Timeout:
        logger.error(f"Timeout while fetching data for user '{username}'")
        return {"error": "Request timeout"}
    except requests.RequestException as e:
        logger.error(f"Request error for user '{username}': {str(e)}")
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error for user '{username}': {str(e)}", exc_info=True)
        return {"error": str(e)}


def validate_contest_name(contest_name: str) -> bool:
    """
    Validate if a contest name follows the expected format.
    
    Args:
        contest_name: Contest name to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not contest_name:
        return False
    
    return (
        contest_name.startswith("weekly-contest-") or 
        contest_name.startswith("biweekly-contest-")
    )
