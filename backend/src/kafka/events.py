"""
Kafka Event Schemas - Pydantic Models for Events
Defines structure for all Kafka events
"""

from typing import Dict, Optional, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================
# Base Event Schema
# ============================================

class BaseEvent(BaseModel):
    """Base event schema with common fields."""
    event_id: str = Field(..., description="Unique event ID (UUID)")
    event_type: str = Field(..., description="Event type identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for request tracking")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


# ============================================
# Message Events
# ============================================

class MessageReceivedEvent(BaseEvent):
    """Event published when a new message is received from any channel."""
    event_type: Literal["message.received"] = "message.received"

    # Message details
    message_id: int = Field(..., description="Database message ID")
    conversation_id: int = Field(..., description="Conversation ID")
    customer_id: int = Field(..., description="Customer ID")

    # Content
    content: str = Field(..., description="Message content")
    channel: Literal["email", "whatsapp", "webform"] = Field(..., description="Channel")
    sender_type: Literal["customer", "agent", "system"] = Field(..., description="Sender type")

    # Channel-specific metadata
    channel_metadata: Optional[Dict[str, Any]] = Field(None, description="Channel-specific data")


class MessageSentEvent(BaseEvent):
    """Event published when a message is sent to customer."""
    event_type: Literal["message.sent"] = "message.sent"

    # Message details
    message_id: int = Field(..., description="Database message ID")
    conversation_id: int = Field(..., description="Conversation ID")
    customer_id: int = Field(..., description="Customer ID")

    # Content
    content: str = Field(..., description="Message content")
    channel: Literal["email", "whatsapp", "webform"] = Field(..., description="Channel")

    # Delivery status
    delivery_status: Literal["sent", "delivered", "failed"] = Field("sent", description="Delivery status")
    delivery_metadata: Optional[Dict[str, Any]] = Field(None, description="Delivery details")


# ============================================
# Escalation Events
# ============================================

class EscalationCreatedEvent(BaseEvent):
    """Event published when conversation is escalated to human."""
    event_type: Literal["escalation.created"] = "escalation.created"

    conversation_id: int = Field(..., description="Conversation ID")
    customer_id: int = Field(..., description="Customer ID")
    reason: str = Field(..., description="Escalation reason")
    urgency: Literal["normal", "high", "critical"] = Field(..., description="Urgency level")

    # Context
    channel: Literal["email", "whatsapp", "webform"] = Field(..., description="Channel")
    trigger: str = Field(..., description="What triggered escalation")


# ============================================
# Ticket Events
# ============================================

class TicketCreatedEvent(BaseEvent):
    """Event published when a support ticket is created."""
    event_type: Literal["ticket.created"] = "ticket.created"

    ticket_id: int = Field(..., description="Ticket ID")
    conversation_id: int = Field(..., description="Conversation ID")
    customer_id: int = Field(..., description="Customer ID")

    subject: str = Field(..., description="Ticket subject")
    priority: Literal["low", "medium", "high", "urgent"] = Field(..., description="Priority")
    category: str = Field(..., description="Ticket category")
    status: str = Field(..., description="Ticket status")


# ============================================
# Agent Events
# ============================================

class AgentExecutionCompletedEvent(BaseEvent):
    """Event published when agent completes processing."""
    event_type: Literal["agent.execution.completed"] = "agent.execution.completed"

    conversation_id: int = Field(..., description="Conversation ID")
    customer_id: int = Field(..., description="Customer ID")
    message_id: int = Field(..., description="Message ID processed")

    execution_time: float = Field(..., description="Execution time in seconds")
    tools_used: list[str] = Field(default_factory=list, description="Tools called by agent")
    success: bool = Field(..., description="Whether execution succeeded")
    error: Optional[str] = Field(None, description="Error message if failed")


# ============================================
# Event Type Registry
# ============================================

EVENT_SCHEMAS = {
    "message.received": MessageReceivedEvent,
    "message.sent": MessageSentEvent,
    "escalation.created": EscalationCreatedEvent,
    "ticket.created": TicketCreatedEvent,
    "agent.execution.completed": AgentExecutionCompletedEvent,
}
