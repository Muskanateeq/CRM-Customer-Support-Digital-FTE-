"""
Run Complete OAuth Migration for Better Auth

This script adds ALL missing OAuth columns to the account table:
- scope (TEXT)
- accessTokenExpiresAt (TIMESTAMP)
- refreshTokenExpiresAt (TIMESTAMP)
"""

import asyncio
import asyncpg
import os
from pathlib import Path


async def run_migration():
    """Run the complete OAuth migration."""

    # Get database URL from environment
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://***REMOVED***:***REMOVED***@***REMOVED***/neondb?sslmode=require"
    )

    print("=" * 70)
    print("Running Complete OAuth Migration for Better Auth")
    print("=" * 70)
    print("\nConnecting to database...")

    # Connect to database
    conn = await asyncpg.connect(database_url)

    try:
        # Read migration file
        migration_file = Path(__file__).parent / "migrations" / "002_fix_better_auth_account_table.sql"

        print(f"Reading migration file: {migration_file}")

        with open(migration_file, "r", encoding="utf-8") as f:
            sql = f.read()

        print("\nRunning migration...")
        print("Adding columns:")
        print("  - scope (TEXT)")
        print("  - accessTokenExpiresAt (TIMESTAMP)")
        print("  - refreshTokenExpiresAt (TIMESTAMP)")

        # Execute migration
        await conn.execute(sql)

        print("\n[OK] Migration completed successfully!")

        # Verify all columns were added
        print("\nVerifying schema...")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'account'
            AND column_name IN ('scope', 'accessTokenExpiresAt', 'refreshTokenExpiresAt')
            ORDER BY column_name
        """)

        if len(columns) == 3:
            print("\n[OK] All OAuth columns verified:")
            for col in columns:
                print(f"   - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        else:
            print(f"\n[WARN] Expected 3 columns, found {len(columns)}")
            for col in columns:
                print(f"   - {col['column_name']}: {col['data_type']}")

        # Show complete account table schema
        print("\n" + "=" * 70)
        print("Complete Account Table Schema:")
        print("=" * 70)
        all_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'account'
            ORDER BY ordinal_position
        """)

        for col in all_columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            print(f"  {col['column_name']:<30} {col['data_type']:<20} {nullable}")

        print("=" * 70)

    except Exception as e:
        print(f"\n[FAIL] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise

    finally:
        await conn.close()
        print("\nDatabase connection closed.")


if __name__ == "__main__":
    asyncio.run(run_migration())
