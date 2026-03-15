"""
Agent Runner - Executes agents with dual-mode support (OpenAI + Groq fallback)
Integrates agent with FastAPI and handles conversation flow
"""

import asyncio
from typing import Optional, Dict, Any, AsyncIterator
from datetime import datetime

from openai import AsyncOpenAI
from agents import Agent, Runner, set_default_openai_client
from openai.types.responses import ResponseTextDeltaEvent

from src.config import settings
from src.utils.logging import get_logger
from src.agent.tools import (
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    escalate_to_human,
    send_response,
)
from src.agent.config import get_agent_instructions, AGENT_CONFIG, TOOL_SETTINGS
from src.agent.dual_mode_router import get_router

logger = get_logger(__name__)


# Initialize custom LLM client (Groq or OpenAI)
def _initialize_llm_client():
    """Initialize LLM client based on configuration."""
    if settings.USE_GROQ:
        logger.info(f"Initializing Groq client with model: {settings.AGENT_MODEL}")
        groq_client = AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.GROQ_API_KEY
        )
        set_default_openai_client(groq_client)
    else:
        logger.info(f"Initializing OpenAI client with model: {settings.AGENT_MODEL}")
        openai_client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY
        )
        set_default_openai_client(openai_client)


# Initialize client on module load
_initialize_llm_client()


class CustomerSuccessAgent:
    """
    Customer Success Agent wrapper for OpenAI Agents SDK.
    Handles agent initialization, execution, and streaming responses.
    """

    def __init__(self):
        """Initialize the agent with tools and configuration."""
        self.agent: Optional[Agent] = None
        self._initialize_agent()

    def _initialize_agent(self) -> None:
        """Create and configure the OpenAI agent."""
        try:
            # Get system instructions (default channel, will be customized per request)
            instructions = get_agent_instructions(channel="webform")

            # Create agent with all 5 tools
            self.agent = Agent(
                name=AGENT_CONFIG["name"],
                instructions=instructions,
                model=settings.AGENT_MODEL,  # From config (gpt-4o or gpt-4o-mini)
                tools=[
                    search_knowledge_base,
                    create_ticket,
                    get_customer_history,
                    escalate_to_human,
                    send_response,
                ],
            )

            logger.info(
                "Agent initialized successfully",
                extra={
                    "model": settings.AGENT_MODEL,
                    "tools_count": 5,
                    "agent_name": AGENT_CONFIG["name"],
                },
            )

        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}", exc_info=True)
            raise

    async def run(
        self,
        user_input: str,
        customer_id: int,
        conversation_id: int,
        channel: str = "webform",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run the agent with user input and return the complete response.

        Args:
            user_input: The customer's message
            customer_id: Customer's unique ID
            conversation_id: Conversation ID
            channel: Communication channel (email, whatsapp, webform)
            context: Additional context (sentiment, metadata, etc.)

        Returns:
            Dict with final_output, tool_calls, and metadata
        """
        start_time = datetime.utcnow()

        try:
            logger.info(
                "Running agent",
                extra={
                    "customer_id": customer_id,
                    "conversation_id": conversation_id,
                    "channel": channel,
                    "input_length": len(user_input),
                },
            )

            # Update agent instructions for specific channel
            channel_instructions = get_agent_instructions(channel=channel)
            self.agent.instructions = channel_instructions

            # Prepare context-aware input
            enhanced_input = self._prepare_input(
                user_input, customer_id, conversation_id, channel, context
            )

            # Run agent (non-streaming)
            result = await Runner.run(
                self.agent,
                input=enhanced_input,
            )

            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()

            logger.info(
                "Agent execution completed",
                extra={
                    "execution_time": execution_time,
                    "output_length": len(result.final_output) if result.final_output else 0,
                },
            )

            return {
                "final_output": result.final_output,
                "execution_time": execution_time,
                "channel": channel,
                "customer_id": customer_id,
                "conversation_id": conversation_id,
            }

        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
            return {
                "final_output": self._get_error_response(channel),
                "error": str(e),
                "execution_time": (datetime.utcnow() - start_time).total_seconds(),
            }

    async def run_streamed(
        self,
        user_input: str,
        customer_id: int,
        conversation_id: int,
        channel: str = "webform",
        context: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Run the agent with streaming responses for real-time feedback.

        Args:
            user_input: The customer's message
            customer_id: Customer's unique ID
            conversation_id: Conversation ID
            channel: Communication channel
            context: Additional context

        Yields:
            Dict with event type and data (text deltas, tool calls, etc.)
        """
        start_time = datetime.utcnow()

        try:
            logger.info(
                "Running agent (streaming)",
                extra={
                    "customer_id": customer_id,
                    "conversation_id": conversation_id,
                    "channel": channel,
                },
            )

            # Update agent instructions for specific channel
            channel_instructions = get_agent_instructions(channel=channel)
            self.agent.instructions = channel_instructions

            # Prepare context-aware input
            enhanced_input = self._prepare_input(
                user_input, customer_id, conversation_id, channel, context
            )

            # Run agent with streaming
            result = Runner.run_streamed(
                self.agent,
                input=enhanced_input,
            )

            # Stream events to caller
            async for event in result.stream_events():
                # Text deltas for real-time display
                if event.type == "raw_response_event":
                    if isinstance(event.data, ResponseTextDeltaEvent):
                        yield {
                            "type": "text_delta",
                            "data": event.data.delta,
                        }

                # Tool calls
                elif event.type == "run_item_stream_event":
                    if event.item.type == "tool_call_item":
                        yield {
                            "type": "tool_call",
                            "data": {
                                "tool_name": event.item.name,
                                "tool_id": event.item.id,
                            },
                        }
                    elif event.item.type == "tool_call_output_item":
                        yield {
                            "type": "tool_output",
                            "data": {
                                "output": event.item.output,
                            },
                        }

            # Final result
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            yield {
                "type": "final",
                "data": {
                    "final_output": result.final_output,
                    "execution_time": execution_time,
                },
            }

            logger.info(
                "Agent streaming completed",
                extra={"execution_time": execution_time},
            )

        except Exception as e:
            logger.error(f"Agent streaming failed: {e}", exc_info=True)
            yield {
                "type": "error",
                "data": {
                    "error": str(e),
                    "fallback_response": self._get_error_response(channel),
                },
            }

    def _prepare_input(
        self,
        user_input: str,
        customer_id: int,
        conversation_id: int,
        channel: str,
        context: Optional[Dict[str, Any]],
    ) -> str:
        """
        Prepare enhanced input with context for the agent.

        Args:
            user_input: Raw customer message
            customer_id: Customer ID
            conversation_id: Conversation ID
            channel: Communication channel
            context: Additional context

        Returns:
            Enhanced input string with metadata
        """
        # Build context string
        context_parts = [
            f"[CONTEXT]",
            f"Customer ID: {customer_id}",
            f"Conversation ID: {conversation_id}",
            f"Channel: {channel.upper()}",
        ]

        # Add sentiment if available
        if context and "sentiment" in context:
            context_parts.append(f"Sentiment: {context['sentiment']}")

        # Add any other metadata
        if context and "metadata" in context:
            for key, value in context["metadata"].items():
                context_parts.append(f"{key}: {value}")

        context_parts.append("[/CONTEXT]\n")

        # Combine context with user input
        enhanced_input = "\n".join(context_parts) + f"\nCustomer Message:\n{user_input}"

        return enhanced_input

    def _get_error_response(self, channel: str) -> str:
        """
        Get channel-appropriate error response.

        Args:
            channel: Communication channel

        Returns:
            Error message formatted for the channel
        """
        base_message = (
            "I apologize, but I'm experiencing technical difficulties at the moment. "
            "Your message has been recorded, and our support team will respond shortly."
        )

        if channel == "email":
            return (
                f"{base_message}\n\n"
                f"Best regards,\n"
                f"Custora AI Customer Success Team\n"
                f"support@custoraai.com"
            )
        elif channel == "whatsapp":
            return f"{base_message}\n\n- Custora AI Support 🚀"
        else:  # webform
            return (
                f"{base_message}\n\n"
                f"If this is urgent, please email us at support@custoraai.com.\n"
                f"- Custora AI Support"
            )


# Global agent instance (singleton)
_agent_instance: Optional[CustomerSuccessAgent] = None


def get_agent() -> CustomerSuccessAgent:
    """
    Get or create the global agent instance.

    Returns:
        CustomerSuccessAgent instance
    """
    global _agent_instance

    if _agent_instance is None:
        _agent_instance = CustomerSuccessAgent()

    return _agent_instance


def process_customer_message(
    user_input: str,
    customer_id: int,
    conversation_id: int,
    channel: str = "webform",
    context: Optional[Dict[str, Any]] = None,
    streaming: bool = False,
):
    """
    Process a customer message through the dual-mode agent router.

    Args:
        user_input: Customer's message
        customer_id: Customer ID
        conversation_id: Conversation ID
        channel: Communication channel
        context: Additional context
        streaming: Whether to use streaming responses

    Returns:
        Agent response (coroutine for non-streaming, async iterator for streaming)
    """
    router = get_router()

    # Convert IDs to strings for UUID compatibility
    customer_id_str = str(customer_id)
    conversation_id_str = str(conversation_id)

    if streaming:
        # Return the async generator directly
        return router.run_streamed(
            user_input=user_input,
            customer_id=customer_id_str,
            conversation_id=conversation_id_str,
            channel=channel,
            context=context,
        )
    else:
        # Return the coroutine
        return router.run(
            user_input=user_input,
            customer_id=customer_id_str,
            conversation_id=conversation_id_str,
            channel=channel,
            context=context,
        )
