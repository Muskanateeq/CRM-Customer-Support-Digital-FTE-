"""
TaskNest Backend API - Main Application Entry Point

This module initializes the FastAPI application with all necessary middleware,
routers, and configuration for the TaskNest Phase 2 backend.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    print("[App] Starting application...")
    try:
        from src.scheduler import scheduler
        scheduler.start()
        print("[App] Scheduler started successfully")
    except Exception as e:
        print(f"[App] Warning: Failed to start scheduler: {e}")

    yield

    # Shutdown
    print("[App] Shutting down application...")
    try:
        from src.scheduler import scheduler
        scheduler.shutdown()
        print("[App] Scheduler stopped successfully")
    except Exception as e:
        print(f"[App] Warning: Failed to stop scheduler: {e}")


# Create FastAPI application instance with lifespan
app = FastAPI(
    title="TaskNest API",
    description="RESTful API for TaskNest Phase 2 - Full-Stack Task Management Application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "TaskNest API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Include API routers
from src.api.auth import router as auth_router
from src.api.tasks import router as tasks_router
from src.api.tags import router as tags_router
from src.api.teams import router as teams_router
from src.api.comments import router as comments_router
from src.api.assignments import router as assignments_router
from src.api.notifications import router as notifications_router
from src.api.projects import router as projects_router
from src.api.milestones import router as milestones_router
from src.api.settings import router as settings_router
from src.api.analytics import router as analytics_router
from src.api.v1.chat import router as chat_router
from src.api.v1.activities import router as activities_router
from src.api.v1.trash import router as trash_router

app.include_router(auth_router, prefix=f"{settings.API_V1_PREFIX}")
app.include_router(tasks_router, prefix=f"{settings.API_V1_PREFIX}")
app.include_router(tags_router, prefix=f"{settings.API_V1_PREFIX}")
app.include_router(teams_router, prefix=f"{settings.API_V1_PREFIX}")
app.include_router(comments_router, prefix=f"{settings.API_V1_PREFIX}")
app.include_router(assignments_router, prefix=f"{settings.API_V1_PREFIX}")
app.include_router(notifications_router, prefix=f"{settings.API_V1_PREFIX}")
app.include_router(projects_router, prefix=f"{settings.API_V1_PREFIX}")
app.include_router(milestones_router, prefix=f"{settings.API_V1_PREFIX}")
app.include_router(settings_router, prefix=f"{settings.API_V1_PREFIX}")
app.include_router(analytics_router, prefix=f"{settings.API_V1_PREFIX}")
app.include_router(chat_router, prefix=f"{settings.API_V1_PREFIX}")
app.include_router(activities_router, prefix=f"{settings.API_V1_PREFIX}")
app.include_router(trash_router, prefix=f"{settings.API_V1_PREFIX}")
