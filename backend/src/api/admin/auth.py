"""
Admin Authentication API
Handles admin user login, logout, and session management
"""

from fastapi import APIRouter, HTTPException, Depends, Response, Cookie
from pydantic import BaseModel, EmailStr
from typing import Optional
import bcrypt
import jwt
from datetime import datetime, timedelta
import os

from src.database.client import get_db_connection
from src.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/admin/auth", tags=["admin-auth"])

# JWT Configuration
JWT_SECRET = os.getenv("BETTER_AUTH_SECRET", "your-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


class AdminLoginRequest(BaseModel):
    """Admin login request"""
    email: EmailStr
    password: str


class AdminLoginResponse(BaseModel):
    """Admin login response"""
    success: bool
    message: str
    admin: Optional[dict] = None
    token: Optional[str] = None


class AdminUserResponse(BaseModel):
    """Admin user info response"""
    id: str
    email: str
    name: str
    role: str


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def create_admin_token(admin_id: str, email: str) -> str:
    """Create JWT token for admin user"""
    payload = {
        "admin_id": admin_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_admin_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Admin token expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid admin token")
        return None


async def get_current_admin(admin_token: Optional[str] = Cookie(None)):
    """Dependency to get current authenticated admin"""
    if not admin_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = verify_admin_token(admin_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Get admin from database
    async with get_db_connection() as conn:
        admin = await conn.fetchrow(
            """
            SELECT id, email, name, role, is_active
            FROM admin_users
            WHERE id = $1 AND is_active = true
            """,
            payload["admin_id"]
        )
        
        if not admin:
            raise HTTPException(status_code=401, detail="Admin user not found")
        
        return dict(admin)


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest, response: Response):
    """
    Admin login endpoint
    
    Returns JWT token in cookie and response body
    """
    try:
        async with get_db_connection() as conn:
            # Get admin user by email
            admin = await conn.fetchrow(
                """
                SELECT id, email, password_hash, name, role, is_active
                FROM admin_users
                WHERE email = $1
                """,
                request.email
            )
            
            if not admin:
                logger.warning(f"Admin login failed: user not found - {request.email}")
                raise HTTPException(status_code=401, detail="Invalid email or password")
            
            if not admin['is_active']:
                logger.warning(f"Admin login failed: account disabled - {request.email}")
                raise HTTPException(status_code=401, detail="Account is disabled")
            
            # Verify password
            if not verify_password(request.password, admin['password_hash']):
                logger.warning(f"Admin login failed: wrong password - {request.email}")
                raise HTTPException(status_code=401, detail="Invalid email or password")
            
            # Create JWT token
            token = create_admin_token(str(admin['id']), admin['email'])
            
            # Update last login timestamp
            await conn.execute(
                """
                UPDATE admin_users
                SET last_login_at = NOW()
                WHERE id = $1
                """,
                admin['id']
            )
            
            # Set cookie
            response.set_cookie(
                key="admin_token",
                value=token,
                httponly=True,
                max_age=JWT_EXPIRATION_HOURS * 3600,
                samesite="lax"
            )
            
            logger.info(f"Admin login successful: {request.email}")
            
            return AdminLoginResponse(
                success=True,
                message="Login successful",
                admin={
                    "id": str(admin['id']),
                    "email": admin['email'],
                    "name": admin['name'],
                    "role": admin['role']
                },
                token=token
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/logout")
async def admin_logout(response: Response):
    """
    Admin logout endpoint
    
    Clears authentication cookie
    """
    response.delete_cookie(key="admin_token")
    return {"success": True, "message": "Logged out successfully"}


@router.get("/me", response_model=AdminUserResponse)
async def get_current_admin_user(admin: dict = Depends(get_current_admin)):
    """
    Get current authenticated admin user
    
    Requires valid admin token
    """
    return AdminUserResponse(
        id=str(admin['id']),
        email=admin['email'],
        name=admin['name'],
        role=admin['role']
    )
