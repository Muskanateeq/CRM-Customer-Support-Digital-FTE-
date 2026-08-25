"""Regression tests for Render startup configuration."""

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import pytest

from scripts import poll_emails
from src.api.main import app
from src.database import migrations


def test_backend_url_uses_explicit_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BACKEND_URL", "https://api.example.com/")
    monkeypatch.setenv("PORT", "10000")

    assert poll_emails.get_backend_url() == "https://api.example.com"


def test_backend_url_uses_render_port(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BACKEND_URL", raising=False)
    monkeypatch.setenv("PORT", "10000")

    assert poll_emails.get_backend_url() == "http://127.0.0.1:10000"


def test_root_endpoint_accepts_render_head_probe() -> None:
    root_route = next(route for route in app.routes if route.path == "/")

    assert {"GET", "HEAD"}.issubset(root_route.methods)


@pytest.mark.asyncio
async def test_channel_jobs_migration_is_applied(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    executed_sql = ""

    class FakeConnection:
        async def execute(self, sql: str) -> None:
            nonlocal executed_sql
            executed_sql = sql

    @asynccontextmanager
    async def fake_connection() -> AsyncIterator[Any]:
        yield FakeConnection()

    monkeypatch.setattr(migrations, "get_db_connection", fake_connection)

    await migrations.ensure_channel_jobs_schema()

    assert "CREATE TABLE IF NOT EXISTS channel_jobs" in executed_sql
