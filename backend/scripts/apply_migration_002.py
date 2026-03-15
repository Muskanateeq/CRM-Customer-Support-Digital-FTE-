"""
Apply Migration 002: Fix Better Auth Account Table
Adds missing columns for Google OAuth support
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import asyncpg
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def apply_migration():
    """Apply migration 002 to fix account table"""

    # Read migration file
    migration_file = Path(__file__).parent.parent / "migrations" / "002_fix_better_auth_account_table.sql"

    if not migration_file.exists():
        print(f"[ERROR] Migration file not found: {migration_file}")
        return False

    with open(migration_file, 'r', encoding='utf-8') as f:
        migration_sql = f.read()

    print("\n" + "="*70)
    print("APPLYING MIGRATION 002: Fix Better Auth Account Table")
    print("="*70)
    print(f"\nMigration file: {migration_file.name}")
    print(f"Database: {os.getenv('POSTGRES_HOST')}/{os.getenv('POSTGRES_DB')}")

    # Connect to database
    try:
        conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
        print("\n[OK] Connected to database")
    except Exception as e:
        print(f"\n[ERROR] Failed to connect to database: {e}")
        return False

    try:
        # Execute migration
        print("\n[INFO] Executing migration SQL...")
        await conn.execute(migration_sql)
        print("[OK] Migration executed successfully!")

        # Verify columns were added
        print("\n[INFO] Verifying schema changes...")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'account'
            AND column_name IN ('scope', 'accessTokenExpiresAt', 'refreshTokenExpiresAt')
            ORDER BY column_name;
        """)

        if len(columns) == 3:
            print(f"\n[OK] All 3 columns added successfully:\n")
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                print(f"  - {col['column_name']:<30} {col['data_type']:<20} {nullable}")

            print("\n" + "="*70)
            print("[SUCCESS] MIGRATION COMPLETE!")
            print("="*70)
            print("\n[INFO] Google OAuth should now work!")
            print("\nNext steps:")
            print("  1. Restart your frontend server (npm run dev)")
            print("  2. Try Google login again")
            print("  3. Check for any errors\n")
            return True
        else:
            print(f"\n[WARN] Expected 3 columns, found {len(columns)}")
            return False

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        return False
    finally:
        await conn.close()

if __name__ == "__main__":
    success = asyncio.run(apply_migration())
    sys.exit(0 if success else 1)
