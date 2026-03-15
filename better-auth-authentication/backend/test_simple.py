"""
Simple test for task creation
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.services.chat_service import ChatService
from src.database import get_session


async def test_simple():
    """Test simple task creation"""
    print("[TEST] Simple task creation test...")

    async for session in get_session():
        try:
            result = await ChatService.send_message(
                user_id="test_user_simple",
                conversation_id=None,
                user_message="Create a task to buy milk",
                session=session
            )

            print(f"[OK] Response: {result['message']}")
            if result.get('tool_calls'):
                print(f"[OK] Tools executed: {len(result['tool_calls'])}")
                for tc in result['tool_calls']:
                    print(f"     - {tc['tool']}: {tc.get('result', {})}")
            else:
                print("[WARN] No tools executed")

        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()

        break


if __name__ == "__main__":
    asyncio.run(test_simple())
