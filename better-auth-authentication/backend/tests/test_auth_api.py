"""
Authentication API Tests

Tests for authentication endpoints and JWT verification.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User


class TestAuthEndpoints:
    """Test authentication endpoints"""

    @pytest.mark.asyncio
    async def test_get_current_user(
        self, client: AsyncClient, test_user: User
    ):
        """Test getting current user profile"""
        from src.main import app
        from src.api.deps import get_current_user_id

        # Mock authentication
        async def mock_auth():
            return test_user.id

        app.dependency_overrides[get_current_user_id] = mock_auth

        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
        assert "created_at" in data
        assert "updated_at" in data

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_current_user_not_found(
        self, client: AsyncClient
    ):
        """Test getting current user when user doesn't exist"""
        from src.main import app
        from src.api.deps import get_current_user_id

        # Mock authentication with non-existent user
        async def mock_auth():
            return "non-existent-user-id"

        app.dependency_overrides[get_current_user_id] = mock_auth

        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_auth_health_check(self, client: AsyncClient):
        """Test authentication system health check"""
        response = await client.get("/api/v1/auth/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["auth_provider"] == "Better Auth"
        assert data["jwt_verification"] == "JWKS"


class TestAuthenticationRequired:
    """Test that endpoints require authentication"""

    @pytest.mark.asyncio
    async def test_tasks_endpoint_requires_auth(self, client: AsyncClient):
        """Test that tasks endpoint requires authentication"""
        # Try to access without auth header
        response = await client.get("/api/v1/tasks")

        # Should return 403 (Forbidden) or 401 (Unauthorized)
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_create_task_requires_auth(self, client: AsyncClient):
        """Test that creating task requires authentication"""
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task", "priority": "medium"}
        )

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_tags_endpoint_requires_auth(self, client: AsyncClient):
        """Test that tags endpoint requires authentication"""
        response = await client.get("/api/v1/tags")

        assert response.status_code in [401, 403]
