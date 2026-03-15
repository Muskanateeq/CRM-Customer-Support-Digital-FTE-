"""
Test tag_names support in create_task
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.services.chat_service import ChatService
from src.database import get_session


async def test_complex_task_creation():
    """Test creating task with complex request"""
    print("="*60)
    print("Testing Complex Task Creation with Tags")
    print("="*60)

    async for session in get_session():
        try:
            test_user = "complex_task_test_user"

            # Test 1: Simple task with tag names
            print("\n[TEST 1] Creating task with tag names...")
            result1 = await ChatService.send_message(
                user_id=test_user,
                conversation_id=None,
                user_message="Create a task: working on job, due date is 26-02-2026, high priority, tag is agentic ai engineer",
                session=session
            )

            print(f"Response: {result1['message']}")
            if result1.get('tool_calls'):
                for tc in result1['tool_calls']:
                    print(f"Tool: {tc['tool']}")
                    if tc.get('result', {}).get('success'):
                        task = tc['result']['task']
                        print(f"  Title: {task['title']}")
                        print(f"  Due Date: {task.get('due_date')}")
                        print(f"  Priority: {task['priority']}")
                        print(f"  Tags: {task.get('tags', [])}")
                        print("  SUCCESS!")
                    else:
                        print(f"  ERROR: {tc.get('error')}")

            # Test 2: Another complex request
            print("\n[TEST 2] Another complex task...")
            result2 = await ChatService.send_message(
                user_id=test_user,
                conversation_id=result1['conversation_id'],
                user_message="Add task: meeting tomorrow at 2pm, medium priority, tags work and urgent",
                session=session
            )

            print(f"Response: {result2['message']}")
            if result2.get('tool_calls'):
                for tc in result2['tool_calls']:
                    if tc.get('result', {}).get('success'):
                        task = tc['result']['task']
                        print(f"  Title: {task['title']}")
                        print(f"  Due Time: {task.get('due_time')}")
                        print(f"  Priority: {task['priority']}")
                        print(f"  Tags: {task.get('tags', [])}")
                        print("  SUCCESS!")

            print("\n" + "="*60)
            print("Test Complete!")
            print("="*60)

        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()

        break


if __name__ == "__main__":
    asyncio.run(test_complex_task_creation())
