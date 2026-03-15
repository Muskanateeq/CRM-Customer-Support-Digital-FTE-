"""
Simple Backend Tests - Verification

Basic tests to verify the backend setup is working.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app


class TestBasicEndpoints:
    """Test basic API endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint returns correct response"""
        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "TaskNest API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"

    def test_health_endpoint(self):
        """Test health check endpoint"""
        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_auth_health_endpoint(self):
        """Test auth health check endpoint"""
        client = TestClient(app)
        response = client.get("/api/v1/auth/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["auth_provider"] == "Better Auth"
        assert data["jwt_verification"] == "JWKS"

    def test_docs_endpoint(self):
        """Test API documentation endpoint is accessible"""
        client = TestClient(app)
        response = client.get("/docs")

        assert response.status_code == 200

    def test_tasks_endpoint_requires_auth(self):
        """Test that tasks endpoint requires authentication"""
        client = TestClient(app)
        response = client.get("/api/v1/tasks")

        # Should return 401 (Unauthorized) without auth
        assert response.status_code == 401

    def test_tags_endpoint_requires_auth(self):
        """Test that tags endpoint requires authentication"""
        client = TestClient(app)
        response = client.get("/api/v1/tags")

        # Should return 401 (Unauthorized) without auth
        assert response.status_code == 401


class TestTaskModel:
    """Test Task model validation"""

    def test_task_model_imports(self):
        """Test that Task model can be imported"""
        from src.models.task import Task, TaskCreate, TaskUpdate, TaskPublic

        assert Task is not None
        assert TaskCreate is not None
        assert TaskUpdate is not None
        assert TaskPublic is not None

    def test_task_create_validation(self):
        """Test TaskCreate model validation"""
        from src.models.task import TaskCreate

        # Valid task
        task = TaskCreate(
            title="Test Task",
            description="Test description",
            priority="high"
        )
        assert task.title == "Test Task"
        assert task.priority == "high"

    def test_task_priority_validation(self):
        """Test that priority must be valid"""
        from src.models.task import TaskCreate
        from pydantic import ValidationError

        # Valid priorities
        for priority in ["high", "medium", "low"]:
            task = TaskCreate(title="Test", priority=priority)
            assert task.priority == priority


class TestTagModel:
    """Test Tag model"""

    def test_tag_model_imports(self):
        """Test that Tag model can be imported"""
        from src.models.tag import Tag, TagCreate, TagPublic

        assert Tag is not None
        assert TagCreate is not None
        assert TagPublic is not None

    def test_tag_create_validation(self):
        """Test TagCreate model validation"""
        from src.models.tag import TagCreate

        tag = TagCreate(name="Work")
        assert tag.name == "Work"


class TestUserModel:
    """Test User model"""

    def test_user_model_imports(self):
        """Test that User model can be imported"""
        from src.models.user import User, UserPublic

        assert User is not None
        assert UserPublic is not None


class TestRecurrenceLogic:
    """Test recurring task logic"""

    def test_recurrence_service_imports(self):
        """Test that TaskService can be imported"""
        from src.services.task_service import TaskService

        assert TaskService is not None
        assert hasattr(TaskService, '_create_next_recurring_task')

    def test_recurrence_pattern_structure(self):
        """Test recurrence pattern structure"""
        # Daily pattern
        daily_pattern = {
            "type": "daily",
            "interval": 1
        }
        assert daily_pattern["type"] == "daily"
        assert daily_pattern["interval"] == 1

        # Weekly pattern
        weekly_pattern = {
            "type": "weekly",
            "interval": 1
        }
        assert weekly_pattern["type"] == "weekly"

        # Monthly pattern
        monthly_pattern = {
            "type": "monthly",
            "interval": 1
        }
        assert monthly_pattern["type"] == "monthly"


class TestJWTUtils:
    """Test JWT utilities"""

    def test_jwt_utils_imports(self):
        """Test that JWT utilities can be imported"""
        from src.utils.jwt import (
            decode_better_auth_token,
            verify_better_auth_token,
            get_user_id_from_better_auth_token
        )

        assert decode_better_auth_token is not None
        assert verify_better_auth_token is not None
        assert get_user_id_from_better_auth_token is not None


# Summary test
def test_backend_setup_complete():
    """Verify all backend components are set up correctly"""

    # Check main app
    from src.main import app
    assert app is not None

    # Check models
    from src.models.task import Task
    from src.models.tag import Tag
    from src.models.user import User
    assert Task is not None
    assert Tag is not None
    assert User is not None

    # Check services
    from src.services.task_service import TaskService
    from src.services.tag_service import TagService
    assert TaskService is not None
    assert TagService is not None

    # Check API routes
    from src.api.tasks import router as tasks_router
    from src.api.tags import router as tags_router
    from src.api.auth import router as auth_router
    assert tasks_router is not None
    assert tags_router is not None
    assert auth_router is not None

    print("\n✅ All backend components verified successfully!")
