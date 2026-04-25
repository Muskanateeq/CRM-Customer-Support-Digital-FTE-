"""
OpenAI Agent Tools - 5 Function Tools for Customer Success FTE
Each tool integrates with database and follows channel-aware patterns

Note: These are legacy tool definitions. The system now uses:
- GroqAgentWithTools for Groq-based agents (tools defined inline)
- SmartAgent for classification-based approach (no tool calling)
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

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


async def create_ticket(
    customer_id: str,
    conversation_id: str,
    subject: str,
    priority: str = "medium",
    category: str = "general",
    channel: str = "webform"
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

        # Build response with conditional URL
        response = (
            f"[OK] Support ticket created successfully!\n\n"
            f"Ticket ID: #{ticket_id}\n"
            f"Subject: {subject}\n"
            f"Priority: {priority.upper()}\n"
            f"Category: {category}\n"
            f"Status: Open\n\n"
        )

        # Add tracking URL ONLY for email and WhatsApp
        if channel in ['email', 'whatsapp']:
            web_url = settings.FRONTEND_URL
            ticket_url = f"{web_url}/tickets/{ticket_id}"
            response += f"Track your ticket at: {ticket_url}\n\n"

        response += "Our support team will review this ticket and follow up with you soon."

        return response

    except Exception as e:
        logger.error(f"Ticket creation failed: {e}", exc_info=True)
        return f"Error creating ticket: {str(e)}"



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

        # Map urgency to priority
        priority_map = {
            "normal": "medium",
            "high": "high",
            "critical": "urgent"
        }
        priority = priority_map[urgency]

        # Get customer and conversation details
        async with get_db_connection() as conn:
            # Get customer info
            customer = await conn.fetchrow(
                "SELECT id, email, name, phone FROM customers WHERE id = $1",
                customer_id
            )

            if not customer:
                raise Exception(f"Customer {customer_id} not found")

            # Get conversation info
            conversation = await conn.fetchrow(
                "SELECT id, initial_channel FROM conversations WHERE id = $1",
                conversation_id
            )

            if not conversation:
                raise Exception(f"Conversation {conversation_id} not found")

            channel = conversation['initial_channel']

            # Get last customer message as query
            last_message = await conn.fetchrow(
                """
                SELECT content FROM messages
                WHERE conversation_id = $1 AND role = 'customer'
                ORDER BY created_at DESC
                LIMIT 1
                """,
                conversation_id
            )

            query = last_message['content'] if last_message else "Customer needs assistance"

            # Create escalated ticket
            ticket_id = await conn.fetchval(
                """
                INSERT INTO tickets (
                    customer_id, conversation_id, category, priority,
                    status, source_channel, escalation_reason, escalated_at
                )
                VALUES ($1, $2, 'general', $3, 'escalated', $4, $5, NOW())
                RETURNING id
                """,
                customer_id,
                conversation_id,
                priority,
                channel,
                reason
            )

            # Generate ticket number
            ticket_number = f"TKT-{str(ticket_id).replace('-', '').upper()[:8]}"

            logger.info(f"Created escalated ticket {ticket_number}")

        # Create escalation message in database
        message_id = await create_message(
            conversation_id=conversation_id,
            role="system",
            content=f"🚨 ESCALATED TO HUMAN SUPPORT\nTicket: {ticket_number}\nReason: {reason}\nUrgency: {urgency.upper()}",
            channel="system",
            direction="outbound",
            metadata={"escalation": True, "urgency": urgency, "reason": reason, "ticket_id": str(ticket_id)}
        )

        # Send notification email to admin
        try:
            from src.services.notification_service import send_escalation_notification

            await send_escalation_notification(
                ticket_id=str(ticket_id),
                ticket_number=ticket_number,
                customer_name=customer['name'] or 'Unknown',
                customer_email=customer['email'] or 'Unknown',
                customer_phone=customer['phone'],
                channel=channel,
                priority=priority,
                query=query,
                escalation_reason=reason
            )

            logger.info(f"Escalation notification sent for ticket {ticket_number}")
        except Exception as e:
            logger.error(f"Failed to send escalation notification: {e}", exc_info=True)

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
                    channel=channel,
                    trigger="agent_tool",
                ))
            except Exception as e:
                logger.warning(f"Failed to publish escalation.created event: {e}")

        urgency_messages = {
            "normal": "A human agent will respond within 24 hours.",
            "high": "A human agent will respond within 4 hours.",
            "critical": "A human agent will respond as soon as possible."
        }

        return (
            f"[OK] Your conversation has been escalated to our human support team.\n\n"
            f"Ticket Number: {ticket_number}\n"
            f"Priority: {priority.upper()}\n"
            f"Reason: {reason}\n\n"
            f"{urgency_messages[urgency]}\n\n"
            f"Thank you for your patience. We're here to help!"
        )

    except Exception as e:
        logger.error(f"Escalation failed: {e}", exc_info=True)
        return f"Error escalating to human support: {str(e)}"



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
