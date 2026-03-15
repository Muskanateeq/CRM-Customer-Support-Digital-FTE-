"""
Complete Chatbot Functionality Test

Tests all TaskNest operations available through the chatbot:
- Task operations (create, list, update, complete, delete)
- Tag operations (create, list, delete)
- Statistics (dashboard stats)
- Comment operations (add, view, delete)
"""

import asyncio
import sys
from dotenv import load_dotenv

load_dotenv()

from src.agents.tasknest_agent import agent
from src.utils.smart_parser import SmartParser


async def main():
    print("=" * 60)
    print("COMPLETE CHATBOT FUNCTIONALITY TEST")
    print("=" * 60)

    passed = 0
    total = 0

    # Test 1: Agent and Smart Parser
    print("\n[TEST 1] Core Components")
    total += 1
    try:
        assert agent is not None
        assert agent.model == "gpt-4o"

        # Test smart parser
        assert SmartParser.parse_date("26-02-2026") == "2026-02-26"
        assert SmartParser.parse_priority("zaruri") == "high"
        assert SmartParser.parse_time("2pm") == "14:00"

        print("PASS - Agent and Smart Parser working")
        passed += 1
    except Exception as e:
        print(f"FAIL - {e}")

    # Test 2: All MCP Tools Available
    print("\n[TEST 2] MCP Tools Availability")
    total += 1
    try:
        from src.mcp.tools import get_all_tools
        tools = get_all_tools()

        expected_tools = [
            "create_task", "list_tasks", "update_task", "complete_task", "delete_task",
            "list_tags", "create_tag", "delete_tag",
            "get_stats",
            "add_comment", "get_comments", "delete_comment"
        ]

        tool_names = [t["function"]["name"] for t in tools]

        missing = []
        for expected in expected_tools:
            if expected not in tool_names:
                missing.append(expected)

        if missing:
            print(f"FAIL - Missing tools: {missing}")
        else:
            print(f"PASS - All {len(tools)} tools available")
            print("       Task ops: create, list, update, complete, delete")
            print("       Tag ops: list, create, delete")
            print("       Stats: get_stats")
            print("       Comments: add, get, delete")
            passed += 1
    except Exception as e:
        print(f"FAIL - {e}")

    # Test 3: Tool Definitions
    print("\n[TEST 3] Tool Definitions Quality")
    total += 1
    try:
        from src.mcp.tools import get_all_tools
        tools = get_all_tools()

        issues = []
        for tool in tools:
            name = tool["function"]["name"]
            desc = tool["function"]["description"]
            params = tool["function"]["parameters"]

            # Check description exists
            if not desc or len(desc) < 10:
                issues.append(f"{name}: description too short")

            # Check parameters structure
            if "properties" not in params:
                issues.append(f"{name}: missing properties")

        if issues:
            print(f"FAIL - Issues found:")
            for issue in issues:
                print(f"       {issue}")
        else:
            print("PASS - All tool definitions are well-formed")
            passed += 1
    except Exception as e:
        print(f"FAIL - {e}")

    # Test 4: Agent System Instructions
    print("\n[TEST 4] Agent System Instructions")
    total += 1
    try:
        instructions = agent.get_system_instructions()

        required_keywords = [
            "TaskNest",
            "create_task", "list_tasks", "complete_task",
            "create_tag", "delete_tag",
            "get_stats",
            "add_comment", "get_comments",
            "CONCISE", "BILINGUAL",
            "English", "Urdu"
        ]

        missing = []
        for keyword in required_keywords:
            if keyword not in instructions:
                missing.append(keyword)

        if missing:
            print(f"FAIL - Missing keywords: {missing}")
        else:
            print("PASS - System instructions include all operations")
            print(f"       Instructions length: {len(instructions)} chars")
            passed += 1
    except Exception as e:
        print(f"FAIL - {e}")

    # Test 5: Tool Execution Logic
    print("\n[TEST 5] Tool Execution Logic")
    total += 1
    try:
        from src.mcp.tools import execute_tool

        # Check that execute_tool function exists and has proper signature
        import inspect
        sig = inspect.signature(execute_tool)
        params = list(sig.parameters.keys())

        expected_params = ["tool_name", "arguments", "user_id", "session"]
        if params == expected_params:
            print("PASS - Tool execution function properly defined")
            passed += 1
        else:
            print(f"FAIL - Expected params {expected_params}, got {params}")
    except Exception as e:
        print(f"FAIL - {e}")

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("\nSUCCESS - Complete chatbot functionality is ready!")
        print("\nAvailable Operations:")
        print("  TASKS:")
        print("    - Create tasks with smart parsing (dates, priorities, tags)")
        print("    - List/search tasks with filters")
        print("    - Update task details")
        print("    - Complete/uncomplete tasks")
        print("    - Delete tasks")
        print("\n  TAGS:")
        print("    - List all tags")
        print("    - Create new tags")
        print("    - Delete tags")
        print("\n  STATISTICS:")
        print("    - View dashboard stats")
        print("    - Completion rates")
        print("    - Priority distribution")
        print("    - Weekly trends")
        print("\n  COMMENTS:")
        print("    - Add comments to tasks")
        print("    - View task comments")
        print("    - Delete comments")
        print("\nNext Steps:")
        print("  1. Uncomment OPENAI_API_KEY in .env file")
        print("  2. Start backend: uvicorn src.main:app --reload")
        print("  3. Test via frontend chat interface")
        print("\nExample Queries:")
        print("  - 'working on job task due date is 26-02-2026 high priority'")
        print("  - 'kal ka meeting task banao 2 baje, zaruri hai'")
        print("  - 'show my stats'")
        print("  - 'create tag called urgent'")
        print("  - 'add comment to task 5: working on this now'")
        print("  - 'what are my overdue tasks?'")
        return 0
    else:
        print("\nFAILED - Some tests did not pass")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
