"""
Run database migration for admin portal
"""
import asyncio
import asyncpg
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

async def run_migration():
    """Run the admin portal schema migration"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("ERROR: DATABASE_URL not found in environment")
        return

    # Read migration file
    migration_file = Path(__file__).parent / "migrations" / "003_admin_portal_schema.sql"

    if not migration_file.exists():
        print(f"ERROR: Migration file not found: {migration_file}")
        return

    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()

    print(f"Running migration: {migration_file.name}")

    try:
        # Connect to database
        conn = await asyncpg.connect(database_url)

        # Run migration
        await conn.execute(sql)

        print("SUCCESS: Migration completed!")

        # Verify tables created
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('admin_users', 'ticket_responses', 'ticket_notes')
            ORDER BY table_name
        """)

        print("\nCreated tables:")
        for table in tables:
            print(f"  - {table['table_name']}")

        # Check if admin user was created
        admin_count = await conn.fetchval("SELECT COUNT(*) FROM admin_users")
        print(f"\nAdmin users: {admin_count}")

        if admin_count > 0:
            admin = await conn.fetchrow("SELECT email, name FROM admin_users LIMIT 1")
            print(f"  - {admin['name']} ({admin['email']})")
            print(f"\nDefault password: Admin@123")
            print(f"IMPORTANT: Change this password after first login!")

        await conn.close()

    except Exception as e:
        print(f"ERROR: Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_migration())
