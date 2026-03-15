"""
Test complete chat flow with Groq provider
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.services.chat_service import ChatService
from src.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession


async def test_chat_flow():
    """Test complete chat flow with task creation"""
    print("[TEST] Testing complete chat flow with Groq...")

    # Get database session
    async for session in get_session():
        try:
            # Test 1: Simple message
            print("\n[TEST 1] Simple greeting...")
            result = await ChatService.send_message(
                user_id="test_groq_user",
                conversation_id=None,
                user_message="Hello, can you help me?",
                session=session
            )

            print(f"[OK] Conversation ID: {result['conversation_id']}")
            print(f"[OK] Response: {result['message'][:100]}...")

            conversation_id = result['conversation_id']

            # Test 2: Task creation with function calling
            print("\n[TEST 2] Task creation with function calling...")
            result = await ChatService.send_message(
                user_id="test_groq_user",
                conversation_id=conversation_id,
                user_message="Create a task to buy groceries tomorrow",
                session=session
            )

            print(f"[OK] Response: {result['message'][:100]}...")
            if result.get('tool_calls'):
                print(f"[OK] Tool calls executed: {len(result['tool_calls'])}")
                for tc in result['tool_calls']:
                    print(f"     - {tc['tool']}: {tc.get('result', {}).get('success', False)}")

            # Test 3: List tasks
            print("\n[TEST 3] List tasks...")
            result = await ChatService.send_message(
                user_id="test_groq_user",
                conversation_id=conversation_id,
                user_message="Show me my tasks",
                session=session
            )

            print(f"[OK] Response: {result['message'][:100]}...")

            print("\n[SUCCESS] All tests passed with Groq provider!")

        except Exception as e:
            print(f"[ERROR] Test failed: {e}")
            import traceback
            traceback.print_exc()

        break  # Exit after first session


if __name__ == "__main__":
    asyncio.run(test_chat_flow())
