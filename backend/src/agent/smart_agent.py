"""
Smart Classification-Based Agent for Custora AI
No tool calling - uses classification + backend logic + response generation
"""

from typing import Dict, Any, Optional, AsyncIterator
from datetime import datetime

from src.utils.logging import get_logger
from src.agent.classifier import QueryClassifier
from src.agent.response_generator import ResponseGenerator

# Import database and service functions
from src.embeddings.vector_search import search_knowledge_base_semantic
from src.database.client import (
    create_ticket as db_create_ticket,
    get_conversation_history,
)

logger = get_logger(__name__)


class SmartAgent:
    """
    Smart agent that uses classification-based approach instead of tool calling.

    Workflow:
    1. Classify query into one of 3 scenarios
    2. Execute appropriate backend logic
    3. Generate scenario-specific response
    """

    def __init__(self):
        """Initialize classifier and response generator."""
        self.classifier = QueryClassifier()
        self.response_generator = ResponseGenerator()
        logger.info("SmartAgent initialized (classification-based, no tool calling)")

    async def run(
        self,
        user_input: str,
        customer_id: str,
        conversation_id: str,
        channel: str = "webform",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run smart agent with classification-based approach.

        Args:
            user_input: Customer's message
            customer_id: Customer ID (UUID)
            conversation_id: Conversation ID (UUID)
            channel: Communication channel
            context: Additional context

        Returns:
            Dict with final_output and execution metadata
        """
        start_time = datetime.utcnow()

        try:
            logger.info(f"SmartAgent processing query [cid: {conversation_id[:8]}]")

            # STEP 1: Classify the query
            classification = await self.classifier.classify(user_input, conversation_id)
            scenario = classification["scenario"]
            category = classification["category"]
            priority = classification["priority"]

            logger.info(f"Classified as {scenario} - {category} ({priority}) [cid: {conversation_id[:8]}]")

            # STEP 2: Execute scenario-specific logic
            kb_results = None
            ticket_id = None

            if scenario == "SCENARIO_1_ECOMMERCE":
                # Search knowledge base
                logger.info(f"Searching knowledge base [cid: {conversation_id[:8]}]")
                kb_results = await search_knowledge_base_semantic(
                    query=user_input,
                    limit=3
                )

                # Create tracking ticket with meaningful subject
                logger.info(f"Creating tracking ticket [cid: {conversation_id[:8]}]")

                # Generate subject from user query (first 100 chars)
                subject = user_input[:100].strip()
                if len(user_input) > 100:
                    subject += "..."

                ticket_id = await db_create_ticket(
                    customer_id=customer_id,
                    conversation_id=conversation_id,
                    category=category,
                    priority=priority,
                    source_channel=channel,
                    resolution_notes=subject  # Use query as subject
                )
                logger.info(f"Ticket created: {ticket_id} [cid: {conversation_id[:8]}]")

            elif scenario == "SCENARIO_2_OUT_OF_SCOPE":
                # No action needed - just generate redirect response
                logger.info(f"Out-of-scope query - no ticket created [cid: {conversation_id[:8]}]")
                pass

            elif scenario == "SCENARIO_3_ESCALATION":
                # Create escalation ticket with user query as subject
                logger.info(f"Creating escalation ticket [cid: {conversation_id[:8]}]")

                # Generate subject from user query (first 100 chars)
                subject = user_input[:100].strip()
                if len(user_input) > 100:
                    subject += "..."

                # Use classification reasoning for escalation_reason
                escalation_reason = classification.get('reasoning', 'Customer requires human support')

                ticket_id = await db_create_ticket(
                    customer_id=customer_id,
                    conversation_id=conversation_id,
                    category="general",  # Escalations go to general category
                    priority=priority,
                    source_channel=channel,
                    resolution_notes=subject,  # User query as subject
                    status="escalated",  # Set status to escalated
                    escalated=True  # Set escalated_at timestamp
                )
                logger.info(f"Escalation ticket created: {ticket_id} [cid: {conversation_id[:8]}]")

            # STEP 3: Generate response
            logger.info(f"Generating response [cid: {conversation_id[:8]}]")
            final_response = await self.response_generator.generate_response(
                scenario=scenario,
                user_query=user_input,
                conversation_id=conversation_id,
                channel=channel,
                kb_results=kb_results,
                ticket_id=ticket_id,
                classification=classification
            )

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            logger.info(f"SmartAgent completed in {execution_time:.2f}s [cid: {conversation_id[:8]}]")

            return {
                "final_output": final_response,
                "execution_time": execution_time,
                "channel": channel,
                "customer_id": customer_id,
                "conversation_id": conversation_id,
                "mode": "smart_agent",
                "scenario": scenario,
                "category": category,
                "priority": priority,
                "ticket_id": ticket_id
            }

        except Exception as e:
            logger.error(f"SmartAgent execution failed: {e}", exc_info=True)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return {
                "final_output": self._get_error_response(channel),
                "error": str(e),
                "execution_time": execution_time,
                "mode": "smart_agent"
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
        Run smart agent with streaming (simulated).

        Note: Since we're not using tool calling, we can't stream the LLM response directly.
        Instead, we'll run the full process and yield the result at the end.
        """
        try:
            logger.info(f"SmartAgent streaming mode [cid: {conversation_id[:8]}]")

            # Yield mode event
            yield {
                "type": "mode",
                "data": {
                    "mode": "groq",
                    "status": "primary"
                }
            }

            # Run the full agent
            result = await self.run(
                user_input=user_input,
                customer_id=customer_id,
                conversation_id=conversation_id,
                channel=channel,
                context=context
            )

            # Yield the final response as text delta
            yield {
                "type": "text_delta",
                "data": result["final_output"]
            }

            # Yield final event
            yield {
                "type": "final",
                "data": {
                    "final_output": result["final_output"],
                    "execution_time": result["execution_time"],
                    "scenario": result.get("scenario"),
                    "ticket_id": result.get("ticket_id")
                }
            }

            logger.info(f"SmartAgent streaming completed [cid: {conversation_id[:8]}]")

        except Exception as e:
            logger.error(f"SmartAgent streaming failed: {e}", exc_info=True)
            yield {
                "type": "error",
                "data": {
                    "error": str(e),
                    "fallback_response": self._get_error_response(channel)
                }
            }

    def _get_error_response(self, channel: str) -> str:
        """Get channel-appropriate error response."""
        base_message = (
            "I apologize, but I'm experiencing technical difficulties at the moment. "
            "Your message has been recorded, and our support team will respond shortly."
        )

        if channel == "email":
            return (
                f"{base_message}\n\n"
                f"Best regards,\n"
                f"Custora AI Support Team\n"
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
