"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from backend.config import settings, validate_settings
from backend.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Args:
        app: FastAPI application instance
    """
    # Startup
    print("🚀 Starting Resume Builder API...")
    validate_settings()
    init_db()
    print("✓ API ready to accept requests")

    yield

    # Shutdown
    print("👋 Shutting down Resume Builder API...")


# Create FastAPI application
app = FastAPI(
    title="Resume Builder API",
    description="Backend API for AI-Powered Resume Builder with authentication and payment integration",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS - Development mode (allow common localhost ports)
cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)


@app.get("/")
async def root():
    """Root endpoint to check API status."""
    return {
        "message": "Resume Builder API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "paypal_mode": settings.PAYPAL_MODE
    }


# Mount static file directories
# Create directories if they don't exist
os.makedirs("uploads/profile_pics", exist_ok=True)
os.makedirs("uploads/resumes", exist_ok=True)
os.makedirs("output/resumes", exist_ok=True)

# Serve uploaded files (profile pictures, resumes)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Import and include routers
from backend.routers import auth, resume, jobs, generation, profile, chat, subscription

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(generation.router, prefix="/api/generation", tags=["Generation"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(subscription.router, prefix="/api/subscription", tags=["Subscription"])

# Note: These will be created in subsequent steps
# from backend.routers import subscription, webhook
#
# app.include_router(subscription.router, prefix="/api/subscription", tags=["Subscription"])
# app.include_router(webhook.router, prefix="/api/webhook", tags=["Webhooks"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
