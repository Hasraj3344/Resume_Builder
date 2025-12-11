"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


# Import and include routers
from backend.routers import auth

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

# Note: These will be created in subsequent steps
# from backend.routers import user, resume, subscription, webhook
#
# app.include_router(user.router, prefix="/api/user", tags=["User"])
# app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
# app.include_router(subscription.router, prefix="/api/subscription", tags=["Subscription"])
# app.include_router(webhook.router, prefix="/api/webhook", tags=["Webhooks"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
