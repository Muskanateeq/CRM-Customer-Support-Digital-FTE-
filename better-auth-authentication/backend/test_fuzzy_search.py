"""
Test the improved task search with fuzzy matching
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.services.task_service import TaskService
from src.models.task import TaskCreate
from src.mcp.tools import execute_tool
from src.database import get_session


async def test_fuzzy_search():
    """Test fuzzy search with various inputs"""
    print("="*60)
    print("Testing Improved Task Search")
    print("="*60)

    async for session in get_session():
        try:
            test_user = "fuzzy_test_user"

            # Step 1: Create test tasks
            print("\n[STEP 1] Creating test tasks...")
            task1 = await TaskService.create_task(
                user_id=test_user,
                task_data=TaskCreate(
                    title="Build Hackathon Project",
                    description="Complete Phase 3 of hackathon",
                    priority="high"
                ),
                session=session
            )
            print(f"  Created: '{task1.title}' (ID: {task1.id})")

            task2 = await TaskService.create_task(
                user_id=test_user,
                task_data=TaskCreate(
                    title="Buy Groceries",
                    priority="medium"
                ),
                session=session
            )
            print(f"  Created: '{task2.title}' (ID: {task2.id})")

            # Step 2: Test various search queries
            test_cases = [
                ("build hackathon task", "Should find 'Build Hackathon Project'"),
                ("hackathon task ko complete kardo", "Should find 'Build Hackathon Project'"),
                ("the hackathon", "Should find 'Build Hackathon Project'"),
                ("groceries", "Should find 'Buy Groceries'"),
                ("buy groceries task", "Should find 'Buy Groceries'"),
            ]

            print("\n[STEP 2] Testing fuzzy search...")
            for query, expected in test_cases:
                print(f"\n  Query: '{query}'")
                print(f"  Expected: {expected}")

                try:
                    result = await execute_tool(
                        tool_name="complete_task",
                        arguments={"task_id": query, "completed": True},
                        user_id=test_user,
                        session=session
                    )

                    if result.get("success"):
                        task_title = result["task"]["title"]
                        print(f"  Result: SUCCESS - Found '{task_title}'")
                    else:
                        print(f"  Result: FAILED - {result.get('error')}")

                except Exception as e:
                    print(f"  Result: ERROR - {str(e)}")

            # Step 3: Test non-existent task
            print("\n[STEP 3] Testing non-existent task...")
            try:
                result = await execute_tool(
                    tool_name="complete_task",
                    arguments={"task_id": "xyz task that does not exist", "completed": True},
                    user_id=test_user,
                    session=session
                )
                print(f"  Result: {result.get('error', 'Unknown error')}")
            except ValueError as e:
                print(f"  Result: {str(e)}")

            # Cleanup
            print("\n[CLEANUP] Deleting test tasks...")
            await TaskService.delete_task(task1.id, test_user, session)
            await TaskService.delete_task(task2.id, test_user, session)
            print("  Cleanup complete")

            print("\n" + "="*60)
            print("Test Complete!")
            print("="*60)

        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()

        break


if __name__ == "__main__":
    asyncio.run(test_fuzzy_search())
