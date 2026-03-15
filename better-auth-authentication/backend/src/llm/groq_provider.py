"""
Groq Provider

Implementation of LLMProvider for Groq API.
Supports Llama 3.3 70B Versatile (default, FREE) and other Groq models.
Uses OpenAI-compatible API format.
"""

import time
from typing import List, Dict, Any, AsyncIterator
from openai import AsyncOpenAI

from src.llm.base import LLMProvider
from src.config import settings


class GroqProvider(LLMProvider):
    """Groq LLM provider using OpenAI-compatible API"""

    def __init__(self):
        """Initialize Groq provider with API key and model"""
        api_key = settings.GROQ_API_KEY
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        # Initialize OpenAI client with Groq base URL
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.model_name = settings.GROQ_MODEL

    def get_model_name(self) -> str:
        """Get the model name being used"""
        return self.model_name

    def get_provider_name(self) -> str:
        """Get the provider name"""
        return "groq"

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate chat completion using Groq API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: List of tool/function definitions (OpenAI format)
            stream: Whether to stream the response (not used in non-streaming)

        Returns:
            OpenAI-compatible response format
        """
        import logging
        logger = logging.getLogger(__name__)

        # Build request parameters
        params = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048,
        }

        # Add tools if provided
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
            logger.info(f"[GroqProvider] Sending {len(tools)} tools to Groq")
            logger.info(f"[GroqProvider] Tool names: {[t['function']['name'] for t in tools]}")

        logger.info(f"[GroqProvider] Sending {len(messages)} messages to Groq")
        logger.info(f"[GroqProvider] Message roles: {[m['role'] for m in messages]}")

        # Call Groq API
        response = await self.client.chat.completions.create(**params)

        # Convert to dict format (OpenAI response is already compatible)
        return {
            "id": response.id,
            "object": response.object,
            "created": response.created,
            "model": response.model,
            "choices": [
                {
                    "index": choice.index,
                    "message": {
                        "role": choice.message.role,
                        "content": choice.message.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": tc.type,
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in (choice.message.tool_calls or [])
                        ] if choice.message.tool_calls else None
                    },
                    "finish_reason": choice.finish_reason
                }
                for choice in response.choices
            ],
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }

    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]]
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Generate streaming chat completion using Groq API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: List of tool/function definitions

        Yields:
            OpenAI-compatible streaming chunks
        """
        import logging
        logger = logging.getLogger(__name__)

        # Build request parameters
        params = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048,
            "stream": True
        }

        # Add tools if provided
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"

        logger.info(f"[GroqProvider] Starting stream with {len(messages)} messages")

        # Stream response
        stream = await self.client.chat.completions.create(**params)

        async for chunk in stream:
            # Convert chunk to dict format
            delta_dict = {
                "role": chunk.choices[0].delta.role if hasattr(chunk.choices[0].delta, 'role') else None,
                "content": chunk.choices[0].delta.content if hasattr(chunk.choices[0].delta, 'content') else None,
            }

            # Handle tool calls in delta
            if hasattr(chunk.choices[0].delta, 'tool_calls') and chunk.choices[0].delta.tool_calls:
                delta_dict["tool_calls"] = [
                    {
                        "id": tc.id if hasattr(tc, 'id') else None,
                        "type": tc.type if hasattr(tc, 'type') else "function",
                        "function": {
                            "name": tc.function.name if hasattr(tc.function, 'name') else None,
                            "arguments": tc.function.arguments if hasattr(tc.function, 'arguments') else None
                        }
                    }
                    for tc in chunk.choices[0].delta.tool_calls
                ]

            yield {
                "id": chunk.id,
                "object": chunk.object,
                "created": chunk.created,
                "model": chunk.model,
                "choices": [
                    {
                        "index": chunk.choices[0].index,
                        "delta": delta_dict,
                        "finish_reason": chunk.choices[0].finish_reason
                    }
                ]
            }
