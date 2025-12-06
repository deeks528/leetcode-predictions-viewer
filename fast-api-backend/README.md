# LeetCode Rating Prediction API

FastAPI backend for LeetCode contest rating predictions and performance tracking.

## 🚀 Features

- **Rating Predictions** - Get predicted ratings for users in upcoming LeetCode contests
- **Actual Performance** - Fetch real contest results from LeetCode's GraphQL API
- **Cache Management** - LRU cache for improved performance
- **Firebase Integration** - Manage users via Discord channels
- **CORS Support** - Ready for React frontend integration
- **Auto Documentation** - Interactive Swagger UI and ReDoc

## 📋 Prerequisites

- Python 3.11+
- `uv` package manager
- Firebase credentials (for user management)

## 🛠️ Installation

### 1. Clone the repository

```bash
cd fast-api-backend
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```bash
PORT=7667
FIREBASE_CREDENTIALS_PATH=db_config/discordbot1-*.json
ALLOWED_ORIGINS=http://localhost:3000
```

### 4. Add Firebase credentials

Place your Firebase credentials JSON file in the `db_config/` directory.

## 🏃 Running the Application

### Development Mode (with auto-reload)

```bash
uv run fastapi dev --port 7667
```

Or using the main script:

```bash
uv run python main.py
```

### Production Mode

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 7667
```

The API will be available at:
- **API**: http://localhost:7667
- **Swagger UI**: http://localhost:7667/docs
- **ReDoc**: http://localhost:7667/redoc

## 📚 API Endpoints

### Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "message": "LeetCode Rating Prediction API is running"
}
```

### Rating Predictions

**GET** `/lc`

Get predicted ratings for users in a specific contest.

**Query Parameters:**
- `contestType` (required) - Contest type (e.g., "weekly-contest-")
- `contestNo` (required) - Contest number (e.g., "476")
- `channelNo` (optional) - Discord channel ID
- `username` (optional) - Comma-separated usernames

**Example:**
```bash
curl "http://localhost:7667/lc?contestType=weekly-contest-&contestNo=476&username=abcd"
```

**Response:**
```json
{
  "contestName": "weekly-contest-476",
  "users": [
    {
      "username": "abcd",
      "link": "https://leetcode.com/u/abcd/",
      "attended": true,
      "rank": 6623,
      "old_rating": 1785.84,
      "new_rating": 1771.76,
      "delta_rating": -14.08,
      "attendedContestsCount": 42
    }
  ]
}
```

### Actual Contest Performance

**GET** `/obtained`

Get actual contest performance data from LeetCode.

**Query Parameters:**
- `name` (required) - Full contest name (e.g., "weekly-contest-476")
- `usernames` (optional) - Comma-separated usernames
- `channelNo` (optional) - Discord channel ID

**Example:**
```bash
curl "http://localhost:7667/obtained?name=weekly-contest-476&usernames=abcd,xyz"
```

**Response:**
```json
[
  {
    "username": "abcd",
    "problemsSolved": 3,
    "totalProblems": 4,
    "ranking": 2790,
    "rating": 1766.448
  },
  {
    "username": "xyz",
    "problemsSolved": 3,
    "totalProblems": 4,
    "ranking": 1585,
    "rating": 1739.108
  }
]
```

### Clear Cache

**POST** `/cache/clear`

Clear the LRU cache.

**Query Parameters:**
- `cache_type` (optional, default: "all") - Type of cache to clear ("all", "user", or "channel")

**Example:**
```bash
curl -X POST "http://localhost:7667/cache/clear?cache_type=all"
```

**Response:**
```json
{
  "success": true,
  "message": "Cache cleared successfully",
  "cache_type": "all"
}
```

## 📁 Project Structure

```
fast-api-backend/
├── main.py                 # FastAPI app entry point
├── pyproject.toml         # Dependencies (managed by uv)
├── uv.lock               # Lock file
├── .env                  # Environment variables
├── db_config/
│   ├── __init__.py
│   ├── firebase_config.py    # Firebase initialization
│   └── *.json                # Firebase credentials
├── helpers/
│   ├── __init__.py
│   ├── cache.py              # LRU cache implementation
│   ├── lc_helper.py          # Rating prediction logic
│   └── lc_graphql.py         # LeetCode GraphQL API
├── models/
│   ├── __init__.py
│   └── schemas.py            # Pydantic models
├── routers/
│   ├── __init__.py
│   └── leetcode.py           # API endpoints
└── middleware/
    ├── __init__.py
    └── cors.py               # CORS configuration
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `7667` |
| `FIREBASE_CREDENTIALS_PATH` | Path to Firebase credentials | `db_config/discordbot1-*.json` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `http://localhost:3000` |

### CORS Configuration

The API is configured to allow requests from the React frontend. Update `ALLOWED_ORIGINS` in `.env` to add more origins:

```bash
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://yourdomain.com
```

## 🧪 Testing

### Manual Testing

Use the interactive Swagger UI at http://localhost:7667/docs to test endpoints.

### Using curl

```bash
# Health check
curl http://localhost:7667/health

# Get predictions
curl "http://localhost:7667/lc?contestType=weekly-contest-&contestNo=476&username=abcd"

# Get actual performance
curl "http://localhost:7667/obtained?name=weekly-contest-476&usernames=abcd"

# Clear cache
curl -X POST "http://localhost:7667/cache/clear?cache_type=all"
```

## 📊 Logging

The application logs all requests and important events:

```
2025-12-04 12:30:00 - INFO - 🚀 Starting LeetCode Rating Prediction API
2025-12-04 12:30:00 - INFO - 📡 Server Port: 7667
2025-12-04 12:30:00 - INFO - 🌐 Allowed Origins: http://localhost:3000
2025-12-04 12:30:00 - INFO - ✅ Firebase connection verified
2025-12-04 12:30:00 - INFO - ✅ Application startup complete
2025-12-04 12:30:05 - INFO - 📥 GET /lc
2025-12-04 12:30:06 - INFO - 📤 GET /lc - Status: 200
```

## 🚀 Deployment

### Production Checklist

- [ ] Update `ALLOWED_ORIGINS` to production domain
- [ ] Set `PORT` to production port
- [ ] Disable auto-reload in uvicorn
- [ ] Configure proper logging
- [ ] Add rate limiting (optional)
- [ ] Set up monitoring
- [ ] Configure HTTPS

### Production Command

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 7667 --workers 4
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

MIT License

## 🔗 Links

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [LeetCode](https://leetcode.com)
- [Firebase](https://firebase.google.com)

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ using FastAPI
