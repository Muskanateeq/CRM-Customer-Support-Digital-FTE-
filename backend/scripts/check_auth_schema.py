"""
Check and display Better Auth database schema
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

async def check_schema():
    """Check current account table schema"""
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))

    try:
        print("\n" + "="*70)
        print("CURRENT ACCOUNT TABLE SCHEMA")
        print("="*70)

        # Get account table columns
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'account'
            ORDER BY ordinal_position;
        """)

        if not columns:
            print("❌ Account table does not exist!")
            return

        print(f"\nFound {len(columns)} columns:\n")
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f"DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  • {col['column_name']:<25} {col['data_type']:<20} {nullable:<10} {default}")

        print("\n" + "="*70)
        print("CHECKING FOR MISSING COLUMNS")
        print("="*70)

        # Required columns for Better Auth v1.0.0+
        required_columns = {
            'id', 'userId', 'accountId', 'providerId',
            'accessToken', 'refreshToken', 'idToken',
            'accessTokenExpiresAt', 'refreshTokenExpiresAt',
            'scope', 'password', 'createdAt', 'updatedAt'
        }

        existing_columns = {col['column_name'] for col in columns}
        missing_columns = required_columns - existing_columns

        if missing_columns:
            print(f"\n❌ Missing {len(missing_columns)} columns:")
            for col in sorted(missing_columns):
                print(f"  • {col}")
        else:
            print("\n✅ All required columns exist!")

        print("\n" + "="*70)

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_schema())
