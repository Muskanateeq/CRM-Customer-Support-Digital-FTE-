"""
Ticket Management API Endpoints
Provides REST API for ticket search, retrieval, and management
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.database.client import (
    get_ticket,
    get_db_connection,
)
from src.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/tickets", tags=["tickets"])


class TicketResponse(BaseModel):
    """Ticket response model."""
    id: str
    ticket_number: str
    customer_id: str
    customer_name: str
    customer_email: str
    category: str
    priority: str
    status: str
    source_channel: str
    created_at: str
    resolved_at: Optional[str] = None


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response."""
    total_tickets: int
    open_tickets: int
    resolved_tickets: int
    avg_response_time: str
    total_customers: int
    total_conversations: int


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats() -> DashboardStatsResponse:
    """
    Get dashboard statistics.

    Returns:
        Dashboard stats including ticket counts and metrics
    """
    try:
        async with get_db_connection() as conn:
            # Get ticket counts
            total_tickets = await conn.fetchval("SELECT COUNT(*) FROM tickets")
            open_tickets = await conn.fetchval("SELECT COUNT(*) FROM tickets WHERE status IN ('open', 'processing')")
            resolved_tickets = await conn.fetchval("SELECT COUNT(*) FROM tickets WHERE status = 'resolved'")

            # Get customer and conversation counts
            total_customers = await conn.fetchval("SELECT COUNT(*) FROM customers")
            total_conversations = await conn.fetchval("SELECT COUNT(*) FROM conversations")

            # Calculate average response time based on message timestamps
            # Get average time between customer message and first agent response
            avg_response_seconds = await conn.fetchval(
                """
                WITH response_times AS (
                    SELECT
                        EXTRACT(EPOCH FROM (
                            agent_msg.created_at - customer_msg.created_at
                        )) as response_seconds
                    FROM messages customer_msg
                    JOIN LATERAL (
                        SELECT created_at
                        FROM messages
                        WHERE conversation_id = customer_msg.conversation_id
                        AND role = 'agent'
                        AND direction = 'outbound'
                        AND created_at > customer_msg.created_at
                        ORDER BY created_at ASC
                        LIMIT 1
                    ) agent_msg ON true
                    WHERE customer_msg.role = 'customer'
                    AND customer_msg.direction = 'inbound'
                    AND customer_msg.created_at >= NOW() - INTERVAL '7 days'
                )
                SELECT AVG(response_seconds)
                FROM response_times
                WHERE response_seconds > 0 AND response_seconds < 3600
                """
            )

            # Format response time
            if avg_response_seconds and avg_response_seconds > 0:
                if avg_response_seconds < 60:
                    avg_response_time = f"< {int(avg_response_seconds)} seconds"
                elif avg_response_seconds < 120:
                    avg_response_time = "< 2 minutes"
                else:
                    avg_minutes = int(avg_response_seconds / 60)
                    avg_response_time = f"< {avg_minutes} minutes"
            else:
                avg_response_time = "< 2 minutes"

            return DashboardStatsResponse(
                total_tickets=total_tickets or 0,
                open_tickets=open_tickets or 0,
                resolved_tickets=resolved_tickets or 0,
                avg_response_time=avg_response_time,
                total_customers=total_customers or 0,
                total_conversations=total_conversations or 0
            )

    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/recent")
async def get_recent_tickets(limit: int = Query(5, ge=1, le=20)) -> Dict[str, Any]:
    """
    Get recent tickets for dashboard.

    Args:
        limit: Number of tickets to return (default: 5, max: 20)

    Returns:
        List of recent tickets
    """
    try:
        async with get_db_connection() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    t.id,
                    t.customer_id,
                    t.category,
                    t.priority,
                    t.status,
                    t.source_channel,
                    t.created_at,
                    t.resolved_at,
                    t.resolution_notes as subject,
                    c.name as customer_name,
                    c.email as customer_email,
                    CONCAT('TKT-', UPPER(REPLACE(t.id::text, '-', ''))) as ticket_number
                FROM tickets t
                JOIN customers c ON t.customer_id = c.id
                ORDER BY t.created_at DESC
                LIMIT $1
                """,
                limit
            )

            tickets = []
            for row in rows:
                ticket = dict(row)
                ticket['created_at'] = ticket['created_at'].isoformat() if ticket['created_at'] else None
                ticket['resolved_at'] = ticket['resolved_at'].isoformat() if ticket['resolved_at'] else None
                ticket['id'] = str(ticket['id'])
                ticket['customer_id'] = str(ticket['customer_id'])
                tickets.append(ticket)

            return {
                "tickets": tickets,
                "count": len(tickets)
            }

    except Exception as e:
        logger.error(f"Failed to get recent tickets: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_tickets(
    q: str = Query(..., description="Search by ticket number or email")
) -> Dict[str, Any]:
    """
    Search tickets by ticket number or email address.

    Examples:
    - /tickets/search?q=TKT-12345678
    - /tickets/search?q=john@example.com
    """
    try:
        logger.info(f"Searching tickets with query: {q}")

        tickets = []

        # Check if query is ticket number or email
        if q.upper().startswith("TKT-"):
            # Search by ticket number
            ticket_id_part = q.replace("TKT-", "").replace("-", "").lower()

            async with get_db_connection() as conn:
                rows = await conn.fetch(
                    """
                    SELECT
                        t.id,
                        t.customer_id,
                        t.category,
                        t.priority,
                        t.status,
                        t.source_channel,
                        t.created_at,
                        t.resolved_at,
                        c.name as customer_name,
                        c.email as customer_email,
                        CONCAT('TKT-', UPPER(REPLACE(t.id::text, '-', ''))) as ticket_number
                    FROM tickets t
                    JOIN customers c ON t.customer_id = c.id
                    WHERE UPPER(REPLACE(t.id::text, '-', '')) LIKE $1
                    ORDER BY t.created_at DESC
                    """,
                    f"%{ticket_id_part.upper()}%"
                )
                tickets = [dict(row) for row in rows]
        else:
            # Search by email
            async with get_db_connection() as conn:
                rows = await conn.fetch(
                    """
                    SELECT
                        t.id,
                        t.customer_id,
                        t.category,
                        t.priority,
                        t.status,
                        t.source_channel,
                        t.created_at,
                        t.resolved_at,
                        c.name as customer_name,
                        c.email as customer_email,
                        CONCAT('TKT-', UPPER(REPLACE(t.id::text, '-', ''))) as ticket_number
                    FROM tickets t
                    JOIN customers c ON t.customer_id = c.id
                    WHERE c.email ILIKE $1
                    ORDER BY t.created_at DESC
                    """,
                    f"%{q}%"
                )
                tickets = [dict(row) for row in rows]

        # Format dates as ISO strings
        for ticket in tickets:
            ticket['created_at'] = ticket['created_at'].isoformat() if ticket['created_at'] else None
            ticket['resolved_at'] = ticket['resolved_at'].isoformat() if ticket['resolved_at'] else None
            ticket['id'] = str(ticket['id'])
            ticket['customer_id'] = str(ticket['customer_id'])

        logger.info(f"Found {len(tickets)} tickets")

        return {
            "tickets": tickets,
            "count": len(tickets)
        }

    except Exception as e:
        logger.error(f"Ticket search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to search tickets: {str(e)}")


@router.get("/{ticket_id}")
async def get_ticket_details(ticket_id: str) -> Dict[str, Any]:
    """Get ticket details with conversation messages."""
    try:
        async with get_db_connection() as conn:
            # Get ticket with customer info
            ticket_row = await conn.fetchrow(
                """
                SELECT
                    t.id,
                    t.customer_id,
                    t.conversation_id,
                    t.category,
                    t.priority,
                    t.status,
                    t.source_channel,
                    t.created_at,
                    t.resolved_at,
                    t.resolution_notes,
                    t.escalation_reason,
                    c.name as customer_name,
                    c.email as customer_email,
                    c.phone as customer_phone
                FROM tickets t
                JOIN customers c ON t.customer_id = c.id
                WHERE t.id = $1
                """,
                ticket_id
            )

        if not ticket_row:
            raise HTTPException(status_code=404, detail="Ticket not found")

        ticket = dict(ticket_row)

        # Get conversation messages if conversation_id exists
        messages = []
        if ticket.get('conversation_id'):
            from src.database.client import get_conversation_history
            conversation_messages = await get_conversation_history(
                str(ticket['conversation_id']),
                limit=100
            )
            messages = [
                {
                    'id': str(msg['id']),
                    'role': msg['role'],
                    'content': msg['content'],
                    'created_at': msg['created_at'].isoformat() if msg.get('created_at') else None,
                    'channel': msg.get('channel', 'web_form')
                }
                for msg in conversation_messages
            ]

        # Format response
        return {
            'ticket': {
                'id': str(ticket['id']),
                'ticket_number': f"TKT-{str(ticket['id']).replace('-', '').upper()[:8]}",
                'customer_id': str(ticket['customer_id']),
                'customer_name': ticket.get('customer_name') or 'Unknown',
                'customer_email': ticket.get('customer_email') or 'Unknown',
                'customer_phone': ticket.get('customer_phone'),
                'category': ticket['category'],
                'priority': ticket['priority'],
                'status': ticket['status'],
                'source_channel': ticket['source_channel'],
                'created_at': ticket['created_at'].isoformat(),
                'resolved_at': ticket['resolved_at'].isoformat() if ticket.get('resolved_at') else None,
                'subject': ticket.get('resolution_notes') or ticket.get('escalation_reason') or 'No subject'
            },
            'messages': messages,
            'message_count': len(messages)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get ticket: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customer/{customer_id}")
async def get_customer_tickets(customer_id: str) -> Dict[str, Any]:
    """Get all tickets for a customer."""
    try:
        async with get_db_connection() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    t.id,
                    t.customer_id,
                    t.category,
                    t.priority,
                    t.status,
                    t.source_channel,
                    t.created_at,
                    t.resolved_at,
                    c.name as customer_name,
                    c.email as customer_email,
                    CONCAT('TKT-', UPPER(REPLACE(t.id::text, '-', ''))) as ticket_number
                FROM tickets t
                JOIN customers c ON t.customer_id = c.id
                WHERE t.customer_id = $1
                ORDER BY t.created_at DESC
                """,
                customer_id
            )

            tickets = []
            for row in rows:
                ticket = dict(row)
                ticket['created_at'] = ticket['created_at'].isoformat() if ticket['created_at'] else None
                ticket['resolved_at'] = ticket['resolved_at'].isoformat() if ticket['resolved_at'] else None
                ticket['id'] = str(ticket['id'])
                ticket['customer_id'] = str(ticket['customer_id'])
                tickets.append(ticket)

            return {
                "tickets": tickets,
                "count": len(tickets)
            }

    except Exception as e:
        logger.error(f"Failed to get customer tickets: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/help/popular")
async def get_popular_topics(limit: int = Query(5, ge=1, le=20)) -> Dict[str, Any]:
    """
    Get popular topics based on customer queries and ticket subjects.
    Groups similar queries together and shows total frequency.

    Args:
        limit: Number of topics to return (default: 5, max: 20)

    Returns:
        List of popular topics with view counts
    """
    try:
        async with get_db_connection() as conn:
            # Get all customer queries with their frequencies
            rows = await conn.fetch(
                """
                SELECT
                    m.content,
                    t.category,
                    COUNT(*) as frequency
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                LEFT JOIN tickets t ON c.id = t.conversation_id
                WHERE
                    m.role = 'customer'
                    AND m.direction = 'inbound'
                    AND LENGTH(m.content) > 10
                    AND LENGTH(m.content) < 300
                GROUP BY m.content, t.category
                ORDER BY frequency DESC
                LIMIT 100
                """
            )

            # Group similar queries using keyword matching
            topic_groups = {}

            for row in rows:
                content = row['content'].strip().lower()
                category = row['category'] or 'general'
                frequency = row['frequency']

                # Extract key phrases (simple keyword-based grouping)
                matched = False
                for key in list(topic_groups.keys()):
                    # Check if queries are similar (share significant words)
                    key_words = set(key.split())
                    content_words = set(content.split())

                    # If 60% or more words match, group them together
                    common_words = key_words & content_words
                    if len(common_words) >= min(3, len(key_words) * 0.6):
                        topic_groups[key]['views'] += frequency
                        topic_groups[key]['count'] += 1
                        matched = True
                        break

                if not matched:
                    # Create new topic group
                    # Generate clean title (first 80 chars, capitalize)
                    clean_title = row['content'].strip()
                    if len(clean_title) > 80:
                        clean_title = clean_title[:77] + "..."

                    topic_groups[content] = {
                        'title': clean_title,
                        'category': category.capitalize(),
                        'views': frequency,
                        'count': 1
                    }

            # Sort by total views and take top N
            sorted_topics = sorted(
                topic_groups.values(),
                key=lambda x: x['views'],
                reverse=True
            )[:limit]

            # Format response
            topics = [
                {
                    'title': topic['title'],
                    'category': topic['category'],
                    'views': topic['views']
                }
                for topic in sorted_topics
            ]

            return {
                "topics": topics,
                "count": len(topics)
            }

    except Exception as e:
        logger.error(f"Failed to get popular topics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/help/categories")
async def get_help_categories() -> Dict[str, Any]:
    """
    Get help categories with ticket counts.

    Returns:
        List of categories with article/ticket counts
    """
    try:
        async with get_db_connection() as conn:
            # Get ticket counts by category
            rows = await conn.fetch(
                """
                SELECT
                    category,
                    COUNT(*) as articles
                FROM tickets
                GROUP BY category
                ORDER BY articles DESC
                """
            )

            # Map categories to display info
            category_map = {
                "technical": {
                    "title": "Technical Support",
                    "description": "Troubleshooting and technical guides",
                    "color": "from-[#10B981] to-[#059669]"
                },
                "billing": {
                    "title": "Billing & Plans",
                    "description": "Payment, invoices, and subscription info",
                    "color": "from-[#F59E0B] to-[#D97706]"
                },
                "account": {
                    "title": "Account Management",
                    "description": "Account settings and preferences",
                    "color": "from-[#3B82F6] to-[#2563EB]"
                },
                "general": {
                    "title": "Getting Started",
                    "description": "Learn the basics and set up your account",
                    "color": "from-[#3B82F6] to-[#2563EB]"
                }
            }

            categories = []
            for row in rows:
                cat_key = row['category'].lower()
                cat_info = category_map.get(cat_key, {
                    "title": row['category'].capitalize(),
                    "description": f"{row['category'].capitalize()} related topics",
                    "color": "from-[#3B82F6] to-[#2563EB]"
                })

                categories.append({
                    "title": cat_info["title"],
                    "description": cat_info["description"],
                    "articles": row['articles'],
                    "color": cat_info["color"],
                    "category": row['category']
                })

            return {
                "categories": categories,
                "count": len(categories)
            }

    except Exception as e:
        logger.error(f"Failed to get help categories: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/help/search")
async def search_help_articles(
    q: str = Query(..., description="Search query for help articles")
) -> Dict[str, Any]:
    """
    Search help articles based on customer queries and ticket data.

    Args:
        q: Search query

    Returns:
        List of matching customer queries and tickets
    """
    try:
        async with get_db_connection() as conn:
            rows = await conn.fetch(
                """
                WITH relevant_queries AS (
                    SELECT DISTINCT
                        m.id::text as id,
                        SUBSTRING(m.content, 1, 150) as title,
                        COALESCE(t.category, 'General') as category,
                        m.created_at,
                        COUNT(*) OVER (PARTITION BY LOWER(SUBSTRING(m.content, 1, 100))) as views
                    FROM messages m
                    JOIN conversations c ON m.conversation_id = c.id
                    LEFT JOIN tickets t ON c.id = t.conversation_id
                    WHERE
                        m.role = 'customer'
                        AND m.direction = 'inbound'
                        AND (
                            m.content ILIKE $1
                            OR t.category ILIKE $1
                        )
                        AND LENGTH(m.content) > 10
                        AND LENGTH(m.content) < 500
                )
                SELECT
                    id,
                    title,
                    category,
                    created_at,
                    views
                FROM relevant_queries
                ORDER BY views DESC, created_at DESC
                LIMIT 20
                """,
                f"%{q}%"
            )

            articles = []
            for row in rows:
                title = row['title'].strip()
                if title:
                    articles.append({
                        "id": row['id'],
                        "title": title,
                        "category": row['category'].capitalize() if row['category'] else 'General',
                        "views": row['views'],
                        "created_at": row['created_at'].isoformat() if row['created_at'] else None
                    })

            return {
                "articles": articles,
                "count": len(articles),
                "query": q
            }

    except Exception as e:
        logger.error(f"Failed to search help articles: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
