"""
ATS CV Maker FastAPI Application
Main application server entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from dotenv import load_dotenv

from .auth_routes import auth_router
from .db import init_db
from .routes import router
from .models import HealthResponse

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ATS CV Maker API",
    description="REST API for analyzing and improving CVs for ATS compatibility",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
default_cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

raw_cors_origins = os.getenv("CORS_ORIGINS", ",".join(default_cors_origins))
cors_origins = [origin.strip() for origin in raw_cors_origins.split(",") if origin.strip()]

# CORS wildcard cannot be combined with credentials in browser requests.
if "*" in cors_origins:
    logger.warning(
        "CORS_ORIGINS contains '*'. Replacing with explicit local development origins "
        "because cookies are enabled."
    )
    cors_origins = default_cors_origins


def _add_localhost_variants(origins: list[str]) -> list[str]:
    """
    Ensure localhost/127.0.0.1 variants are both allowed for each local origin.
    """
    expanded: list[str] = []

    for origin in origins:
        if origin not in expanded:
            expanded.append(origin)

        if "localhost" in origin:
            variant = origin.replace("localhost", "127.0.0.1")
            if variant not in expanded:
                expanded.append(variant)
        elif "127.0.0.1" in origin:
            variant = origin.replace("127.0.0.1", "localhost")
            if variant not in expanded:
                expanded.append(variant)

    return expanded


cors_origins = _add_localhost_variants(cors_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZIP compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routes
app.include_router(router)
app.include_router(auth_router)


@app.on_event("startup")
async def startup_event():
    """Initialize required database tables on startup."""
    init_db()


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns basic information about the API status.
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        api_ready=True
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to ATS CV Maker API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "analyze": "/api/v1/analyze",
            "improve": "/api/v1/improve",
            "match_skills": "/api/v1/match-skills"
        }
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
