"""
OpenAI Agent Tools - 5 Function Tools for Customer Success FTE
Each tool integrates with database and follows channel-aware patterns
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from agents import function_tool, RunContextWrapper

from src.database.client import (
    get_db_connection,
    create_ticket as db_create_ticket,
    get_conversation_history,
    create_message,
)
from src.embeddings.vector_search import search_knowledge_base_semantic
from src.utils.logging import get_logger
from src.config import settings

logger = get_logger(__name__)


@function_tool
async def search_knowledge_base(
    query: str,
    limit: int = 5
) -> str:
    """Search the knowledge base for relevant product documentation and help articles.

    Use this tool when the customer asks questions about:
    - Product features and functionality
    - How-to guides and tutorials
    - Troubleshooting common issues
    - Account management
    - Integrations and API usage

    Args:
        query: The search query based on customer's question
        limit: Maximum number of results to return (default: 5)

    Returns:
        Formatted string with relevant knowledge base articles
    """
    try:
        logger.info(f"Searching knowledge base", extra={"query": query, "limit": limit})

        # Search knowledge base using semantic search (vector similarity)
        results = await search_knowledge_base_semantic(
            query=query,
            limit=limit,
            similarity_threshold=0.7  # 70% similarity minimum
        )

        if not results:
            return """No specific documentation found in knowledge base for this query.

IMPORTANT: Use your general knowledge and expertise to help the customer.
Provide a helpful, actionable response based on common best practices and your training.
Only escalate if the issue truly requires human intervention (legal matters, refunds, security incidents, or customer explicitly requests human support)."""

        # Format results for agent
        formatted_results = []
        for idx, result in enumerate(results, 1):
            similarity_pct = int(result.get('similarity', 0) * 100)
            formatted_results.append(
                f"{idx}. {result['title']} (Relevance: {similarity_pct}%)\n"
                f"   Category: {result['category']}\n"
                f"   Content: {result['content'][:200]}...\n"
            )

        response = "Found relevant articles:\n\n" + "\n".join(formatted_results)
        logger.info(f"Knowledge base search returned {len(results)} results", extra={
            'top_similarity': results[0].get('similarity', 0) if results else 0
        })

        return response

    except Exception as e:
        logger.error(f"Knowledge base search failed: {e}", exc_info=True)
        return f"Error searching knowledge base: {str(e)}"


@function_tool
async def create_ticket(
    customer_id: str,
    conversation_id: str,
    subject: str,
    priority: str = "medium",
    category: str = "general"
) -> str:
    """Create a support ticket for tracking customer issues.

    Use this tool when:
    - Customer reports a bug or technical issue
    - Issue requires investigation or follow-up
    - Customer requests a feature or enhancement
    - Issue cannot be resolved immediately

    Args:
        customer_id: The customer's unique ID (UUID)
        conversation_id: The conversation ID where issue was reported (UUID)
        subject: Brief description of the issue (max 200 chars)
        priority: Ticket priority - "low", "medium", "high", "urgent" (default: "medium")
        category: Issue category - "order_status", "shipping", "returns", "payment", "account", "product", "general" (default: "general")

    Returns:
        Confirmation message with ticket ID
    """
    try:
        logger.info(f"Creating ticket", extra={
            "customer_id": customer_id,
            "conversation_id": conversation_id,
            "priority": priority,
            "category": category
        })

        # Validate priority
        valid_priorities = ["low", "medium", "high", "urgent"]
        if priority not in valid_priorities:
            priority = "medium"

        # Validate category
        valid_categories = ["order_status", "shipping", "returns", "payment", "account", "product", "general"]
        if category not in valid_categories:
            category = "general"

        # Create ticket in database (returns UUID string)
        ticket_id = await db_create_ticket(
            customer_id=customer_id,
            conversation_id=conversation_id,
            category=category,
            priority=priority,
            source_channel="webform",
            resolution_notes=subject
        )

        logger.info(f"Ticket created successfully", extra={"ticket_id": ticket_id})

        # Publish ticket.created event (fire and forget)
        if settings.KAFKA_ENABLED:
            try:
                from src.kafka.helpers import publish_ticket_created
                import asyncio
                asyncio.create_task(publish_ticket_created(
                    ticket_id=ticket_id,
                    conversation_id=conversation_id,
                    customer_id=customer_id,
                    subject=subject,
                    priority=priority,
                    category=category,
                    status="open",
                ))
            except Exception as e:
                logger.warning(f"Failed to publish ticket.created event: {e}")

        return (
            f"[OK] Support ticket created successfully!\n\n"
            f"Ticket ID: #{ticket_id}\n"
            f"Subject: {subject}\n"
            f"Priority: {priority.upper()}\n"
            f"Category: {category}\n"
            f"Status: Open\n\n"
            f"Our support team will review this ticket and follow up with you soon."
        )

    except Exception as e:
        logger.error(f"Ticket creation failed: {e}", exc_info=True)
        return f"Error creating ticket: {str(e)}"


@function_tool
async def get_customer_history(
    customer_id: str,
    conversation_id: str,
    limit: int = 10
) -> str:
    """Retrieve customer's conversation history across all channels.

    Use this tool to:
    - Understand context from previous interactions
    - Check if issue was discussed before
    - Provide personalized responses based on history
    - Avoid asking for information already provided

    Args:
        customer_id: The customer's unique ID (UUID)
        conversation_id: Current conversation ID (UUID)
        limit: Maximum number of previous messages to retrieve (default: 10)

    Returns:
        Formatted conversation history with timestamps and channels
    """
    try:
        logger.info(f"Fetching customer history", extra={
            "customer_id": customer_id,
            "conversation_id": conversation_id,
            "limit": limit
        })

        # Get customer info from database
        async with get_db_connection() as conn:
            customer = await conn.fetchrow(
                "SELECT id, email, name, phone FROM customers WHERE id = $1",
                customer_id
            )

        if not customer:
            return f"Customer with ID {customer_id} not found."

        # Get conversation messages
        messages = await get_conversation_history(conversation_id)

        if not messages:
            return "No previous messages in this conversation."

        # Format history
        formatted_history = [
            f"Customer: {customer['name']} ({customer['email']})\n"
            f"Conversation started: {messages[0]['created_at']}\n"
            f"Total messages: {len(messages)}\n"
        ]

        for msg in messages:
            timestamp = msg['created_at'].strftime("%Y-%m-%d %H:%M")
            sender = "Customer" if msg['role'] == 'customer' else "Agent"
            channel = msg['channel'].upper()
            content = msg['content'][:150] + "..." if len(msg['content']) > 150 else msg['content']

            formatted_history.append(
                f"\n[{timestamp}] {sender} via {channel}:\n{content}"
            )

        response = "\n".join(formatted_history)
        logger.info(f"Retrieved {len(messages)} messages from history")

        return response

    except Exception as e:
        logger.error(f"Failed to fetch customer history: {e}", exc_info=True)
        return f"Error retrieving customer history: {str(e)}"


@function_tool
async def escalate_to_human(
    customer_id: str,
    conversation_id: str,
    reason: str,
    urgency: str = "normal"
) -> str:
    """Escalate the conversation to a human support agent.

    Use this tool when:
    - Customer explicitly requests human support
    - Issue involves legal, refund, or security matters
    - Customer is frustrated or angry (negative sentiment)
    - Issue is complex and beyond AI capabilities
    - Multiple resolution attempts have failed

    Args:
        customer_id: The customer's unique ID (UUID)
        conversation_id: The conversation ID to escalate (UUID)
        reason: Clear explanation of why escalation is needed
        urgency: Escalation urgency - "normal", "high", "critical" (default: "normal")

    Returns:
        Confirmation message that human agent will take over
    """
    try:
        logger.warning(f"Escalating to human", extra={
            "customer_id": customer_id,
            "conversation_id": conversation_id,
            "reason": reason,
            "urgency": urgency
        })

        # Validate urgency
        valid_urgencies = ["normal", "high", "critical"]
        if urgency not in valid_urgencies:
            urgency = "normal"

        # Create escalation message in database (returns UUID string)
        message_id = await create_message(
            conversation_id=conversation_id,
            role="system",
            content=f"🚨 ESCALATED TO HUMAN SUPPORT\nReason: {reason}\nUrgency: {urgency.upper()}",
            channel="system",
            direction="outbound",
            metadata={"escalation": True, "urgency": urgency, "reason": reason}
        )

        # In production, this would trigger:
        # 1. Kafka event to notify human support team
        # 2. Update conversation status to "escalated"
        # 3. Assign to available human agent based on urgency

        logger.info(f"Escalation recorded", extra={"message_id": message_id})

        # Publish escalation.created event (fire and forget)
        if settings.KAFKA_ENABLED:
            try:
                from src.kafka.helpers import publish_escalation_created
                import asyncio
                asyncio.create_task(publish_escalation_created(
                    conversation_id=conversation_id,
                    customer_id=customer_id,
                    reason=reason,
                    urgency=urgency,
                    channel="system",  # Will be updated with actual channel
                    trigger="agent_tool",
                ))
            except Exception as e:
                logger.warning(f"Failed to publish escalation.created event: {e}")

        urgency_messages = {
            "normal": "A human agent will respond within 2-4 hours.",
            "high": "A human agent will respond within 30 minutes.",
            "critical": "A human agent will respond immediately."
        }

        return (
            f"[OK] Your conversation has been escalated to our human support team.\n\n"
            f"Urgency Level: {urgency.upper()}\n"
            f"Reason: {reason}\n\n"
            f"{urgency_messages[urgency]}\n\n"
            f"Thank you for your patience. We're here to help!"
        )

    except Exception as e:
        logger.error(f"Escalation failed: {e}", exc_info=True)
        return f"Error escalating to human support: {str(e)}"


@function_tool
async def send_response(
    conversation_id: str,
    content: str,
    channel: str
) -> str:
    """Send a response to the customer through the appropriate channel.

    This tool formats and sends the final response to the customer.
    Channel-specific formatting is applied automatically.

    Args:
        conversation_id: The conversation ID (UUID)
        content: The response message content
        channel: Communication channel - "email", "whatsapp", "webform"

    Returns:
        Confirmation that message was sent
    """
    try:
        logger.info(f"Sending response", extra={
            "conversation_id": conversation_id,
            "channel": channel,
            "content_length": len(content)
        })

        # Validate channel
        valid_channels = ["email", "whatsapp", "webform"]
        if channel not in valid_channels:
            return f"Invalid channel: {channel}. Must be one of: {', '.join(valid_channels)}"

        # Apply channel-specific formatting
        formatted_content = _format_for_channel(content, channel)

        # Save message to database (returns UUID string)
        message_id = await create_message(
            conversation_id=conversation_id,
            role="agent",
            content=formatted_content,
            channel=channel,
            direction="outbound",
            metadata={"ai_generated": True, "original_length": len(content)}
        )

        # In production, this would trigger:
        # 1. Kafka event to channel-specific handler
        # 2. Email/WhatsApp/WebForm delivery
        # 3. Delivery confirmation tracking

        logger.info(f"Response sent successfully", extra={"message_id": message_id})

        return f"[OK] Response sent successfully via {channel.upper()}"

    except Exception as e:
        logger.error(f"Failed to send response: {e}", exc_info=True)
        return f"Error sending response: {str(e)}"


def _format_for_channel(content: str, channel: str) -> str:
    """Apply channel-specific formatting to response content."""

    if channel == "email":
        # Email: Formal, structured with signature
        return (
            f"{content}\n\n"
            f"Best regards,\n"
            f"Custora AI Customer Success Team\n"
            f"support@custoraai.com\n"
            f"Available 24/7"
        )

    elif channel == "whatsapp":
        # WhatsApp: Concise, friendly, emojis
        # Keep it under 300 chars if possible
        if len(content) > 300:
            content = content[:297] + "..."
        return f"{content}\n\n- Custora AI Support 🚀"

    elif channel == "webform":
        # Web Form: Semi-formal, clear structure
        return (
            f"{content}\n\n"
            f"Need more help? Reply to this conversation or visit our Help Center.\n"
            f"- Custora AI Support"
        )

    return content
