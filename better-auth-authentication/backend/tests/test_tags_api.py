"""
Tag API Tests

Tests for tag CRUD operations and task-tag associations.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.models.tag import Tag
from src.api.deps import get_current_user_id


@pytest.fixture
def mock_auth(test_user: User):
    """Mock authentication dependency"""
    async def override_get_current_user_id():
        return test_user.id

    return override_get_current_user_id


class TestTagCreation:
    """Test tag creation endpoint"""

    @pytest.mark.asyncio
    async def test_create_tag(
        self, client: AsyncClient, test_user: User, mock_auth
    ):
        """Test creating a new tag"""
        from src.main import app
        app.dependency_overrides[get_current_user_id] = mock_auth

        response = await client.post(
            "/api/v1/tags",
            json={"name": "Work"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Work"
        assert data["user_id"] == test_user.id
        assert "id" in data

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_create_duplicate_tag(
        self, client: AsyncClient, test_user: User, test_tag: Tag, mock_auth
    ):
        """Test creating duplicate tag (should fail)"""
        from src.main import app
        app.dependency_overrides[get_current_user_id] = mock_auth

        response = await client.post(
            "/api/v1/tags",
            json={"name": test_tag.name}
        )

        # Should return 400 (Bad Request) for duplicate
        assert response.status_code == 400

        app.dependency_overrides.clear()


class TestTagRetrieval:
    """Test tag retrieval endpoints"""

    @pytest.mark.asyncio
    async def test_list_tags(
        self, client: AsyncClient, test_user: User, test_tag: Tag, mock_auth
    ):
        """Test listing all user tags"""
        from src.main import app
        app.dependency_overrides[get_current_user_id] = mock_auth

        response = await client.get("/api/v1/tags")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(tag["name"] == test_tag.name for tag in data)

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_list_tags_empty(
        self, client: AsyncClient, test_user: User, mock_auth
    ):
        """Test listing tags when user has none"""
        from src.main import app
        app.dependency_overrides[get_current_user_id] = mock_auth

        response = await client.get("/api/v1/tags")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        app.dependency_overrides.clear()


class TestTagDeletion:
    """Test tag deletion endpoint"""

    @pytest.mark.asyncio
    async def test_delete_tag(
        self, client: AsyncClient, test_user: User, test_tag: Tag, mock_auth
    ):
        """Test deleting a tag"""
        from src.main import app
        app.dependency_overrides[get_current_user_id] = mock_auth

        response = await client.delete(f"/api/v1/tags/{test_tag.id}")

        assert response.status_code == 204

        # Verify tag is deleted
        list_response = await client.get("/api/v1/tags")
        tags = list_response.json()
        assert not any(tag["id"] == test_tag.id for tag in tags)

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_tag(
        self, client: AsyncClient, test_user: User, mock_auth
    ):
        """Test deleting non-existent tag"""
        from src.main import app
        app.dependency_overrides[get_current_user_id] = mock_auth

        response = await client.delete("/api/v1/tags/99999")

        assert response.status_code == 404

        app.dependency_overrides.clear()


class TestTagDataIsolation:
    """Test tag data isolation between users"""

    @pytest.mark.asyncio
    async def test_user_cannot_delete_other_user_tag(
        self, client: AsyncClient, test_user: User, test_user_2: User,
        test_session: AsyncSession
    ):
        """Test that users cannot delete other users' tags"""
        from src.main import app

        # Create tag for user 1
        tag_user_1 = Tag(
            user_id=test_user.id,
            name="User 1 Tag",
        )
        test_session.add(tag_user_1)
        await test_session.commit()
        await test_session.refresh(tag_user_1)

        # Try to delete as user 2
        async def mock_auth_user_2():
            return test_user_2.id

        app.dependency_overrides[get_current_user_id] = mock_auth_user_2

        response = await client.delete(f"/api/v1/tags/{tag_user_1.id}")

        # Should return 404 (not found) because tag doesn't belong to user 2
        assert response.status_code == 404

        app.dependency_overrides.clear()
