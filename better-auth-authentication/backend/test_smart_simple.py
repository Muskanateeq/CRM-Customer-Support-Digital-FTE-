"""
Simple Smart Chatbot Validation Test
Tests core functionality without Unicode characters
"""

import asyncio
import sys
from dotenv import load_dotenv

load_dotenv()

from src.agents.tasknest_agent import agent
from src.utils.smart_parser import SmartParser


async def main():
    print("=" * 60)
    print("SMART CHATBOT VALIDATION")
    print("=" * 60)

    passed = 0
    total = 0

    # Test 1: Agent initialization
    print("\n[TEST 1] Agent Initialization")
    total += 1
    try:
        assert agent is not None
        assert agent.model == "gpt-4o"
        instructions = agent.get_system_instructions()
        assert "TaskNest" in instructions
        print("PASS - Agent initialized with gpt-4o model")
        print(f"       System instructions: {len(instructions)} chars")
        passed += 1
    except Exception as e:
        print(f"FAIL - {e}")

    # Test 2: Date parsing
    print("\n[TEST 2] Smart Parser - Date Parsing")
    total += 1
    try:
        result1 = SmartParser.parse_date("26-02-2026")
        assert result1 == "2026-02-26", f"Expected 2026-02-26, got {result1}"

        result2 = SmartParser.parse_date("tomorrow")
        assert result2 is not None, "Tomorrow parsing failed"

        result3 = SmartParser.parse_date("kal")
        assert result3 is not None, "Urdu 'kal' parsing failed"

        print("PASS - Date parsing works (DD-MM-YYYY, tomorrow, kal)")
        passed += 1
    except Exception as e:
        print(f"FAIL - {e}")

    # Test 3: Priority parsing
    print("\n[TEST 3] Smart Parser - Priority Parsing")
    total += 1
    try:
        assert SmartParser.parse_priority("high") == "high"
        assert SmartParser.parse_priority("urgent") == "high"
        assert SmartParser.parse_priority("zaruri") == "high"
        assert SmartParser.parse_priority("medium") == "medium"
        assert SmartParser.parse_priority("low") == "low"
        print("PASS - Priority parsing works (English + Urdu)")
        passed += 1
    except Exception as e:
        print(f"FAIL - {e}")

    # Test 4: Time parsing
    print("\n[TEST 4] Smart Parser - Time Parsing")
    total += 1
    try:
        assert SmartParser.parse_time("2pm") == "14:00"
        assert SmartParser.parse_time("14:00") == "14:00"
        assert SmartParser.parse_time("2:30 PM") == "14:30"
        assert SmartParser.parse_time("2 baje") == "02:00"
        print("PASS - Time parsing works (12h, 24h, Urdu)")
        passed += 1
    except Exception as e:
        print(f"FAIL - {e}")

    # Test 5: Language detection
    print("\n[TEST 5] Smart Parser - Language Detection")
    total += 1
    try:
        assert SmartParser.detect_language("Create a task") == "english"
        assert SmartParser.detect_language("kal ka task banao") == "urdu"
        print("PASS - Language detection works")
        passed += 1
    except Exception as e:
        print(f"FAIL - {e}")

    # Test 6: MCP Tools
    print("\n[TEST 6] MCP Tools Availability")
    total += 1
    try:
        from src.mcp.tools import get_all_tools
        tools = get_all_tools()
        tool_names = [t["function"]["name"] for t in tools]

        expected = ["create_task", "list_tasks", "update_task", "complete_task", "delete_task"]
        for name in expected:
            assert name in tool_names, f"Missing tool: {name}"

        print(f"PASS - All {len(tools)} MCP tools available")
        passed += 1
    except Exception as e:
        print(f"FAIL - {e}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("\nSUCCESS - Smart chatbot is ready!")
        print("\nNext steps:")
        print("  1. Uncomment OPENAI_API_KEY in .env file")
        print("  2. Start backend: uvicorn src.main:app --reload")
        print("  3. Test via frontend chat interface")
        print("  4. Try: 'working on job task due date is 26-02-2026 high priority'")
        print("  5. Try: 'kal ka meeting task banao 2 baje, zaruri hai'")
        return 0
    else:
        print("\nFAILED - Some tests did not pass")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
