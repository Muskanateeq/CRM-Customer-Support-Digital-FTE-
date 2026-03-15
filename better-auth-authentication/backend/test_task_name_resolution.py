"""
Test Task Name Resolution in Chatbot
Tests that the chatbot can handle task names instead of numeric IDs
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.services.chat_service import ChatService
from src.services.task_service import TaskService
from src.models.task import TaskCreate
from src.database import get_session


async def test_task_name_resolution():
    """Test that chatbot can complete tasks by name"""
    print("\n" + "="*60)
    print("Testing Task Name Resolution in Chatbot")
    print("="*60)

    async for session in get_session():
        try:
            test_user_id = "test_name_resolution_user"

            # Step 1: Create a test task
            print("\n[STEP 1] Creating test task 'Build Hackathon Project'...")
            task = await TaskService.create_task(
                user_id=test_user_id,
                task_data=TaskCreate(
                    title="Build Hackathon Project",
                    description="Complete the hackathon project for Phase 3",
                    priority="high"
                ),
                session=session
            )
            print(f"[OK] Task created with ID: {task.id}")
            print(f"     Title: {task.title}")
            print(f"     Completed: {task.completed}")

            # Step 2: Test chatbot with task NAME (not ID)
            print("\n[STEP 2] Testing chatbot: 'Complete the hackathon task'...")
            result = await ChatService.send_message(
                user_id=test_user_id,
                conversation_id=None,
                user_message="Complete the hackathon task",
                session=session
            )

            print(f"\n[OK] Chatbot Response:")
            print(f"     Message: {result['message']}")

            if result.get('tool_calls'):
                print(f"\n[OK] Tool Calls Executed: {len(result['tool_calls'])}")
                for tc in result['tool_calls']:
                    print(f"     - Tool: {tc['tool']}")
                    print(f"       Arguments: {tc.get('arguments', {})}")

                    # Check for errors
                    if tc.get('error'):
                        print(f"       ERROR: {tc.get('error')}")
                    else:
                        print(f"       Success: {tc.get('result', {}).get('success', False)}")
                        if tc.get('result', {}).get('task'):
                            task_result = tc['result']['task']
                            print(f"       Task Title: {task_result.get('title')}")
                            print(f"       Task Completed: {task_result.get('completed')}")

            # Step 3: Verify task is actually completed
            print("\n[STEP 3] Verifying task completion in database...")
            updated_task = await TaskService.get_task_by_id(task.id, test_user_id, session)
            print(f"[OK] Task Status:")
            print(f"     ID: {updated_task.id}")
            print(f"     Title: {updated_task.title}")
            print(f"     Completed: {updated_task.completed}")

            if updated_task.completed:
                print("\n" + "="*60)
                print("[SUCCESS] Task name resolution works correctly!")
                print("="*60)
            else:
                print("\n" + "="*60)
                print("[FAILED] Task was not marked as completed")
                print("="*60)

            # Step 4: Test with another task name variation
            print("\n[STEP 4] Creating another test task...")
            task2 = await TaskService.create_task(
                user_id=test_user_id,
                task_data=TaskCreate(
                    title="Write Documentation",
                    description="Document the chatbot features",
                    priority="medium"
                ),
                session=session
            )
            print(f"[OK] Task created with ID: {task2.id}")

            print("\n[STEP 5] Testing: 'Mark the documentation task as done'...")
            result2 = await ChatService.send_message(
                user_id=test_user_id,
                conversation_id=result['conversation_id'],
                user_message="Mark the documentation task as done",
                session=session
            )

            print(f"\n[OK] Chatbot Response:")
            print(f"     Message: {result2['message']}")

            if result2.get('tool_calls'):
                print(f"\n[OK] Tool Calls: {len(result2['tool_calls'])}")
                for tc in result2['tool_calls']:
                    print(f"     - {tc['tool']}: {tc.get('result', {}).get('success', False)}")

            # Verify
            updated_task2 = await TaskService.get_task_by_id(task2.id, test_user_id, session)
            if updated_task2.completed:
                print("\n[SUCCESS] Second test also passed!")
            else:
                print("\n[FAILED] Second test failed!")

            # Cleanup
            print("\n[CLEANUP] Deleting test tasks...")
            await TaskService.delete_task(task.id, test_user_id, session)
            await TaskService.delete_task(task2.id, test_user_id, session)
            print("[OK] Cleanup complete")

        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()

        break


if __name__ == "__main__":
    asyncio.run(test_task_name_resolution())
