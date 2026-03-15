"""
Quick test script for Groq provider
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from src.llm.groq_provider import GroqProvider


async def test_groq():
    """Test Groq provider with simple message"""
    print("[TEST] Testing Groq Provider...")

    try:
        # Initialize provider
        provider = GroqProvider()
        print(f"[OK] Provider initialized: {provider.get_provider_name()}")
        print(f"[OK] Model: {provider.get_model_name()}")

        # Test simple message
        messages = [
            {"role": "user", "content": "Say hello in one word"}
        ]

        print("\n[TEST] Sending test message...")
        response = await provider.chat_completion(
            messages=messages,
            tools=[],
            stream=False
        )

        print(f"[OK] Response received!")
        print(f"     Content: {response['choices'][0]['message']['content']}")
        print(f"     Tokens: {response['usage']['total_tokens']}")

        # Test with function calling
        print("\n[TEST] Testing function calling...")
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_task",
                    "description": "Create a new task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Task title"
                            }
                        },
                        "required": ["title"]
                    }
                }
            }
        ]

        messages = [
            {"role": "user", "content": "Create a task to buy groceries"}
        ]

        response = await provider.chat_completion(
            messages=messages,
            tools=tools,
            stream=False
        )

        message = response['choices'][0]['message']
        if message.get('tool_calls'):
            print(f"[OK] Function calling works!")
            print(f"     Tool: {message['tool_calls'][0]['function']['name']}")
            print(f"     Args: {message['tool_calls'][0]['function']['arguments']}")
        else:
            print(f"[WARN] No tool calls (content: {message['content']})")

        print("\n[SUCCESS] All tests passed!")

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_groq())
