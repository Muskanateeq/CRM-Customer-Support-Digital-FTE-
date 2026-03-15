"""
Google Gemini Provider

Implementation of LLMProvider for Google Gemini API.
Supports Gemini 2.5 Flash (default, FREE) and Gemini 2.5 Pro.
"""

import time
import json
from typing import List, Dict, Any, AsyncIterator
from google import genai
from google.genai import types

from src.llm.base import LLMProvider
from src.config import settings


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider"""

    def __init__(self):
        """Initialize Gemini provider with API key and model"""
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        self.client = genai.Client(api_key=api_key)
        self.model_name = settings.GEMINI_MODEL

    def get_model_name(self) -> str:
        """Get the model name being used"""
        return self.model_name

    def get_provider_name(self) -> str:
        """Get the provider name"""
        return "gemini"

    def _convert_tools_to_gemini_format(
        self,
        tools: List[Dict[str, Any]]
    ) -> List[types.Tool]:
        """
        Convert OpenAI tool format to Gemini format.

        OpenAI format:
        {
            "type": "function",
            "function": {
                "name": "create_task",
                "description": "Create a new task",
                "parameters": {...}
            }
        }

        Gemini format:
        Tool(function_declarations=[
            FunctionDeclaration(
                name="create_task",
                description="Create a new task",
                parameters={...}
            )
        ])
        """
        if not tools:
            return []

        function_declarations = []
        for tool in tools:
            if tool.get("type") == "function":
                func = tool["function"]
                function_declarations.append(
                    types.FunctionDeclaration(
                        name=func["name"],
                        description=func["description"],
                        parameters=func.get("parameters", {})
                    )
                )

        return [types.Tool(function_declarations=function_declarations)] if function_declarations else []

    def _convert_messages_to_gemini_format(
        self,
        messages: List[Dict[str, str]]
    ) -> List[types.Content]:
        """
        Convert OpenAI message format to Gemini format.

        OpenAI uses: system, user, assistant, function
        Gemini uses: user, model, tool
        """
        gemini_messages = []
        system_message = None

        for msg in messages:
            role = msg["role"]
            content = msg.get("content", "")

            if role == "system":
                system_message = content
            elif role == "user":
                # Create proper Content object with Part
                gemini_messages.append(
                    types.Content(
                        role="user",
                        parts=[types.Part(text=content)]
                    )
                )
            elif role == "assistant":
                # Handle assistant messages with tool_calls
                parts = []

                # Add text content if present
                if content:
                    parts.append(types.Part(text=content))

                # Add function calls if present
                if msg.get("tool_calls"):
                    for tool_call in msg["tool_calls"]:
                        func = tool_call["function"]
                        parts.append(
                            types.Part(
                                function_call=types.FunctionCall(
                                    name=func["name"],
                                    args=json.loads(func["arguments"])
                                )
                            )
                        )

                # Only add if we have parts
                if parts:
                    gemini_messages.append(
                        types.Content(
                            role="model",
                            parts=parts
                        )
                    )
            elif role == "function":
                # Convert function result to Gemini tool response format
                function_name = msg.get("name", "unknown")
                function_result = json.loads(content) if isinstance(content, str) else content

                gemini_messages.append(
                    types.Content(
                        role="tool",
                        parts=[
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=function_name,
                                    response=function_result
                                )
                            )
                        ]
                    )
                )

        # Prepend system message to first user message if exists
        if system_message and gemini_messages:
            first_msg = gemini_messages[0]
            if first_msg.role == "user":
                # Prepend system message to first user message
                first_msg.parts[0].text = f"{system_message}\n\n{first_msg.parts[0].text}"

        return gemini_messages

    def _convert_gemini_response_to_openai_format(
        self,
        response: Any,
        model_name: str
    ) -> Dict[str, Any]:
        """
        Convert Gemini response to OpenAI format for ChatKit compatibility.
        """
        # Extract content
        content = ""
        tool_calls = []

        if response.candidates:
            candidate = response.candidates[0]

            # Extract text content
            if candidate.content.parts:
                for part in candidate.content.parts:
                    if hasattr(part, 'text') and part.text:
                        content += part.text
                    elif hasattr(part, 'function_call'):
                        # Convert function call to OpenAI format
                        fc = part.function_call
                        tool_calls.append({
                            "id": f"call_{int(time.time())}",
                            "type": "function",
                            "function": {
                                "name": fc.name,
                                "arguments": json.dumps(dict(fc.args))
                            }
                        })

        # Build OpenAI-compatible response
        openai_response = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model_name,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content or None,
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            }
        }

        # Add tool_calls if present
        if tool_calls:
            openai_response["choices"][0]["message"]["tool_calls"] = tool_calls
            openai_response["choices"][0]["finish_reason"] = "tool_calls"

        return openai_response

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate chat completion using Gemini API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: List of tool/function definitions
            stream: Whether to stream the response (not used in non-streaming)

        Returns:
            OpenAI-compatible response format
        """
        # Convert formats
        gemini_messages = self._convert_messages_to_gemini_format(messages)
        gemini_tools = self._convert_tools_to_gemini_format(tools)

        # Build config with tools inside
        config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=2048,
            tools=gemini_tools if gemini_tools else None
        )

        # Generate response
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=gemini_messages,
            config=config
        )

        # Convert to OpenAI format
        return self._convert_gemini_response_to_openai_format(response, self.model_name)

    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]]
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Generate streaming chat completion using Gemini API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: List of tool/function definitions

        Yields:
            OpenAI-compatible streaming chunks
        """
        # Convert formats
        gemini_messages = self._convert_messages_to_gemini_format(messages)
        gemini_tools = self._convert_tools_to_gemini_format(tools)

        # Build config with tools inside
        config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=2048,
            tools=gemini_tools if gemini_tools else None
        )

        # Generate streaming response
        response_stream = self.client.models.generate_content_stream(
            model=self.model_name,
            contents=gemini_messages,
            config=config
        )

        # Stream chunks in OpenAI format
        async for chunk in response_stream:
            if hasattr(chunk, 'candidates') and chunk.candidates:
                candidate = chunk.candidates[0]
                if hasattr(candidate, 'content') and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            yield {
                                "id": f"chatcmpl-{int(time.time())}",
                                "object": "chat.completion.chunk",
                                "created": int(time.time()),
                                "model": self.model_name,
                                "choices": [{
                                    "index": 0,
                                    "delta": {
                                        "role": "assistant",
                                        "content": part.text
                                    },
                                    "finish_reason": None
                                }]
                            }

        # Send final chunk
        yield {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": self.model_name,
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }]
        }
