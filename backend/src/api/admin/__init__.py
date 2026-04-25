"""
Admin API Module
Combines authentication and ticket management routes
"""

from fastapi import APIRouter

from src.api.admin.auth import router as auth_router
from src.api.admin.tickets import router as tickets_router

# Create main admin router
router = APIRouter()

# Include sub-routers
router.include_router(auth_router)
router.include_router(tickets_router)

__all__ = ["router"]
