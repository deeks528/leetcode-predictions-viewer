# requests

1. to get user contest info
{
    'url': 'https://leetcode.com/graphql/',
    'method': 'POST',
    'body': {
                "operationName": "userContestRankingInfo",
                "variables": {
                    "username": "deekshith06"
                },
                "query": "query userContestRankingInfo($username: String!) {\n  userContestRanking(username: $username) {\n    attendedContestsCount\n    rating\n    globalRanking\n    totalParticipants\n    topPercentage\n    badge {\n      name\n    }\n  }\n  userContestRankingHistory(username: $username) {\n    attended\n    problemsSolved\n    totalProblems\n   rating\n    ranking\n    contest {\n      title\n      }\n  }\n}"
            }   
}

2. list all contests
{
    'url1': https://alfa-leetcode-api.onrender.com/contests,
    'url2': https://alfa-leetcode-api.onrender.com/contests/upcoming,
    'method': 'GET'
}