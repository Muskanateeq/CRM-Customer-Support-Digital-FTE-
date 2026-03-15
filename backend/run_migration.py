"""
Run Better Auth Database Migration

This script creates the necessary tables for Better Auth authentication.
"""

import asyncio
import asyncpg
import os
from pathlib import Path


async def run_migration():
    """Run the Better Auth database migration."""

    # Get database URL from environment
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://***REMOVED***:***REMOVED***@***REMOVED***/neondb?sslmode=require"
    )

    print("Connecting to database...")

    # Connect to database
    conn = await asyncpg.connect(database_url)

    try:
        # Read migration file
        migration_file = Path(__file__).parent / "migrations" / "001_better_auth_schema.sql"

        print(f"Reading migration file: {migration_file}")

        with open(migration_file, "r") as f:
            sql = f.read()

        print("Running migration...")

        # Execute migration
        await conn.execute(sql)

        print("Migration completed successfully!")

        # Verify tables were created
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('user', 'session', 'account', 'verification')
            ORDER BY table_name
        """)

        print("\nCreated tables:")
        for table in tables:
            print(f"  - {table['table_name']}")

    except Exception as e:
        print(f"Migration failed: {e}")
        raise

    finally:
        await conn.close()
        print("\nDatabase connection closed.")


if __name__ == "__main__":
    asyncio.run(run_migration())
