import requests
from typing import List, Tuple
from helpers.cache import LRUCache
from models.schemas import UserResult

# Global caches
user_response_cache = LRUCache(capacity=40)  # for GET requests
lc_cache = LRUCache(capacity=10)        # for contest results


# ---------------------------------------------------------
# Cached GET request (no exceptions cached)
# ---------------------------------------------------------
def get_response(url: str):
    cached = user_response_cache.get(url)
    if cached is not None:
        return cached

    try:
        response = requests.get(url)
        data = response.json()

        # ---- API-level error (not in array form) ----
        if not (isinstance(data, dict) and "detail" in data):
            response.raise_for_status()

            # ---- Cache only valid list responses ----
            if isinstance(data, list):
                user_response_cache.put(url, data)
        return data
    except Exception:
        raise


# ---------------------------------------------------------
# Compute contest results (real logic here)
# ---------------------------------------------------------
def _compute_lc(contest_name: str, users: tuple) -> Tuple[List[UserResult], int, int]:
    results: List[UserResult] = []
    error_count = 0
    not_participated_count = 0

    for user in users:
        url = (
            f'https://lccn.lbao.site/api/v1/contest-records/user'
            f'?contest_name={contest_name}&username={user}&archived=false'
        )

        # Build result data as dict first, then convert to UserResult
        result_data = {
            "link": f"https://leetcode.com/u/{user}/",
            "username": user,
            "attended": True,
        }

        try:
            data = get_response(url)
            # print(data)
            if not data:
                result_data["attended"] = False
                result_data["error"] = "❌ Not Participated"
                not_participated_count += 1
            elif 'detail' in data:
                result_data['error'] = f"❌ {data['detail']}"
                result_data["attended"] = False
                result_data["username"] = ""
                error_count += len(users)
                return results, error_count, not_participated_count
            else:
                d = data[0]
                result_data['rank'] = d['rank']
                result_data['old_rating'] = d['old_rating']
                result_data['new_rating'] = d['new_rating']
                result_data['delta_rating'] = d['delta_rating']
                result_data['attendedContestsCount'] = d['attendedContestsCount']

        except Exception as e:
            result_data['error'] = f"⚠️ Error for {user}: `{str(e)}`"
            result_data["attended"] = False
            error_count += 1

        finally:
            # Convert dict to UserResult Pydantic model
            user_result = UserResult(**result_data)
            if user_result.attended:
                results.insert(0, user_result)
            else:
                results.append(user_result)

    # Sort final results
    results.sort(
        key=lambda x: (
            x.attended, 
            x.delta_rating if x.delta_rating is not None else -float("inf"),
            x.new_rating if x.new_rating is not None else -float("inf")
        ),
        reverse=True
    )

    return results, error_count, not_participated_count


# ---------------------------------------------------------
# Public lc() — Safe layer that prevents caching exceptions
# ---------------------------------------------------------
def lc(contest_name: str, users: tuple) -> Tuple[List[UserResult], bool]:
    key = (contest_name, users)

    cached = lc_cache.get(key)
    if cached is not None:
        return cached

    try:
        results, error_count, not_attempted = _compute_lc(contest_name, users)

        # Cache only good results
        if error_count == 0:
            lc_cache.put(key, (results, not_attempted>=len(users)))
        # print(results)
        return results, not_attempted>=len(users)

    except Exception as e:
        # Never cache failures
        lc_cache.remove(key)
        raise

# ---------------------------------------------------------
# Public clear_cache() — Safe layer that clears caches
# ---------------------------------------------------------
def clear_cache(cache_type: str = "all"):
    """Utility to clear all caches."""
    if cache_type in ("all", "user"):
        user_response_cache.clear()
    if cache_type in ("all", "channel"):
        lc_cache.clear()