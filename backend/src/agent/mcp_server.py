"""
Custora Customer Success Agent - MCP Server
Provides 5 tools for the OpenAI Agent to use
"""

import asyncio
import asyncpg
import os
from typing import Optional, List
from pydantic import BaseModel
from enum import Enum
import json

# Import settings from config (secure way)
from src.config import settings

# Database connection - use settings instead of hardcoded value
DATABASE_URL = settings.DATABASE_URL

# Channel enum
class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"

# Tool Input Models
class KnowledgeSearchInput(BaseModel):
    query: str
    max_results: int = 5

class TicketInput(BaseModel):
    customer_id: str
    issue: str
    priority: str = "medium"
    category: Optional[str] = None
    channel: Channel

class EscalationInput(BaseModel):
    ticket_id: str
    reason: str
    urgency: str = "normal"

class ResponseInput(BaseModel):
    ticket_id: str
    message: str
    channel: Channel

# Database connection pool
db_pool = None

async def get_db_pool():
    """Get or create database connection pool."""
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    return db_pool

# Tool 1: Search Knowledge Base
async def search_knowledge_base(input: KnowledgeSearchInput) -> str:
    """
    Search product documentation for relevant information.

    Use this when the customer asks questions about product features,
    how to use something, or needs technical information.

    Args:
        input: KnowledgeSearchInput with query and max_results

    Returns:
        Formatted search results with relevance scores
    """
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        # For now, simple text search (embeddings will be added in Phase 2)
        results = await conn.fetch("""
            SELECT id, title, content, category,
                   similarity(content, $1) as relevance
            FROM knowledge_base
            WHERE content ILIKE '%' || $1 || '%'
            ORDER BY relevance DESC
            LIMIT $2
        """, input.query, input.max_results)

        if not results:
            return "No relevant documentation found. Consider escalating to human support."

        formatted_results = []
        for i, row in enumerate(results, 1):
            formatted_results.append(
                f"{i}. **{row['title']}** (Category: {row['category']})\n"
                f"   {row['content'][:300]}...\n"
            )

        return "\n".join(formatted_results)

# Tool 2: Create Ticket
async def create_ticket(input: TicketInput) -> str:
    """
    Create a support ticket for tracking.

    ALWAYS create a ticket at the start of every conversation.
    Include the source channel for proper tracking.

    Args:
        input: TicketInput with customer_id, issue, priority, category, channel

    Returns:
        ticket_id
    """
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        ticket_id = await conn.fetchval("""
            INSERT INTO tickets (customer_id, category, priority, status, source_channel, resolution_notes)
            VALUES ($1, $2, $3, 'open', $4, $5)
            RETURNING id
        """, input.customer_id, input.category or 'general', input.priority, input.channel.value, input.issue)

        return f"Ticket created successfully: {ticket_id}"

# Tool 3: Get Customer History
async def get_customer_history(customer_id: str) -> str:
    """
    Get customer's complete interaction history across ALL channels.

    Use this to understand context from previous conversations,
    even if they happened on a different channel.

    Args:
        customer_id: UUID of the customer

    Returns:
        Formatted history (last 20 interactions)
    """
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        history = await conn.fetch("""
            SELECT c.initial_channel, c.started_at, c.status,
                   m.content, m.role, m.channel, m.created_at
            FROM conversations c
            JOIN messages m ON m.conversation_id = c.id
            WHERE c.customer_id = $1
            ORDER BY m.created_at DESC
            LIMIT 20
        """, customer_id)

        if not history:
            return "No previous interaction history found for this customer."

        formatted_history = []
        for row in history:
            formatted_history.append(
                f"[{row['created_at'].strftime('%Y-%m-%d %H:%M')}] "
                f"{row['channel']} - {row['role']}: {row['content'][:100]}..."
            )

        return "\n".join(formatted_history)

# Tool 4: Escalate to Human
async def escalate_to_human(input: EscalationInput) -> str:
    """
    Escalate conversation to human support.

    Use this when:
    - Customer asks about pricing or refunds
    - Customer sentiment is negative
    - You cannot find relevant information
    - Customer explicitly requests human help

    Args:
        input: EscalationInput with ticket_id, reason, urgency

    Returns:
        Escalation confirmation with expected response time
    """
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE tickets
            SET status = 'escalated',
                resolution_notes = $1
            WHERE id = $2
        """, f"Escalation reason: {input.reason}", input.ticket_id)

        # Determine response time based on urgency
        response_times = {
            "urgent": "1-2 hours",
            "high": "4-8 hours",
            "normal": "12-24 hours"
        }

        response_time = response_times.get(input.urgency, "12-24 hours")

        return (
            f"I've escalated your case to our human support team. "
            f"A specialist will respond within {response_time}. "
            f"Your ticket reference is: {input.ticket_id}"
        )

# Tool 5: Send Response
async def send_response(input: ResponseInput) -> str:
    """
    Send response to customer via their preferred channel.

    The response will be automatically formatted for the channel.
    Email: Formal with greeting/signature
    WhatsApp: Concise and conversational
    Web: Semi-formal

    Args:
        input: ResponseInput with ticket_id, message, channel

    Returns:
        Delivery status
    """
    # Format response based on channel
    formatted_message = format_for_channel(input.message, input.channel)

    # In Phase 2, this will actually send via Gmail API, Twilio, etc.
    # For now, we just return the formatted message

    return f"Response formatted for {input.channel.value}:\n\n{formatted_message}"

def format_for_channel(message: str, channel: Channel) -> str:
    """Format response appropriately for the channel."""

    if channel == Channel.EMAIL:
        return f"""Dear Customer,

Thank you for reaching out to Custora Support.

{message}

If you have any further questions, please don't hesitate to reply to this email.

Best regards,
Custora Support Team
---
This response was generated by our AI assistant."""

    elif channel == Channel.WHATSAPP:
        # Keep it short for WhatsApp
        if len(message) > 300:
            message = message[:297] + "..."
        return f"{message}\n\n📱 Reply for more help or type 'human' for live support."

    else:  # web_form
        return f"""{message}

---
Need more help? Submit another ticket or contact support@custora.com"""

# MCP Server Tools Registry
TOOLS = {
    "search_knowledge_base": search_knowledge_base,
    "create_ticket": create_ticket,
    "get_customer_history": get_customer_history,
    "escalate_to_human": escalate_to_human,
    "send_response": send_response
}

async def main():
    """Initialize MCP server."""
    print("Custora Customer Success Agent - MCP Server")
    print("=" * 50)
    print(f"Available Tools: {len(TOOLS)}")
    for tool_name in TOOLS.keys():
        print(f"  - {tool_name}")
    print("=" * 50)

    # Initialize database pool
    await get_db_pool()
    print("[OK] Database connection pool initialized")
    print("[OK] MCP Server ready")

if __name__ == "__main__":
    asyncio.run(main())
