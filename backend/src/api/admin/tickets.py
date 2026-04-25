"""
Admin Ticket Management API
Handles escalated ticket viewing, responding, and status management
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.database.client import get_db_connection
from src.utils.logging import get_logger
from src.api.admin.auth import get_current_admin

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/admin/tickets", tags=["admin-tickets"])


class TicketListItem(BaseModel):
    """Ticket list item"""
    id: str
    ticket_number: str
    customer_id: str
    customer_name: str
    customer_email: str
    category: str
    priority: str
    status: str
    source_channel: str
    escalation_reason: Optional[str]
    created_at: str
    escalated_at: Optional[str]


class MessageItem(BaseModel):
    """Conversation message"""
    id: str
    role: str
    content: str
    channel: str
    direction: str
    created_at: str


class TicketDetailResponse(BaseModel):
    """Detailed ticket information"""
    ticket: Dict[str, Any]
    messages: List[MessageItem]
    responses: List[Dict[str, Any]]
    notes: List[Dict[str, Any]]


class SendResponseRequest(BaseModel):
    """Send response to customer"""
    content: str


class UpdateStatusRequest(BaseModel):
    """Update ticket status"""
    status: str


class AddNoteRequest(BaseModel):
    """Add internal note"""
    note_content: str


class DashboardStatsResponse(BaseModel):
    """Admin dashboard statistics"""
    total_escalated: int
    open_escalated: int
    in_progress: int
    resolved_today: int
    avg_response_time: str


@router.get("/list", response_model=List[TicketListItem])
async def list_escalated_tickets(
    status: Optional[str] = Query(None, description="Filter by status"),
    channel: Optional[str] = Query(None, description="Filter by channel"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    admin: dict = Depends(get_current_admin)
):
    """
    List all escalated tickets

    Supports filtering by status, channel, and priority
    """
    try:
        async with get_db_connection() as conn:
            # Build query with filters
            where_clauses = ["t.status = 'escalated' OR t.escalated_at IS NOT NULL"]
            params = []
            param_count = 0

            if status:
                param_count += 1
                where_clauses.append(f"t.status = ${param_count}")
                params.append(status)

            if channel:
                param_count += 1
                where_clauses.append(f"t.source_channel = ${param_count}")
                params.append(channel)

            if priority:
                param_count += 1
                where_clauses.append(f"t.priority = ${param_count}")
                params.append(priority)

            where_sql = " AND ".join(where_clauses)

            param_count += 1
            limit_param = f"${param_count}"
            param_count += 1
            offset_param = f"${param_count}"
            params.extend([limit, offset])

            query = f"""
                SELECT
                    t.id,
                    t.customer_id,
                    t.category,
                    t.priority,
                    t.status,
                    t.source_channel,
                    t.escalation_reason,
                    t.created_at,
                    t.escalated_at,
                    c.name as customer_name,
                    c.email as customer_email,
                    CONCAT('TKT-', UPPER(REPLACE(t.id::text, '-', ''))) as ticket_number
                FROM tickets t
                JOIN customers c ON t.customer_id = c.id
                WHERE {where_sql}
                ORDER BY t.escalated_at DESC NULLS LAST, t.created_at DESC
                LIMIT {limit_param} OFFSET {offset_param}
            """

            rows = await conn.fetch(query, *params)

            tickets = []
            for row in rows:
                tickets.append(TicketListItem(
                    id=str(row['id']),
                    ticket_number=row['ticket_number'],
                    customer_id=str(row['customer_id']),
                    customer_name=row['customer_name'] or 'Unknown',
                    customer_email=row['customer_email'] or 'Unknown',
                    category=row['category'] or 'general',
                    priority=row['priority'],
                    status=row['status'],
                    source_channel=row['source_channel'],
                    escalation_reason=row['escalation_reason'],
                    created_at=row['created_at'].isoformat() if row['created_at'] else None,
                    escalated_at=row['escalated_at'].isoformat() if row['escalated_at'] else None
                ))

            return tickets

    except Exception as e:
        logger.error(f"Failed to list tickets: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket_detail(
    ticket_id: str,
    admin: dict = Depends(get_current_admin)
):
    """
    Get detailed ticket information with conversation history
    """
    try:
        async with get_db_connection() as conn:
            # Get ticket details
            ticket = await conn.fetchrow(
                """
                SELECT
                    t.id,
                    t.customer_id,
                    t.conversation_id,
                    t.category,
                    t.priority,
                    t.status,
                    t.source_channel,
                    t.escalation_reason,
                    t.created_at,
                    t.escalated_at,
                    t.resolved_at,
                    t.assigned_to,
                    c.name as customer_name,
                    c.email as customer_email,
                    c.phone as customer_phone,
                    CONCAT('TKT-', UPPER(REPLACE(t.id::text, '-', ''))) as ticket_number
                FROM tickets t
                JOIN customers c ON t.customer_id = c.id
                WHERE t.id = $1
                """,
                ticket_id
            )

            if not ticket:
                raise HTTPException(status_code=404, detail="Ticket not found")

            # Get conversation messages
            messages = []
            if ticket['conversation_id']:
                msg_rows = await conn.fetch(
                    """
                    SELECT
                        id, role, content, channel, direction, created_at
                    FROM messages
                    WHERE conversation_id = $1
                    ORDER BY created_at ASC
                    """,
                    ticket['conversation_id']
                )

                messages = [
                    MessageItem(
                        id=str(row['id']),
                        role=row['role'],
                        content=row['content'],
                        channel=row['channel'],
                        direction=row['direction'],
                        created_at=row['created_at'].isoformat()
                    )
                    for row in msg_rows
                ]

            # Get human responses
            response_rows = await conn.fetch(
                """
                SELECT
                    tr.id,
                    tr.content,
                    tr.sent_via_channel,
                    tr.sent_at,
                    tr.delivery_status,
                    au.name as admin_name,
                    au.email as admin_email
                FROM ticket_responses tr
                JOIN admin_users au ON tr.admin_user_id = au.id
                WHERE tr.ticket_id = $1
                ORDER BY tr.sent_at DESC
                """,
                ticket_id
            )

            responses = [
                {
                    'id': str(row['id']),
                    'content': row['content'],
                    'sent_via_channel': row['sent_via_channel'],
                    'sent_at': row['sent_at'].isoformat(),
                    'delivery_status': row['delivery_status'],
                    'admin_name': row['admin_name'],
                    'admin_email': row['admin_email']
                }
                for row in response_rows
            ]

            # Get internal notes
            note_rows = await conn.fetch(
                """
                SELECT
                    tn.id,
                    tn.note_content,
                    tn.created_at,
                    au.name as admin_name
                FROM ticket_notes tn
                JOIN admin_users au ON tn.admin_user_id = au.id
                WHERE tn.ticket_id = $1
                ORDER BY tn.created_at DESC
                """,
                ticket_id
            )

            notes = [
                {
                    'id': str(row['id']),
                    'note_content': row['note_content'],
                    'created_at': row['created_at'].isoformat(),
                    'admin_name': row['admin_name']
                }
                for row in note_rows
            ]

            return TicketDetailResponse(
                ticket={
                    'id': str(ticket['id']),
                    'ticket_number': ticket['ticket_number'],
                    'customer_id': str(ticket['customer_id']),
                    'customer_name': ticket['customer_name'] or 'Unknown',
                    'customer_email': ticket['customer_email'] or 'Unknown',
                    'customer_phone': ticket['customer_phone'],
                    'category': ticket['category'],
                    'priority': ticket['priority'],
                    'status': ticket['status'],
                    'source_channel': ticket['source_channel'],
                    'escalation_reason': ticket['escalation_reason'],
                    'created_at': ticket['created_at'].isoformat() if ticket['created_at'] else None,
                    'escalated_at': ticket['escalated_at'].isoformat() if ticket['escalated_at'] else None,
                    'resolved_at': ticket['resolved_at'].isoformat() if ticket['resolved_at'] else None,
                    'assigned_to': str(ticket['assigned_to']) if ticket['assigned_to'] else None
                },
                messages=messages,
                responses=responses,
                notes=notes
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get ticket detail: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{ticket_id}/respond")
async def send_response(
    ticket_id: str,
    request: SendResponseRequest,
    admin: dict = Depends(get_current_admin)
):
    """
    Send response to customer

    Response will be routed to correct channel automatically
    """
    try:
        # Import here to avoid circular dependency
        from src.services.response_router import route_admin_response

        async with get_db_connection() as conn:
            # Get ticket info
            ticket = await conn.fetchrow(
                """
                SELECT id, customer_id, source_channel, status
                FROM tickets
                WHERE id = $1
                """,
                ticket_id
            )

            if not ticket:
                raise HTTPException(status_code=404, detail="Ticket not found")

            # Get customer info
            customer = await conn.fetchrow(
                """
                SELECT email, phone, name
                FROM customers
                WHERE id = $1
                """,
                ticket['customer_id']
            )

            # Route response to correct channel
            success = await route_admin_response(
                ticket_id=ticket_id,
                customer_email=customer['email'],
                customer_phone=customer['phone'],
                customer_name=customer['name'],
                channel=ticket['source_channel'],
                response_content=request.content
            )

            if not success:
                raise HTTPException(status_code=500, detail="Failed to send response")

            # Save response to database
            await conn.execute(
                """
                INSERT INTO ticket_responses
                (ticket_id, admin_user_id, content, sent_via_channel, delivery_status)
                VALUES ($1, $2, $3, $4, 'sent')
                """,
                ticket_id,
                admin['id'],
                request.content,
                ticket['source_channel']
            )

            # Update ticket
            await conn.execute(
                """
                UPDATE tickets
                SET
                    last_human_response_at = NOW(),
                    status = CASE WHEN status = 'escalated' THEN 'processing' ELSE status END,
                    assigned_to = $2
                WHERE id = $1
                """,
                ticket_id,
                admin['id']
            )

            logger.info(f"Admin {admin['email']} sent response to ticket {ticket_id}")

            return {
                "success": True,
                "message": "Response sent successfully",
                "channel": ticket['source_channel']
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send response: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: str,
    request: UpdateStatusRequest,
    admin: dict = Depends(get_current_admin)
):
    """
    Update ticket status
    """
    try:
        valid_statuses = ['open', 'escalated', 'processing', 'resolved', 'closed']
        if request.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

        async with get_db_connection() as conn:
            # Update status
            result = await conn.execute(
                """
                UPDATE tickets
                SET
                    status = $2,
                    resolved_at = CASE WHEN $2 = 'resolved' THEN NOW() ELSE resolved_at END
                WHERE id = $1
                """,
                ticket_id,
                request.status
            )

            if result == "UPDATE 0":
                raise HTTPException(status_code=404, detail="Ticket not found")

            logger.info(f"Admin {admin['email']} updated ticket {ticket_id} status to {request.status}")

            return {
                "success": True,
                "message": f"Ticket status updated to {request.status}"
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update ticket status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{ticket_id}/notes")
async def add_internal_note(
    ticket_id: str,
    request: AddNoteRequest,
    admin: dict = Depends(get_current_admin)
):
    """
    Add internal note (not visible to customer)
    """
    try:
        async with get_db_connection() as conn:
            # Verify ticket exists
            ticket_exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM tickets WHERE id = $1)",
                ticket_id
            )

            if not ticket_exists:
                raise HTTPException(status_code=404, detail="Ticket not found")

            # Add note
            note_id = await conn.fetchval(
                """
                INSERT INTO ticket_notes (ticket_id, admin_user_id, note_content)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                ticket_id,
                admin['id'],
                request.note_content
            )

            logger.info(f"Admin {admin['email']} added note to ticket {ticket_id}")

            return {
                "success": True,
                "message": "Note added successfully",
                "note_id": str(note_id)
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add note: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(admin: dict = Depends(get_current_admin)):
    """
    Get admin dashboard statistics
    """
    try:
        async with get_db_connection() as conn:
            # Total escalated tickets
            total_escalated = await conn.fetchval(
                "SELECT COUNT(*) FROM tickets WHERE escalated_at IS NOT NULL"
            )

            # Open escalated tickets
            open_escalated = await conn.fetchval(
                "SELECT COUNT(*) FROM tickets WHERE status = 'escalated'"
            )

            # In progress tickets
            in_progress = await conn.fetchval(
                "SELECT COUNT(*) FROM tickets WHERE status = 'processing' AND escalated_at IS NOT NULL"
            )

            # Resolved today
            resolved_today = await conn.fetchval(
                """
                SELECT COUNT(*) FROM tickets
                WHERE status = 'resolved'
                AND escalated_at IS NOT NULL
                AND resolved_at >= CURRENT_DATE
                """
            )

            # Average response time for escalated tickets
            avg_seconds = await conn.fetchval(
                """
                SELECT AVG(EXTRACT(EPOCH FROM (last_human_response_at - escalated_at)))
                FROM tickets
                WHERE escalated_at IS NOT NULL
                AND last_human_response_at IS NOT NULL
                AND last_human_response_at > escalated_at
                """
            )

            if avg_seconds and avg_seconds > 0:
                if avg_seconds < 3600:
                    avg_minutes = int(avg_seconds / 60)
                    avg_response_time = f"{avg_minutes} minutes"
                else:
                    avg_hours = int(avg_seconds / 3600)
                    avg_response_time = f"{avg_hours} hours"
            else:
                avg_response_time = "N/A"

            return DashboardStatsResponse(
                total_escalated=total_escalated or 0,
                open_escalated=open_escalated or 0,
                in_progress=in_progress or 0,
                resolved_today=resolved_today or 0,
                avg_response_time=avg_response_time
            )

    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
