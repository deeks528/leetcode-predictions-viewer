"""
FastAPI Backend for LeetCode Rating Prediction

Main application entry point with:
- CORS middleware configuration
- API routers
- Health check endpoint
- Startup/shutdown events
- Exception handlers
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

from middleware import setup_cors
from routers import leetcode_router
from models.schemas import HealthResponse, ErrorResponse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    Startup:
    - Log application start
    - Verify Firebase connection
    - Display configuration
    
    Shutdown:
    - Log application shutdown
    - Clean up resources
    """
    # Startup
    logger.info("=" * 60)
    logger.info("🚀 Starting LeetCode Rating Prediction API")
    logger.info("=" * 60)
    
    # Log configuration
    port = os.getenv("PORT", "7667")
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
    logger.info(f"📡 Server Port: {port}")
    logger.info(f"🌐 Allowed Origins: {allowed_origins}")
    
    # Verify Firebase connection
    try:
        from db_config import initialize_firebase
        initialize_firebase()
        logger.info("✅ Firebase connection verified")
    except Exception as e:
        logger.error(f"❌ Firebase connection failed: {str(e)}")
        logger.warning("⚠️  Application will start but Firebase features may not work")
    
    logger.info("=" * 60)
    logger.info("✅ Application startup complete")
    logger.info("📚 API Documentation: http://localhost:{}/docs".format(port))
    logger.info("📖 ReDoc Documentation: http://localhost:{}/redoc".format(port))
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("🛑 Shutting down LeetCode Rating Prediction API")
    logger.info("=" * 60)


# Create FastAPI application
app = FastAPI(
    title="LeetCode Rating Prediction API",
    description="""
    FastAPI backend for LeetCode contest rating predictions.
    
    ## Features
    
    * **Rating Predictions** - Get predicted ratings for upcoming contests
    * **Actual Performance** - Fetch real contest results from LeetCode
    * **Cache Management** - Clear cache for fresh data
    * **Firebase Integration** - Manage users via Discord channels
    
    ## Endpoints
    
    * `GET /lc` - Get rating predictions for a contest
    * `GET /obtained` - Get actual contest performance data
    * `POST /cache/clear` - Clear the LRU cache
    * `GET /health` - Health check endpoint
    
    ## Authentication
    
    Currently no authentication required. Consider adding API keys for production.
    """,
    version="1.0.0",
    contact={
        "name": "LeetCode Rating Prediction",
        "url": "https://github.com/yourusername/leetcode-rating-prediction",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan,
)

# Setup CORS middleware
setup_cors(app)

# Include routers
app.include_router(
    leetcode_router,
    tags=["LeetCode"],
)

# Health check endpoint
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check",
    description="Check if the API is running and healthy",
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns:
        HealthResponse with status and message
    """
    return HealthResponse(
        status="healthy",
        message="LeetCode Rating Prediction API is running"
    )


# Root endpoint
@app.get(
    "/",
    tags=["Root"],
    summary="Root endpoint",
    description="Welcome message and API information",
)
async def root():
    """
    Root endpoint with welcome message.
    
    Returns:
        Dictionary with welcome message and links
    """
    return {
        "message": "Welcome to LeetCode Rating Prediction API",
        "version": "1.0.0",
        "documentation": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "endpoints": {
            "predictions": "/lc",
            "actual_performance": "/obtained",
            "cache_clear": "/cache/clear"
        }
    }


# Exception handlers

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors with detailed error messages.
    
    Args:
        request: The request that caused the error
        exc: The validation error exception
    
    Returns:
        JSONResponse with error details
    """
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "body": exc.body,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions.
    
    Args:
        request: The request that caused the error
        exc: The exception
    
    Returns:
        JSONResponse with error message
    """
    logger.error(f"Unexpected error on {request.url.path}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "error": str(exc),
        },
    )


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming requests.
    
    Args:
        request: The incoming request
        call_next: The next middleware/route handler
    
    Returns:
        Response from the next handler
    """
    logger.info(f"📥 {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    logger.info(f"📤 {request.method} {request.url.path} - Status: {response.status_code}")
    
    return response


if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", "7667"))
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Enable auto-reload for development
        log_level="info",
    )
