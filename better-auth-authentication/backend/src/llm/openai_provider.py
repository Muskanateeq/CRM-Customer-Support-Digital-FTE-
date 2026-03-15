"""
OpenAI Provider

Implementation of LLMProvider for OpenAI API.
Supports GPT-4o and other OpenAI models.
"""

import os
from typing import List, Dict, Any, AsyncIterator
from openai import AsyncOpenAI

from src.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider"""

    def __init__(self):
        """Initialize OpenAI provider with API key and model"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = AsyncOpenAI(api_key=api_key)
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o")

    def get_model_name(self) -> str:
        """Get the model name being used"""
        return self.model_name

    def get_provider_name(self) -> str:
        """Get the provider name"""
        return "openai"

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate chat completion using OpenAI API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: List of tool/function definitions
            stream: Whether to stream the response (not used in non-streaming)

        Returns:
            OpenAI-compatible response format (native format)
        """
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

        # Call OpenAI API
        response = await self.client.chat.completions.create(**params)

        # Convert to dict (OpenAI SDK returns Pydantic models)
        return response.model_dump()

    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]]
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Generate streaming chat completion using OpenAI API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: List of tool/function definitions

        Yields:
            OpenAI-compatible streaming chunks (native format)
        """
        # Build request parameters
        params = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048,
            "stream": True,
        }

        # Add tools if provided
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"

        # Call OpenAI API with streaming
        stream = await self.client.chat.completions.create(**params)

        # Yield chunks
        async for chunk in stream:
            yield chunk.model_dump()
