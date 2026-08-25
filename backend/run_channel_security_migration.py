"""Apply the durable channel security migration."""

import asyncio
import os
from pathlib import Path

import asyncpg
from dotenv import load_dotenv

load_dotenv()


async def main() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    migration = Path(__file__).parent / "migrations" / "004_channel_security_jobs.sql"
    connection = await asyncpg.connect(database_url)
    try:
        await connection.execute(migration.read_text(encoding="utf-8"))
        print("Applied 004_channel_security_jobs.sql")
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
