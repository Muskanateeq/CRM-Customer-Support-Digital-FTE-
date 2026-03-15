"""
Wake up Neon database with retry logic
"""
import psycopg2
import os
import time
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("="*70)
print("Neon Database Wake-Up Script with Retry")
print("="*70)
print(f"\nHost: {os.getenv('POSTGRES_HOST')}")
print(f"Database: {os.getenv('POSTGRES_DB')}")
print()

max_retries = 5
retry_delay = 10  # seconds

for attempt in range(1, max_retries + 1):
    print(f"[Attempt {attempt}/{max_retries}] Connecting to database...")

    try:
        # Try to connect with longer timeout
        conn = psycopg2.connect(
            DATABASE_URL,
            connect_timeout=30  # 30 second timeout
        )

        print("[OK] Connected successfully!")

        # Run a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"[OK] Database version: {version[:80]}")

        # Check Better Auth tables
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('user', 'account', 'session', 'verification')
            ORDER BY table_name;
        """)
        auth_tables = cursor.fetchall()
        print(f"\n[OK] Better Auth tables found: {len(auth_tables)}/4")
        for table in auth_tables:
            print(f"  - {table[0]}")

        # Check account table columns
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'account'
            AND column_name IN ('scope', 'accessTokenExpiresAt', 'refreshTokenExpiresAt')
            ORDER BY column_name;
        """)
        new_columns = cursor.fetchall()
        print(f"\n[OK] OAuth columns in account table: {len(new_columns)}/3")
        for col in new_columns:
            print(f"  - {col[0]}")

        cursor.close()
        conn.close()

        print("\n" + "="*70)
        print("[SUCCESS] Database is awake and ready!")
        print("="*70)
        print("\nYou can now start the backend server:")
        print("  cd D:/Hackathon5/backend")
        print("  python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8001")
        print()
        exit(0)

    except Exception as e:
        print(f"[FAIL] Connection failed: {str(e)[:100]}")

        if attempt < max_retries:
            print(f"[INFO] Waiting {retry_delay} seconds before retry...")
            print(f"[INFO] Neon free tier databases auto-suspend and take 10-30s to wake up")
            time.sleep(retry_delay)
            print()
        else:
            print("\n" + "="*70)
            print("[ERROR] Failed to connect after all retries")
            print("="*70)
            print("\nPossible solutions:")
            print("  1. Check Neon dashboard: https://console.neon.tech/")
            print("  2. Verify database is not suspended")
            print("  3. Check if there are any Neon service issues")
            print("  4. Try connecting from Neon SQL Editor in dashboard")
            print()
            exit(1)
