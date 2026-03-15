"""
Web Form Channel Handler - FastAPI Endpoints
Handles web form submissions and provides REST API for chat
"""

from typing import Dict, Optional, Any
from datetime import datetime

from src.utils.logging import get_logger
from src.database.client import (
    get_customer_by_email,
    create_customer,
    get_or_create_customer_identifier,
    create_conversation,
    get_active_conversation,
    create_message,
    create_ticket,
)

logger = get_logger(__name__)


class WebFormHandler:
    """
    Web form handler for web-based chat interface.
    Processes messages from Next.js frontend.
    """

    def __init__(self):
        """Initialize web form handler."""
        logger.info("Web form handler initialized")

    async def process_message(
        self,
        email: str,
        name: str,
        subject: str,
        category: str,
        priority: str,
        message: str,
        conversation_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process incoming message from web form.

        Args:
            email: Customer's email address
            name: Customer's name
            subject: Issue subject/title
            category: Issue category
            priority: Priority level
            message: Message content
            conversation_id: Existing conversation ID (optional)
            metadata: Additional metadata (browser, IP, etc.)

        Returns:
            Processing result with customer_id, conversation_id, and ticket_id
        """
        try:
            logger.info(f"Processing web form message from {email}")

            # Get or create customer
            customer = await get_customer_by_email(email)

            if not customer:
                customer_id = await create_customer(
                    email=email,
                    phone=None,
                    name=name,
                )
                logger.info(f"Created new customer: {customer_id}")
            else:
                customer_id = str(customer['id'])
                if customer.get('name') != name:
                    # Update customer name if changed
                    # In production, would use update_customer function
                    logger.debug(f"Customer name mismatch: {customer.get('name')} vs {name}")

            # Ensure customer identifier exists
            await get_or_create_customer_identifier(
                customer_id=customer_id,
                identifier_type='email',
                identifier_value=email,
            )

            # Get or create conversation
            if conversation_id:
                # Use existing conversation
                pass
            else:
                # Get active conversation or create new one
                conversation = await get_active_conversation(customer_id)

                if not conversation:
                    conversation_id = await create_conversation(
                        customer_id=customer_id,
                        channel='webform',
                    )
                    logger.info(f"Created new conversation: {conversation_id}")
                else:
                    conversation_id = str(conversation['id'])

            # Prepare metadata
            msg_metadata = metadata or {}
            msg_metadata['source'] = 'webform'
            msg_metadata['subject'] = subject
            msg_metadata['category'] = category
            msg_metadata['priority'] = priority

            # NOTE: Ticket creation moved to agent tools
            # Agent will decide when to create ticket based on query type
            # Simple questions: Agent answers + creates ticket for tracking
            # Escalations: Agent creates ticket + escalates to human

            # Create message record
            message_id = await create_message(
                conversation_id=conversation_id,
                role='customer',
                content=message,
                channel='webform',
                direction='inbound',
                metadata=msg_metadata
            )

            logger.info(f"Web form message processed successfully", extra={
                'customer_id': customer_id,
                'conversation_id': conversation_id,
                'message_id': message_id,
            })

            return {
                'customer_id': customer_id,
                'conversation_id': conversation_id,
                'message_id': message_id,
                'ticket_id': None,  # Will be created by agent if needed
                'ticket_number': None,  # Will be created by agent if needed
                'email': email,
                'name': name,
            }

        except Exception as e:
            logger.error(f"Failed to process web form message: {e}", exc_info=True)
            raise

    async def send_response(
        self,
        conversation_id: int,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send response message for web form channel.

        Args:
            conversation_id: Conversation ID
            content: Response content
            metadata: Additional metadata

        Returns:
            Created message record
        """
        try:
            logger.info(f"Sending web form response to conversation {conversation_id}")

            # Prepare metadata
            msg_metadata = metadata or {}
            msg_metadata['source'] = 'webform'
            msg_metadata['ai_generated'] = True

            # Create message record
            message_id = await create_message(
                conversation_id=conversation_id,
                role='agent',
                content=content,
                channel='webform',
                direction='outbound',
                metadata=msg_metadata
            )

            logger.info(f"Web form response sent successfully", extra={
                'message_id': message_id
            })

            return {
                'message_id': message_id,
                'content': content
            }

        except Exception as e:
            logger.error(f"Failed to send web form response: {e}", exc_info=True)
            raise


# Global handler instance
_webform_handler: Optional[WebFormHandler] = None


def get_webform_handler() -> WebFormHandler:
    """
    Get or create global web form handler instance.

    Returns:
        WebFormHandler instance
    """
    global _webform_handler

    if _webform_handler is None:
        _webform_handler = WebFormHandler()

    return _webform_handler
