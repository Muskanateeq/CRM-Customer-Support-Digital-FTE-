# Backend Tests

This directory contains automated tests for the TaskNest backend API.

## Test Structure

- `conftest.py` - Pytest fixtures and configuration
- `test_auth_api.py` - Authentication endpoint tests
- `test_tasks_api.py` - Task CRUD endpoint tests
- `test_tags_api.py` - Tag endpoint tests
- `test_task_service.py` - Business logic tests

## Running Tests

```bash
# Install test dependencies
cd backend
uv sync

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_tasks_api.py

# Run specific test
uv run pytest tests/test_tasks_api.py::TestTaskCreation::test_create_basic_task
```

## Test Coverage

- ✅ Task CRUD operations
- ✅ Recurring task auto-generation
- ✅ Search and filter functionality
- ✅ User data isolation
- ✅ Tag management
- ✅ Authentication requirements
- ✅ Service layer business logic
