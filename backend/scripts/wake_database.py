"""
Wake up Neon database by making a simple connection
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("Attempting to wake up Neon database...")
print(f"Host: {os.getenv('POSTGRES_HOST')}")
print(f"Database: {os.getenv('POSTGRES_DB')}")
print()

try:
    # Simple connection to wake up the database
    print("[INFO] Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    print("[OK] Connected successfully!")

    # Run a simple query
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"[OK] Database version: {version[:80]}")

    # Check if our tables exist
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    print(f"\n[OK] Found {len(tables)} tables:")
    for table in tables:
        print(f"  - {table[0]}")

    cursor.close()
    conn.close()

    print("\n[SUCCESS] Database is awake and ready!")
    print("\nNow try starting the backend again.")

except Exception as e:
    print(f"\n[ERROR] Failed to connect: {e}")
    print("\nPossible issues:")
    print("  1. Database might be suspended - wait 30 seconds and try again")
    print("  2. Network connectivity issue")
    print("  3. Invalid credentials")
