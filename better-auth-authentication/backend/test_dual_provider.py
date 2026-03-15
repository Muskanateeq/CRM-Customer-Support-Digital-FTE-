"""
Test Dual Provider Support (Groq + OpenAI)

Tests that the agent correctly detects and uses the available LLM provider.
"""

import os
import sys
from dotenv import load_dotenv

# Test different scenarios
def test_provider_detection():
    print("=" * 60)
    print("DUAL PROVIDER SUPPORT TEST")
    print("=" * 60)

    # Save original env vars
    original_groq = os.environ.get("GROQ_API_KEY")
    original_openai = os.environ.get("OPENAI_API_KEY")
    original_pref = os.environ.get("PREFERRED_LLM_PROVIDER")

    test_results = []

    # Test 1: Only Groq key
    print("\n[TEST 1] Only Groq Key Set")
    os.environ["GROQ_API_KEY"] = "test_groq_key"
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.pop("PREFERRED_LLM_PROVIDER", None)

    try:
        # Need to reload module to test
        import importlib
        import src.agents.tasknest_agent as agent_module
        importlib.reload(agent_module)

        agent = agent_module.TaskNestAgent()

        if agent.provider == "groq" and agent.model == "llama-3.1-70b-versatile":
            print("PASS - Detected Groq provider")
            print(f"       Provider: {agent.provider}")
            print(f"       Model: {agent.model}")
            test_results.append(True)
        else:
            print(f"FAIL - Expected groq, got {agent.provider}")
            test_results.append(False)
    except Exception as e:
        print(f"FAIL - {e}")
        test_results.append(False)

    # Test 2: Only OpenAI key
    print("\n[TEST 2] Only OpenAI Key Set")
    os.environ.pop("GROQ_API_KEY", None)
    os.environ["OPENAI_API_KEY"] = "test_openai_key"
    os.environ.pop("PREFERRED_LLM_PROVIDER", None)

    try:
        importlib.reload(agent_module)
        agent = agent_module.TaskNestAgent()

        if agent.provider == "openai" and agent.model == "gpt-4o":
            print("PASS - Detected OpenAI provider")
            print(f"       Provider: {agent.provider}")
            print(f"       Model: {agent.model}")
            test_results.append(True)
        else:
            print(f"FAIL - Expected openai, got {agent.provider}")
            test_results.append(False)
    except Exception as e:
        print(f"FAIL - {e}")
        test_results.append(False)

    # Test 3: Both keys, default preference (groq)
    print("\n[TEST 3] Both Keys Set (Default Preference)")
    os.environ["GROQ_API_KEY"] = "test_groq_key"
    os.environ["OPENAI_API_KEY"] = "test_openai_key"
    os.environ.pop("PREFERRED_LLM_PROVIDER", None)

    try:
        importlib.reload(agent_module)
        agent = agent_module.TaskNestAgent()

        if agent.provider == "groq":
            print("PASS - Default preference is Groq (FREE)")
            print(f"       Provider: {agent.provider}")
            print(f"       Model: {agent.model}")
            test_results.append(True)
        else:
            print(f"FAIL - Expected groq as default, got {agent.provider}")
            test_results.append(False)
    except Exception as e:
        print(f"FAIL - {e}")
        test_results.append(False)

    # Test 4: Both keys, OpenAI preference
    print("\n[TEST 4] Both Keys Set (OpenAI Preference)")
    os.environ["GROQ_API_KEY"] = "test_groq_key"
    os.environ["OPENAI_API_KEY"] = "test_openai_key"
    os.environ["PREFERRED_LLM_PROVIDER"] = "openai"

    try:
        importlib.reload(agent_module)
        agent = agent_module.TaskNestAgent()

        if agent.provider == "openai":
            print("PASS - Preference honored (OpenAI)")
            print(f"       Provider: {agent.provider}")
            print(f"       Model: {agent.model}")
            test_results.append(True)
        else:
            print(f"FAIL - Expected openai, got {agent.provider}")
            test_results.append(False)
    except Exception as e:
        print(f"FAIL - {e}")
        test_results.append(False)

    # Test 5: No keys
    print("\n[TEST 5] No API Keys Set")
    os.environ.pop("GROQ_API_KEY", None)
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.pop("PREFERRED_LLM_PROVIDER", None)

    try:
        importlib.reload(agent_module)
        agent = agent_module.TaskNestAgent()
        print("FAIL - Should have raised error for missing keys")
        test_results.append(False)
    except ValueError as e:
        if "No LLM API key found" in str(e):
            print("PASS - Correctly raised error for missing keys")
            print(f"       Error message includes setup instructions")
            test_results.append(True)
        else:
            print(f"FAIL - Wrong error: {e}")
            test_results.append(False)
    except Exception as e:
        print(f"FAIL - Unexpected error: {e}")
        test_results.append(False)

    # Restore original env vars
    if original_groq:
        os.environ["GROQ_API_KEY"] = original_groq
    else:
        os.environ.pop("GROQ_API_KEY", None)

    if original_openai:
        os.environ["OPENAI_API_KEY"] = original_openai
    else:
        os.environ.pop("OPENAI_API_KEY", None)

    if original_pref:
        os.environ["PREFERRED_LLM_PROVIDER"] = original_pref
    else:
        os.environ.pop("PREFERRED_LLM_PROVIDER", None)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(test_results)
    total = len(test_results)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("\nSUCCESS - Dual provider support working correctly!")
        print("\nProvider Selection Logic:")
        print("  1. Only Groq key → Use Groq (FREE)")
        print("  2. Only OpenAI key → Use OpenAI (PAID)")
        print("  3. Both keys → Use PREFERRED_LLM_PROVIDER (default: groq)")
        print("  4. No keys → Error with setup instructions")
        print("\nTo Switch Providers:")
        print("  - Edit .env file")
        print("  - Uncomment/comment API keys")
        print("  - Restart server")
        print("  - No code changes needed!")
        return 0
    else:
        print("\nFAILED - Some tests did not pass")
        return 1


if __name__ == "__main__":
    sys.exit(test_provider_detection())
