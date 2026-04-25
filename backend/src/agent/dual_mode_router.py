"""
Dual Mode Agent Router - Orchestrates between OpenAI and Groq agents
Provides automatic fallback from OpenAI to Groq for resilience
"""

from typing import Optional, Dict, Any, AsyncIterator
from datetime import datetime

from src.config import settings
from src.utils.logging import get_logger
from src.agent.smart_agent import SmartAgent
from src.agent.groq_agent import GroqAgentWithTools

logger = get_logger(__name__)


class DualModeAgentRouter:
    """
    Router that manages dual-mode agent execution.
    Primary: OpenAI with full tools support
    Fallback: Groq with full tools support
    """

    def __init__(self):
        """Initialize GroqAgent and SmartAgent."""
        self.groq_agent: Optional[GroqAgentWithTools] = None
        self.smart_agent: Optional[SmartAgent] = None

        # Initialize GroqAgent if using Groq and API key is available
        if settings.USE_GROQ and settings.GROQ_API_KEY:
            try:
                self.groq_agent = GroqAgentWithTools()
                logger.info("GroqAgentWithTools initialized as primary")
            except Exception as e:
                logger.warning(f"Failed to initialize GroqAgent: {e}")

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

        # Try GroqAgent first (if available and using Groq as primary)
        if self.groq_agent and settings.USE_GROQ:
            try:
                logger.info(
                    f"Attempting GroqAgent [cid: {conversation_id[:8]}]"
                )

                # Run Groq agent (non-streaming)
                result = await self.groq_agent.run(
                    user_input=user_input,
                    customer_id=customer_id,
                    conversation_id=conversation_id,
                    channel=channel,
                    context=context,
                )

                # Calculate execution time
                execution_time = (datetime.utcnow() - start_time).total_seconds()

                logger.info(
                    f"GroqAgent succeeded [cid: {conversation_id[:8]}]"
                )

                return {
                    "final_output": result.get("final_output", ""),
                    "execution_time": execution_time,
                    "channel": channel,
                    "customer_id": customer_id,
                    "conversation_id": conversation_id,
                    "mode": "groq"
                }

            except Exception as e:
                logger.warning(
                    f"GroqAgent failed: {e} - Falling back to SmartAgent [cid: {conversation_id[:8]}]"
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
        # Try GroqAgent first (if available and using Groq as primary)
        if self.groq_agent and settings.USE_GROQ:
            try:
                logger.info(
                    f"Attempting GroqAgent (streaming) [cid: {conversation_id[:8]}]"
                )

                # Yield mode indicator
                yield {
                    "type": "mode",
                    "data": {"mode": "groq", "status": "primary"},
                }

                # Use GroqAgent streaming
                async for event in self.groq_agent.run_streamed(
                    user_input=user_input,
                    customer_id=customer_id,
                    conversation_id=conversation_id,
                    channel=channel,
                    context=context,
                ):
                    yield event

                logger.info(
                    f"GroqAgent streaming succeeded [cid: {conversation_id[:8]}]"
                )
                return

            except Exception as e:
                logger.warning(
                    f"GroqAgent streaming failed: {e} - Falling back to SmartAgent [cid: {conversation_id[:8]}]"
                )

                # Yield fallback indicator
                yield {
                    "type": "mode",
                    "data": {
                        "mode": "smart",
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
                if not settings.USE_GROQ or not self.groq_agent:
                    logger.info(f"Yielding mode event: smart/{mode_type} [cid: {conversation_id[:8]}]")
                    yield {
                        "type": "mode",
                        "data": {"mode": "smart", "status": mode_type},
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
