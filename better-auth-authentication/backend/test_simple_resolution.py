"""
Simple test to verify task name resolution works
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.mcp.tools import execute_tool
from src.services.task_service import TaskService
from src.models.task import TaskCreate
from src.database import get_session


async def test_simple():
    """Test task name resolution directly"""
    print("="*60)
    print("Testing Task Name Resolution")
    print("="*60)

    async for session in get_session():
        try:
            test_user = "simple_test_user"

            # Create test task
            print("\n1. Creating task 'Build Hackathon'...")
            task = await TaskService.create_task(
                user_id=test_user,
                task_data=TaskCreate(
                    title="Build Hackathon",
                    priority="high"
                ),
                session=session
            )
            print(f"   Created task ID: {task.id}")

            # Test with task NAME (not numeric ID)
            print("\n2. Calling complete_task with task_id='hackathon'...")
            result = await execute_tool(
                tool_name="complete_task",
                arguments={"task_id": "hackathon", "completed": True},
                user_id=test_user,
                session=session
            )

            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message')}")

            # Verify
            print("\n3. Verifying task is completed...")
            updated = await TaskService.get_task_by_id(task.id, test_user, session)
            print(f"   Task completed: {updated.completed}")

            if updated.completed:
                print("\n" + "="*60)
                print("SUCCESS! Task name resolution works!")
                print("="*60)
            else:
                print("\nFAILED!")

            # Cleanup
            await TaskService.delete_task(task.id, test_user, session)

        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()

        break


if __name__ == "__main__":
    asyncio.run(test_simple())
