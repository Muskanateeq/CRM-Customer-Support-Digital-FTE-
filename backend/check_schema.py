import asyncio
from src.database.client import get_db_connection

async def check_schema():
    async with get_db_connection() as conn:
        # Check messages table schema
        result = await conn.fetch("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_name = 'messages'
            ORDER BY ordinal_position
        """)

        print("=== MESSAGES TABLE SCHEMA ===")
        for row in result:
            print(f"{row['column_name']}: {row['data_type']} ({row['udt_name']})")

        # Check a sample message
        sample = await conn.fetchrow("""
            SELECT id, conversation_id, role, content, created_at
            FROM messages
            ORDER BY created_at DESC
            LIMIT 1
        """)

        print("\n=== SAMPLE MESSAGE ===")
        if sample:
            print(f"ID: {sample['id']} (type: {type(sample['id'])})")
            print(f"Conversation ID: {sample['conversation_id']} (type: {type(sample['conversation_id'])})")
            print(f"Role: {sample['role']}")
            print(f"Content: {sample['content'][:50]}...")
        else:
            print("No messages found")

if __name__ == "__main__":
    asyncio.run(check_schema())
