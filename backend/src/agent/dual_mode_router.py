"""
Dual Mode Agent Router - Orchestrates between OpenAI and Groq agents
Provides automatic fallback from OpenAI to Groq for resilience
"""

from typing import Optional, Dict, Any, AsyncIterator, Union
from datetime import datetime

from openai import AsyncOpenAI
from agents import Agent, Runner, set_default_openai_client
from openai.types.responses import ResponseTextDeltaEvent

from src.config import settings
from src.utils.logging import get_logger
from src.agent.smart_agent import SmartAgent
from src.agent.tools import (
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    escalate_to_human,
    send_response,
)
from src.agent.config import get_agent_instructions, AGENT_CONFIG

logger = get_logger(__name__)


class DualModeAgentRouter:
    """
    Router that manages dual-mode agent execution.
    Primary: OpenAI with full tools support
    Fallback: Groq with full tools support
    """

    def __init__(self):
        """Initialize both OpenAI and SmartAgent."""
        self.openai_agent: Optional[Agent] = None
        self.smart_agent: Optional[SmartAgent] = None

        # Initialize OpenAI agent if not using Groq as primary
        if not settings.USE_GROQ:
            try:
                # Initialize OpenAI client
                openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                set_default_openai_client(openai_client)

                # Get system instructions
                instructions = get_agent_instructions(channel="webform")

                # Create agent with all 5 tools
                self.openai_agent = Agent(
                    name=AGENT_CONFIG["name"],
                    instructions=instructions,
                    model=settings.AGENT_MODEL,
                    tools=[
                        search_knowledge_base,
                        create_ticket,
                        get_customer_history,
                        escalate_to_human,
                        send_response,
                    ],
                )
                logger.info("OpenAI agent initialized as primary")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI agent: {e}")

        # Always initialize SmartAgent as fallback (classification-based, no tool calling)
        try:
            self.smart_agent = SmartAgent()
            logger.info("SmartAgent initialized as fallback (classification-based)")
        except Exception as e:
            logger.warning(f"Failed to initialize SmartAgent: {e}")

    async def run(
        self,
        user_input: str,
        customer_id: str,
        conversation_id: str,
        channel: str = "webform",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run agent with automatic fallback.

        Args:
            user_input: Customer's message
            customer_id: Customer ID (UUID)
            conversation_id: Conversation ID (UUID)
            channel: Communication channel
            context: Additional context

        Returns:
            Dict with final_output, execution metadata, and mode used
        """
        start_time = datetime.utcnow()

        # Try OpenAI first (if available and not using Groq as primary)
        if self.openai_agent and not settings.USE_GROQ:
            try:
                logger.info(
                    f"Attempting OpenAI agent [cid: {conversation_id[:8]}]"
                )

                # Update agent instructions for specific channel
                channel_instructions = get_agent_instructions(channel=channel)
                self.openai_agent.instructions = channel_instructions

                # Prepare context-aware input
                enhanced_input = self._prepare_input(
                    user_input, customer_id, conversation_id, channel, context
                )

                # Run agent (non-streaming)
                result = await Runner.run(
                    self.openai_agent,
                    input=enhanced_input,
                )

                # Calculate execution time
                execution_time = (datetime.utcnow() - start_time).total_seconds()

                logger.info(
                    f"OpenAI agent succeeded [cid: {conversation_id[:8]}]"
                )

                return {
                    "final_output": result.final_output,
                    "execution_time": execution_time,
                    "channel": channel,
                    "customer_id": customer_id,
                    "conversation_id": conversation_id,
                    "mode": "openai"
                }

            except Exception as e:
                logger.warning(
                    f"OpenAI agent failed: {e} - Falling back to Groq [cid: {conversation_id[:8]}]"
                )

        # Fallback to SmartAgent (or use as primary if USE_GROQ=true)
        if self.smart_agent:
            try:
                mode_type = "primary" if settings.USE_GROQ else "fallback"
                logger.info(
                    f"Using SmartAgent ({mode_type}) [cid: {conversation_id[:8]}]"
                )
                result = await self.smart_agent.run(
                    user_input=user_input,
                    customer_id=customer_id,
                    conversation_id=conversation_id,
                    channel=channel,
                    context=context,
                )
                logger.info(
                    f"SmartAgent succeeded [cid: {conversation_id[:8]}]"
                )
                return result

            except Exception as e:
                logger.error(
                    f"SmartAgent failed: {e} [cid: {conversation_id[:8]}]",
                    exc_info=True,
                )

        # Both agents failed
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        logger.error(
            f"All agents failed [cid: {conversation_id[:8]}]"
        )
        return {
            "final_output": self._get_error_response(channel),
            "error": "All agent modes failed",
            "execution_time": execution_time,
            "mode": "none",
        }

    async def run_streamed(
        self,
        user_input: str,
        customer_id: str,
        conversation_id: str,
        channel: str = "webform",
        context: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Run agent with streaming and automatic fallback.

        Args:
            user_input: Customer's message
            customer_id: Customer ID (UUID)
            conversation_id: Conversation ID (UUID)
            channel: Communication channel
            context: Additional context

        Yields:
            Dict with event type and data
        """
        # Try OpenAI first (if available and not using Groq as primary)
        if self.openai_agent and not settings.USE_GROQ:
            try:
                logger.info(
                    f"Attempting OpenAI agent (streaming) [cid: {conversation_id[:8]}]"
                )

                # Yield mode indicator
                yield {
                    "type": "mode",
                    "data": {"mode": "openai", "status": "primary"},
                }

                # Update agent instructions for specific channel
                channel_instructions = get_agent_instructions(channel=channel)
                self.openai_agent.instructions = channel_instructions

                # Prepare context-aware input
                enhanced_input = self._prepare_input(
                    user_input, customer_id, conversation_id, channel, context
                )

                # Run agent with streaming
                result = Runner.run_streamed(
                    self.openai_agent,
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
                start_time = datetime.utcnow()
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                yield {
                    "type": "final",
                    "data": {
                        "final_output": result.final_output,
                        "execution_time": execution_time,
                    },
                }

                logger.info(
                    f"OpenAI agent streaming succeeded [cid: {conversation_id[:8]}]"
                )
                return

            except Exception as e:
                logger.warning(
                    f"OpenAI agent streaming failed: {e} - Falling back to SmartAgent [cid: {conversation_id[:8]}]"
                )

                # Yield fallback indicator
                yield {
                    "type": "mode",
                    "data": {
                        "mode": "groq",
                        "status": "fallback",
                        "reason": str(e),
                    },
                }

        # Fallback to SmartAgent (or use as primary if USE_GROQ=true)
        if self.smart_agent:
            try:
                mode_type = "primary" if settings.USE_GROQ else "fallback"
                logger.info(
                    f"Using SmartAgent (streaming, {mode_type}) [cid: {conversation_id[:8]}]"
                )

                # Yield mode indicator (only if not already yielded above)
                if settings.USE_GROQ or not self.openai_agent:
                    logger.info(f"Yielding mode event: groq/{mode_type} [cid: {conversation_id[:8]}]")
                    yield {
                        "type": "mode",
                        "data": {"mode": "groq", "status": mode_type},
                    }

                # Use SmartAgent streaming
                logger.info(f"Using SmartAgent with classification-based approach [cid: {conversation_id[:8]}]")

                async for event in self.smart_agent.run_streamed(
                    user_input=user_input,
                    customer_id=customer_id,
                    conversation_id=conversation_id,
                    channel=channel,
                    context=context,
                ):
                    yield event

                logger.info(
                    f"SmartAgent succeeded [cid: {conversation_id[:8]}]"
                )
                return

            except Exception as e:
                logger.error(
                    f"SmartAgent failed: {e} [cid: {conversation_id[:8]}]",
                    exc_info=True,
                )

                # Provide user-friendly error message
                error_text = (
                    "I apologize for the inconvenience. I'm experiencing technical difficulties at the moment. "
                    "Please try again, or contact our support team directly at support@custora.com for immediate assistance."
                )

                yield {
                    "type": "text_delta",
                    "data": error_text,
                }

                yield {
                    "type": "final",
                    "data": {
                        "final_output": error_text,
                        "execution_time": 0,
                    },
                }
                return

    def _prepare_input(
        self,
        user_input: str,
        customer_id: str,
        conversation_id: str,
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


# Global router instance (singleton)
_router_instance: Optional[DualModeAgentRouter] = None


def get_router() -> DualModeAgentRouter:
    """
    Get or create the global router instance.

    Returns:
        DualModeAgentRouter instance
    """
    global _router_instance

    # Force recreation on every call during development to avoid caching issues
    if _router_instance is None:
        _router_instance = DualModeAgentRouter()
        logger.info("Created new DualModeAgentRouter instance")

    return _router_instance
