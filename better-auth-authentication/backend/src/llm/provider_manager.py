"""
Provider Manager

Factory pattern for LLM provider selection.
Automatically selects provider based on LLM_PROVIDER environment variable.
"""

import os
from typing import Optional

from src.llm.base import LLMProvider
from src.llm.groq_provider import GroqProvider
from src.llm.gemini_provider import GeminiProvider
from src.llm.openai_provider import OpenAIProvider


class ProviderManager:
    """Factory for creating LLM providers"""

    _instance: Optional[LLMProvider] = None

    @classmethod
    def get_provider(cls) -> LLMProvider:
        """
        Get the configured LLM provider.

        Returns:
            LLMProvider instance (Groq, Gemini, or OpenAI)

        Raises:
            ValueError: If provider is not configured or invalid

        Environment Variables:
            LLM_PROVIDER: "groq" (default), "gemini", or "openai"
            GROQ_API_KEY: Required if using Groq
            GOOGLE_API_KEY: Required if using Gemini
            OPENAI_API_KEY: Required if using OpenAI
        """
        # Return cached instance if exists
        if cls._instance is not None:
            return cls._instance

        # Get provider from environment
        provider_name = os.getenv("LLM_PROVIDER", "groq").lower()

        # Create provider instance
        if provider_name == "groq":
            cls._instance = GroqProvider()
        elif provider_name == "gemini":
            cls._instance = GeminiProvider()
        elif provider_name == "openai":
            cls._instance = OpenAIProvider()
        else:
            raise ValueError(
                f"Invalid LLM_PROVIDER: {provider_name}. "
                f"Must be 'groq', 'gemini', or 'openai'"
            )

        return cls._instance

    @classmethod
    def reset(cls):
        """Reset the cached provider instance (useful for testing)"""
        cls._instance = None
