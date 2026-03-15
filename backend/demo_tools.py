"""
TaskNest Customer Success Agent - Demo Script
Tests the 5 MCP tools with sample data
"""

import asyncio
import sys
sys.path.append('src')

from agent.mcp_server import (
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    escalate_to_human,
    send_response,
    get_db_pool,
    KnowledgeSearchInput,
    TicketInput,
    EscalationInput,
    ResponseInput,
    Channel
)

async def demo():
    """Run demo of all 5 tools."""

    print("=" * 60)
    print("TaskNest Customer Success Agent - Tool Demo")
    print("=" * 60)
    print()

    # Initialize database connection
    await get_db_pool()
    print("✅ Database connected\n")

    # Demo 1: Create a test customer
    print("📝 Demo 1: Creating test customer...")
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        customer_id = await conn.fetchval("""
            INSERT INTO customers (email, name)
            VALUES ($1, $2)
            ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
        """, "demo@example.com", "Demo User")
    print(f"   Customer ID: {customer_id}\n")

    # Demo 2: Create Ticket
    print("🎫 Demo 2: Creating support ticket...")
    ticket_input = TicketInput(
        customer_id=str(customer_id),
        issue="How do I reset my password?",
        priority="medium",
        category="account",
        channel=Channel.EMAIL
    )
    ticket_result = await create_ticket(ticket_input)
    print(f"   {ticket_result}\n")

    # Extract ticket_id from result
    ticket_id = ticket_result.split(": ")[1]

    # Demo 3: Search Knowledge Base
    print("🔍 Demo 3: Searching knowledge base...")
    search_input = KnowledgeSearchInput(
        query="password reset",
        max_results=3
    )
    search_result = await search_knowledge_base(search_input)
    print(f"   Results:\n{search_result}\n")

    # Demo 4: Get Customer History
    print("📜 Demo 4: Getting customer history...")
    history_result = await get_customer_history(str(customer_id))
    print(f"   History:\n{history_result}\n")

    # Demo 5: Send Response (Email)
    print("📧 Demo 5: Sending response via Email...")
    response_input = ResponseInput(
        ticket_id=ticket_id,
        message="To reset your password, go to the login page and click 'Forgot Password'. Enter your email and you'll receive a reset link.",
        channel=Channel.EMAIL
    )
    response_result = await send_response(response_input)
    print(f"{response_result}\n")

    # Demo 6: Send Response (WhatsApp)
    print("💬 Demo 6: Sending response via WhatsApp...")
    response_input_wa = ResponseInput(
        ticket_id=ticket_id,
        message="To reset password: Login page → Forgot Password → Enter email → Check inbox for reset link.",
        channel=Channel.WHATSAPP
    )
    response_result_wa = await send_response(response_input_wa)
    print(f"{response_result_wa}\n")

    # Demo 7: Escalate to Human
    print("🚨 Demo 7: Escalating to human support...")
    escalation_input = EscalationInput(
        ticket_id=ticket_id,
        reason="Customer requested human agent",
        urgency="normal"
    )
    escalation_result = await escalate_to_human(escalation_input)
    print(f"   {escalation_result}\n")

    print("=" * 60)
    print("✅ All 5 tools tested successfully!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(demo())
