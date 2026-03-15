"""
Message Handlers - Process Different Event Types
Each handler processes a specific event type from Kafka
"""

from typing import Dict, Any
from datetime import datetime

from src.utils.logging import get_logger
from src.database.client import (
    get_db_connection,
    get_conversation_history,
    update_conversation_status,
)

logger = get_logger(__name__)


# ============================================
# Message Event Handlers
# ============================================

async def handle_message_received(event: Dict[str, Any]) -> None:
    """
    Handle message.received event.

    This event is published when a customer message arrives.
    We can use it for:
    - Real-time analytics
    - Sentiment analysis
    - Spam detection
    - Message routing

    Args:
        event: MessageReceivedEvent data
    """
    try:
        message_id = event.get('message_id')
        conversation_id = event.get('conversation_id')
        customer_id = event.get('customer_id')
        content = event.get('content')
        channel = event.get('channel')

        logger.info(f"Processing message.received event", extra={
            'message_id': message_id,
            'conversation_id': conversation_id,
            'customer_id': customer_id,
            'channel': channel,
        })

        # Example: Log message for analytics
        # In production, you might:
        # - Send to analytics service
        # - Perform sentiment analysis
        # - Check for spam
        # - Update real-time dashboards

        logger.info(f"Message received event processed", extra={
            'message_id': message_id,
            'content_length': len(content) if content else 0,
        })

    except Exception as e:
        logger.error(f"Failed to handle message.received event: {e}", exc_info=True)
        raise


async def handle_message_sent(event: Dict[str, Any]) -> None:
    """
    Handle message.sent event.

    This event is published when a response is sent to customer.
    We can use it for:
    - Delivery tracking
    - Response time metrics
    - Customer satisfaction tracking

    Args:
        event: MessageSentEvent data
    """
    try:
        message_id = event.get('message_id')
        conversation_id = event.get('conversation_id')
        customer_id = event.get('customer_id')
        channel = event.get('channel')
        delivery_status = event.get('delivery_status')

        logger.info(f"Processing message.sent event", extra={
            'message_id': message_id,
            'conversation_id': conversation_id,
            'customer_id': customer_id,
            'channel': channel,
            'delivery_status': delivery_status,
        })

        # Example: Track delivery metrics
        # In production, you might:
        # - Update delivery status in database
        # - Send delivery confirmation
        # - Track response time metrics
        # - Update customer satisfaction scores

        logger.info(f"Message sent event processed", extra={
            'message_id': message_id,
            'delivery_status': delivery_status,
        })

    except Exception as e:
        logger.error(f"Failed to handle message.sent event: {e}", exc_info=True)
        raise


# ============================================
# Escalation Event Handlers
# ============================================

async def handle_escalation_created(event: Dict[str, Any]) -> None:
    """
    Handle escalation.created event.

    This event is published when a conversation is escalated to human.
    We can use it for:
    - Notify human support team
    - Update conversation status
    - Send alerts based on urgency
    - Track escalation metrics

    Args:
        event: EscalationCreatedEvent data
    """
    try:
        conversation_id = event.get('conversation_id')
        customer_id = event.get('customer_id')
        reason = event.get('reason')
        urgency = event.get('urgency')
        channel = event.get('channel')
        trigger = event.get('trigger')

        logger.warning(f"Processing escalation.created event", extra={
            'conversation_id': conversation_id,
            'customer_id': customer_id,
            'urgency': urgency,
            'trigger': trigger,
        })

        # Update conversation status to escalated
        await update_conversation_status(conversation_id, 'escalated')
        logger.info(f"Conversation status updated to escalated", extra={
            'conversation_id': conversation_id,
        })

        # Send notification based on urgency
        if urgency == 'critical':
            # Send immediate alert (SMS, Slack, PagerDuty)
            logger.critical(f"CRITICAL ESCALATION", extra={
                'conversation_id': conversation_id,
                'customer_id': customer_id,
                'reason': reason,
            })
            # TODO: Send to notification service

        elif urgency == 'high':
            # Send high priority alert
            logger.error(f"HIGH PRIORITY ESCALATION", extra={
                'conversation_id': conversation_id,
                'customer_id': customer_id,
                'reason': reason,
            })
            # TODO: Send to notification service

        else:
            # Normal escalation - add to queue
            logger.info(f"Normal escalation queued", extra={
                'conversation_id': conversation_id,
            })

        # In production, you might:
        # - Send Slack notification to support team
        # - Create Jira ticket
        # - Send email to support manager
        # - Update CRM system
        # - Trigger PagerDuty alert (for critical)

        logger.info(f"Escalation event processed", extra={
            'conversation_id': conversation_id,
            'urgency': urgency,
        })

    except Exception as e:
        logger.error(f"Failed to handle escalation.created event: {e}", exc_info=True)
        raise


# ============================================
# Ticket Event Handlers
# ============================================

async def handle_ticket_created(event: Dict[str, Any]) -> None:
    """
    Handle ticket.created event.

    This event is published when a support ticket is created.
    We can use it for:
    - Notify support team
    - Auto-assign tickets
    - Track ticket metrics
    - Send confirmation to customer

    Args:
        event: TicketCreatedEvent data
    """
    try:
        ticket_id = event.get('ticket_id')
        conversation_id = event.get('conversation_id')
        customer_id = event.get('customer_id')
        subject = event.get('subject')
        priority = event.get('priority')
        category = event.get('category')

        logger.info(f"Processing ticket.created event", extra={
            'ticket_id': ticket_id,
            'conversation_id': conversation_id,
            'customer_id': customer_id,
            'priority': priority,
            'category': category,
        })

        # Get customer info
        customer = await get_customer_by_id(customer_id)
        customer_name = customer['name'] if customer else 'Unknown'

        # Auto-assign based on category and priority
        assigned_to = await _auto_assign_ticket(category, priority)

        if assigned_to:
            logger.info(f"Ticket auto-assigned", extra={
                'ticket_id': ticket_id,
                'assigned_to': assigned_to,
            })
            # TODO: Update ticket assignment in database

        # Send notification to support team
        logger.info(f"New ticket notification", extra={
            'ticket_id': ticket_id,
            'customer': customer_name,
            'subject': subject,
            'priority': priority,
        })

        # In production, you might:
        # - Send email to assigned agent
        # - Post to Slack channel
        # - Update ticket tracking system
        # - Send confirmation email to customer
        # - Create calendar reminder for follow-up

        logger.info(f"Ticket event processed", extra={
            'ticket_id': ticket_id,
        })

    except Exception as e:
        logger.error(f"Failed to handle ticket.created event: {e}", exc_info=True)
        raise


async def _auto_assign_ticket(category: str, priority: str) -> str:
    """
    Auto-assign ticket to support agent based on category and priority.

    Args:
        category: Ticket category
        priority: Ticket priority

    Returns:
        Agent email or None
    """
    # Simple round-robin assignment logic
    # In production, use proper load balancing

    assignment_rules = {
        'technical': 'tech-support@custora.com',
        'billing': 'billing@custora.com',
        'security': 'security@custora.com',
        'account': 'account-support@custora.com',
    }

    return assignment_rules.get(category, 'general-support@custora.com')


# ============================================
# Agent Event Handlers
# ============================================

async def handle_agent_execution_completed(event: Dict[str, Any]) -> None:
    """
    Handle agent.execution.completed event.

    This event is published when agent finishes processing a message.
    We can use it for:
    - Track agent performance metrics
    - Monitor execution times
    - Identify slow queries
    - Track tool usage

    Args:
        event: AgentExecutionCompletedEvent data
    """
    try:
        conversation_id = event.get('conversation_id')
        customer_id = event.get('customer_id')
        message_id = event.get('message_id')
        execution_time = event.get('execution_time')
        tools_used = event.get('tools_used', [])
        success = event.get('success')
        error = event.get('error')

        logger.info(f"Processing agent.execution.completed event", extra={
            'conversation_id': conversation_id,
            'message_id': message_id,
            'execution_time': execution_time,
            'tools_count': len(tools_used),
            'success': success,
        })

        # Track performance metrics
        if execution_time > 10.0:
            logger.warning(f"Slow agent execution detected", extra={
                'conversation_id': conversation_id,
                'execution_time': execution_time,
                'tools_used': tools_used,
            })

        # Track tool usage
        if tools_used:
            logger.info(f"Agent tools used", extra={
                'tools': tools_used,
                'count': len(tools_used),
            })

        # Track failures
        if not success:
            logger.error(f"Agent execution failed", extra={
                'conversation_id': conversation_id,
                'message_id': message_id,
                'error': error,
            })

        # In production, you might:
        # - Send metrics to monitoring system (Prometheus, Datadog)
        # - Update performance dashboards
        # - Alert on high failure rates
        # - Track tool usage statistics
        # - Identify optimization opportunities

        logger.info(f"Agent execution event processed", extra={
            'conversation_id': conversation_id,
            'execution_time': execution_time,
        })

    except Exception as e:
        logger.error(f"Failed to handle agent.execution.completed event: {e}", exc_info=True)
        raise


# ============================================
# Event Router
# ============================================

async def route_event(event: Dict[str, Any]) -> None:
    """
    Route event to appropriate handler based on event_type.

    Args:
        event: Event data with event_type field
    """
    event_type = event.get('event_type')

    if not event_type:
        logger.error("Event missing event_type field", extra={'event': event})
        return

    handlers = {
        'message.received': handle_message_received,
        'message.sent': handle_message_sent,
        'escalation.created': handle_escalation_created,
        'ticket.created': handle_ticket_created,
        'agent.execution.completed': handle_agent_execution_completed,
    }

    handler = handlers.get(event_type)

    if not handler:
        logger.warning(f"No handler for event type: {event_type}")
        return

    await handler(event)
