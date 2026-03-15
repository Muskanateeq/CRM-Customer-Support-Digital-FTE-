"""
Base LLM Provider Interface

Abstract base class for all LLM providers.
Ensures consistent interface across Gemini, OpenAI, and future providers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncIterator


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate chat completion with function calling support.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: List of tool/function definitions
            stream: Whether to stream the response

        Returns:
            OpenAI-compatible response format:
            {
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": 1677652288,
                "model": "gpt-4o",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! How can I help you?",
                        "tool_calls": [...]  # Optional
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "total_tokens": 30
                }
            }
        """
        pass

    @abstractmethod
    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]]
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Generate streaming chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: List of tool/function definitions

        Yields:
            OpenAI-compatible streaming chunks
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name being used"""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name (e.g., 'gemini', 'openai')"""
        pass
