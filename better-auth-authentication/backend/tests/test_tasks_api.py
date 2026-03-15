"""
Task API Endpoint Tests

Tests for task CRUD operations, search, filter, sort, and recurring tasks.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, time

from src.models.task import Task
from src.models.user import User
from src.models.tag import Tag
from src.api.deps import get_current_user_id


@pytest.fixture
def mock_auth(test_user: User):
    """Mock authentication dependency"""
    async def override_get_current_user_id():
        return test_user.id

    return override_get_current_user_id


class TestTaskCreation:
    """Test task creation endpoint"""

    @pytest.mark.asyncio
    async def test_create_basic_task(
        self, client: AsyncClient, test_user: User, mock_auth
    ):
        """Test creating a basic task"""
        from src.main import app
        app.dependency_overrides[get_current_user_id] = mock_auth

        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "New Task",
                "description": "Task description",
                "priority": "high",
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["description"] == "Task description"
        assert data["priority"] == "high"
        assert data["completed"] is False
        assert "id" in data

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_create_task_with_due_date(
        self, client: AsyncClient, test_user: User, mock_auth
    ):
        """Test creating task with due date"""
        from src.main import app
        app.dependency_overrides[get_current_user_id] = mock_auth

        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Task with deadline",
                "priority": "medium",
                "due_date": "2026-12-31",
                "due_time": "14:00:00",
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["due_date"] == "2026-12-31"
        assert data["due_time"] == "14:00:00"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_create_recurring_task(
        self, client: AsyncClient, test_user: User, mock_auth
    ):
        """Test creating recurring task"""
        from src.main import app
        app.dependency_overrides[get_current_user_id] = mock_auth

        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Daily standup",
                "priority": "high",
                "due_date": "2026-02-08",
                "due_time": "09:00:00",
                "recurrence_pattern": {
                    "type": "daily",
                    "interval": 1,
                }
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["recurrence_pattern"]["type"] == "daily"
        assert data["recurrence_pattern"]["interval"] == 1

        app.dependency_overrides.clear()


class TestTaskRetrieval:
    """Test task retrieval endpoints"""

    @pytest.mark.asyncio
    async def test_list_tasks(
        self, client: AsyncClient, test_user: User, test_task: Task, mock_auth
    ):
        """Test listing all tasks"""
        from src.main import app
        app.dependency_overrides[get_current_user_id] = mock_auth

        response = await client.get("/api/v1/tasks")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["title"] == test_task.title

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_task_by_id(
        self, client: AsyncClient, test_user: User, test_task: Task, mock_auth
    ):
        """Test getting single task by ID"""
        from src.main import app
        app.dependency_overrides[get_current_user_id] = mock_auth

        response = await client.get(f"/api/v1/tasks/{test_task.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_task.id
        assert data["title"] == test_task.title

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_search_tasks(
        self, client: AsyncClient, test_user: User, test_task: Task, mock_auth
    ):
        """Test searching tasks by keyword"""
        from src.main import app
        app.dependency_overrides[get_current_user_id] = mock_auth

        response = await client.get("/api/v1/tasks?search=Test")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert "Test" in data[0]["title"]

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_filter_by_priority(
        self, client: AsyncClient, test_user: User, test_task: Task, mock_auth
    ):
        """Test filtering tasks by priority"""
        from src.main import app
        app.dependency_overrides[get_current_user_id] = mock_auth

        response = await client.get("/api/v1/tasks?priority=medium")

        assert response.status_code == 200
        data = response.json()
        for task in data:
            assert task["priority"] == "medium"

        app.dependency_overrides.clear()


class TestTaskUpdate:
    """Test task update endpoint"""

    @pytest.mark.asyncio
    async def test_update_task_title(
        self, client: AsyncClient, test_user: User, test_task: Task, mock_auth
    ):
        """Test updating task title"""
        from src.main import app
        app.dependency_overrides[get_current_user_id] = mock_auth

        response = await client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": "Updated Title"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_update_task_priority(
        self, client: AsyncClient, test_user: User, test_task: Task, mock_auth
    ):
        """Test updating task priority"""
        from src.main import app
        app.dependency_overrides[get_current_user_id] = mock_auth

        response = await client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"priority": "high"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "high"

        app.dependency_overrides.clear()


class TestTaskCompletion:
    """Test task completion toggle"""

    @pytest.mark.asyncio
    async def test_mark_task_complete(
        self, client: AsyncClient, test_user: User, test_task: Task, mock_auth
    ):
        """Test marking task as complete"""
        from src.main import app
        app.dependency_overrides[get_current_user_id] = mock_auth

        response = await client.patch(
            f"/api/v1/tasks/{test_task.id}/complete",
            json={"completed": True}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_recurring_task_creates_next_occurrence(
        self, client: AsyncClient, test_session: AsyncSession, test_user: User, mock_auth
    ):
        """Test that completing recurring task creates next occurrence"""
        from src.main import app
        from sqlmodel import select

        app.dependency_overrides[get_current_user_id] = mock_auth

        # Create recurring task
        create_response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Daily Task",
                "priority": "medium",
                "due_date": "2026-02-07",
                "due_time": "10:00:00",
                "recurrence_pattern": {
                    "type": "daily",
                    "interval": 1,
                }
            }
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Mark as complete
        complete_response = await client.patch(
            f"/api/v1/tasks/{task_id}/complete",
            json={"completed": True}
        )
        assert complete_response.status_code == 200

        # Check that new task was created
        result = await test_session.execute(
            select(Task).where(Task.user_id == test_user.id)
        )
        tasks = result.scalars().all()

        # Should have 2 tasks: completed one and new occurrence
        assert len(tasks) == 2

        # Find the new task (not completed)
        new_task = next((t for t in tasks if not t.completed), None)
        assert new_task is not None
        assert new_task.title == "Daily Task"
        assert new_task.due_date == date(2026, 2, 8)  # Next day

        app.dependency_overrides.clear()


class TestTaskDeletion:
    """Test task deletion endpoint"""

    @pytest.mark.asyncio
    async def test_delete_task(
        self, client: AsyncClient, test_user: User, test_task: Task, mock_auth
    ):
        """Test deleting a task"""
        from src.main import app
        app.dependency_overrides[get_current_user_id] = mock_auth

        response = await client.delete(f"/api/v1/tasks/{test_task.id}")

        assert response.status_code == 204

        # Verify task is deleted
        get_response = await client.get(f"/api/v1/tasks/{test_task.id}")
        assert get_response.status_code == 404

        app.dependency_overrides.clear()


class TestDataIsolation:
    """Test user data isolation"""

    @pytest.mark.asyncio
    async def test_user_cannot_access_other_user_tasks(
        self, client: AsyncClient, test_user: User, test_user_2: User,
        test_session: AsyncSession
    ):
        """Test that users can only access their own tasks"""
        from src.main import app
        from src.api.deps import get_current_user_id

        # Create task for user 1
        task_user_1 = Task(
            user_id=test_user.id,
            title="User 1 Task",
            priority="medium",
            completed=False,
        )
        test_session.add(task_user_1)
        await test_session.commit()
        await test_session.refresh(task_user_1)

        # Try to access as user 2
        async def mock_auth_user_2():
            return test_user_2.id

        app.dependency_overrides[get_current_user_id] = mock_auth_user_2

        response = await client.get(f"/api/v1/tasks/{task_user_1.id}")

        # Should return 404 (not found) because task doesn't belong to user 2
        assert response.status_code == 404

        app.dependency_overrides.clear()
