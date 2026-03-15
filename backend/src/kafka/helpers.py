"""
Kafka Helper Functions
Convenience functions for publishing events
"""

import uuid
from typing import Optional
from datetime import datetime

from src.kafka.producer import publish_event
from src.kafka.topics import get_topic_for_event_type
from src.kafka.events import (
    MessageReceivedEvent,
    MessageSentEvent,
    EscalationCreatedEvent,
    TicketCreatedEvent,
    AgentExecutionCompletedEvent,
)
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def publish_message_received(
    message_id: int,
    conversation_id: int,
    customer_id: int,
    content: str,
    channel: str,
    sender_type: str = "customer",
    channel_metadata: Optional[dict] = None,
) -> bool:
    """
    Publish message.received event.

    Args:
        message_id: Database message ID
        conversation_id: Conversation ID
        customer_id: Customer ID
        content: Message content
        channel: Channel (email, whatsapp, webform)
        sender_type: Sender type (customer, agent, system)
        channel_metadata: Channel-specific metadata

    Returns:
        True if published successfully
    """
    try:
        event = MessageReceivedEvent(
            event_id=str(uuid.uuid4()),
            message_id=message_id,
            conversation_id=conversation_id,
            customer_id=customer_id,
            content=content,
            channel=channel,
            sender_type=sender_type,
            channel_metadata=channel_metadata or {},
        )

        topic = get_topic_for_event_type("message.received")
        return await publish_event(topic, event, key=str(customer_id))

    except Exception as e:
        logger.error(f"Failed to publish message.received event: {e}", exc_info=True)
        return False


async def publish_message_sent(
    message_id: int,
    conversation_id: int,
    customer_id: int,
    content: str,
    channel: str,
    delivery_status: str = "sent",
    delivery_metadata: Optional[dict] = None,
) -> bool:
    """
    Publish message.sent event.

    Args:
        message_id: Database message ID
        conversation_id: Conversation ID
        customer_id: Customer ID
        content: Message content
        channel: Channel
        delivery_status: Delivery status (sent, delivered, failed)
        delivery_metadata: Delivery details

    Returns:
        True if published successfully
    """
    try:
        event = MessageSentEvent(
            event_id=str(uuid.uuid4()),
            message_id=message_id,
            conversation_id=conversation_id,
            customer_id=customer_id,
            content=content,
            channel=channel,
            delivery_status=delivery_status,
            delivery_metadata=delivery_metadata or {},
        )

        topic = get_topic_for_event_type("message.sent")
        return await publish_event(topic, event, key=str(customer_id))

    except Exception as e:
        logger.error(f"Failed to publish message.sent event: {e}", exc_info=True)
        return False


async def publish_escalation_created(
    conversation_id: int,
    customer_id: int,
    reason: str,
    urgency: str,
    channel: str,
    trigger: str,
) -> bool:
    """
    Publish escalation.created event.

    Args:
        conversation_id: Conversation ID
        customer_id: Customer ID
        reason: Escalation reason
        urgency: Urgency level (normal, high, critical)
        channel: Channel
        trigger: What triggered escalation

    Returns:
        True if published successfully
    """
    try:
        event = EscalationCreatedEvent(
            event_id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            customer_id=customer_id,
            reason=reason,
            urgency=urgency,
            channel=channel,
            trigger=trigger,
        )

        topic = get_topic_for_event_type("escalation.created")
        return await publish_event(topic, event, key=str(customer_id))

    except Exception as e:
        logger.error(f"Failed to publish escalation.created event: {e}", exc_info=True)
        return False


async def publish_ticket_created(
    ticket_id: int,
    conversation_id: int,
    customer_id: int,
    subject: str,
    priority: str,
    category: str,
    status: str,
) -> bool:
    """
    Publish ticket.created event.

    Args:
        ticket_id: Ticket ID
        conversation_id: Conversation ID
        customer_id: Customer ID
        subject: Ticket subject
        priority: Priority (low, medium, high, urgent)
        category: Category
        status: Status

    Returns:
        True if published successfully
    """
    try:
        event = TicketCreatedEvent(
            event_id=str(uuid.uuid4()),
            ticket_id=ticket_id,
            conversation_id=conversation_id,
            customer_id=customer_id,
            subject=subject,
            priority=priority,
            category=category,
            status=status,
        )

        topic = get_topic_for_event_type("ticket.created")
        return await publish_event(topic, event, key=str(customer_id))

    except Exception as e:
        logger.error(f"Failed to publish ticket.created event: {e}", exc_info=True)
        return False


async def publish_agent_execution_completed(
    conversation_id: int,
    customer_id: int,
    message_id: int,
    execution_time: float,
    tools_used: list,
    success: bool,
    error: Optional[str] = None,
) -> bool:
    """
    Publish agent.execution.completed event.

    Args:
        conversation_id: Conversation ID
        customer_id: Customer ID
        message_id: Message ID processed
        execution_time: Execution time in seconds
        tools_used: List of tools called
        success: Whether execution succeeded
        error: Error message if failed

    Returns:
        True if published successfully
    """
    try:
        event = AgentExecutionCompletedEvent(
            event_id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            customer_id=customer_id,
            message_id=message_id,
            execution_time=execution_time,
            tools_used=tools_used,
            success=success,
            error=error,
        )

        topic = get_topic_for_event_type("agent.execution.completed")
        return await publish_event(topic, event, key=str(customer_id))

    except Exception as e:
        logger.error(f"Failed to publish agent.execution.completed event: {e}", exc_info=True)
        return False
