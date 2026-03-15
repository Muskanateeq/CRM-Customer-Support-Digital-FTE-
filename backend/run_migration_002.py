"""
Run Migration to Add accessTokenExpiresAt Column

This script adds the missing accessTokenExpiresAt column to the account table.
"""

import asyncio
import asyncpg
import os
from pathlib import Path


async def run_migration():
    """Run the migration to add accessTokenExpiresAt column."""

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
        migration_file = Path(__file__).parent / "migrations" / "002_add_access_token_expires_at.sql"

        print(f"Reading migration file: {migration_file}")

        with open(migration_file, "r") as f:
            sql = f.read()

        print("Running migration...")

        # Execute migration
        await conn.execute(sql)

        print("Migration completed successfully!")

        # Verify column was added
        result = await conn.fetchrow("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'account'
            AND column_name = 'accessTokenExpiresAt'
        """)

        if result:
            print(f"\nVerified: Column '{result['column_name']}' added with type '{result['data_type']}'")
        else:
            print("\nWarning: Could not verify column was added")

    except Exception as e:
        print(f"Migration failed: {e}")
        raise

    finally:
        await conn.close()
        print("\nDatabase connection closed.")


if __name__ == "__main__":
    asyncio.run(run_migration())
