"""
Channel API Endpoints - FastAPI Routes
Integrates channel handlers with OpenAI agent
"""

import json
from typing import Optional, Dict, Any, AsyncIterator
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Header, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, EmailStr

from src.utils.logging import get_logger
from src.channels.email_handler import get_gmail_handler
from src.channels.whatsapp_handler import get_whatsapp_handler
from src.channels.webform_handler import get_webform_handler
from src.agent.runner import process_customer_message
from src.agent.dual_mode_router import get_router
from src.kafka.helpers import (
    publish_message_received,
    publish_message_sent,
    publish_agent_execution_completed,
)
from src.config import settings

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/channels", tags=["channels"])


# ============================================
# Request/Response Models
# ============================================

class WebFormMessageRequest(BaseModel):
    """Web form message request."""
    email: EmailStr = Field(..., description="Customer's email address")
    name: str = Field(..., min_length=1, max_length=100, description="Customer's name")
    subject: str = Field(..., min_length=1, max_length=200, description="Issue subject/title")
    category: str = Field(..., description="Issue category (order_status, shipping, returns, payment, account, product, general)")
    priority: str = Field(..., description="Priority level (low, medium, high, urgent)")
    message: str = Field(..., min_length=1, max_length=5000, description="Message content")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID (UUID)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class WebFormMessageResponse(BaseModel):
    """Web form message response."""
    success: bool
    conversation_id: str  # UUID
    customer_id: str  # UUID
    message_id: str  # UUID
    agent_response: str
    execution_time: float


class WhatsAppWebhookRequest(BaseModel):
    """Twilio WhatsApp webhook request."""
    MessageSid: str
    From: str  # whatsapp:+1234567890
    To: str
    Body: str
    NumMedia: Optional[str] = "0"
    MediaUrl0: Optional[str] = None


class ChannelStatusResponse(BaseModel):
    """Channel status response."""
    channel: str
    enabled: bool
    status: str
    details: Optional[Dict[str, Any]] = None


# ============================================
# Web Form Endpoints
# ============================================

@router.post("/webform/message", response_model=WebFormMessageResponse)
async def webform_message_endpoint(
    request: WebFormMessageRequest,
    background_tasks: BackgroundTasks,
) -> WebFormMessageResponse:
    """
    Process message from web form and return agent response.

    This endpoint:
    1. Creates/retrieves customer and conversation
    2. Saves customer message to database
    3. Processes message through AI agent
    4. Returns agent response
    """
    start_time = datetime.utcnow()

    try:
        logger.info(f"Web form message received from {request.email}")

        # Get handler
        handler = get_webform_handler()

        # Process incoming message
        result = await handler.process_message(
            email=request.email,
            name=request.name,
            subject=request.subject,
            category=request.category,
            priority=request.priority,
            message=request.message,
            conversation_id=request.conversation_id,
            metadata=request.metadata,
        )

        customer_id = result['customer_id']
        conversation_id = result['conversation_id']

        # Process through agent
        agent_result = await process_customer_message(
            user_input=request.message,
            customer_id=customer_id,
            conversation_id=conversation_id,
            channel='webform',
            context=request.metadata,
            streaming=False,
        )

        # Save agent response
        response_msg = await handler.send_response(
            conversation_id=conversation_id,
            content=agent_result['final_output'],
            metadata={'execution_time': agent_result['execution_time']},
        )

        # Publish message.sent event (fire and forget)
        if settings.KAFKA_ENABLED:
            background_tasks.add_task(
                publish_message_sent,
                message_id=response_msg['message_id'],
                conversation_id=conversation_id,
                customer_id=customer_id,
                content=agent_result['final_output'],
                channel='webform',
            )

        # Publish agent.execution.completed event
        if settings.KAFKA_ENABLED:
            background_tasks.add_task(
                publish_agent_execution_completed,
                conversation_id=conversation_id,
                customer_id=customer_id,
                message_id=result['message_id'],
                execution_time=agent_result['execution_time'],
                tools_used=[],  # TODO: Track tools used in agent
                success=True,
            )

        execution_time = (datetime.utcnow() - start_time).total_seconds()

        logger.info(f"Web form message processed successfully", extra={
            'customer_id': customer_id,
            'conversation_id': conversation_id,
            'execution_time': execution_time,
        })

        return WebFormMessageResponse(
            success=True,
            conversation_id=conversation_id,
            customer_id=customer_id,
            message_id=result['message_id'],
            agent_response=agent_result['final_output'],
            execution_time=execution_time,
        )

    except Exception as e:
        logger.error(f"Web form message processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.post("/webform/message/stream")
async def webform_message_stream_endpoint(
    request: WebFormMessageRequest,
) -> StreamingResponse:
    """
    Process message from web form with streaming response.

    Returns Server-Sent Events (SSE) stream with:
    - thinking: When agent is using tools
    - text: Text deltas as they're generated
    - done: Final completion with metadata
    """

    async def event_generator() -> AsyncIterator[str]:
        """Generate SSE events from agent stream."""
        try:
            print(f"[DEBUG] event_generator started for {request.email}", flush=True)
            logger.info(f"Web form streaming message from {request.email}")

            # Get handler
            handler = get_webform_handler()

            # Process incoming message (save to DB)
            result = await handler.process_message(
                email=request.email,
                name=request.name,
                subject=request.subject,
                category=request.category,
                priority=request.priority,
                message=request.message,
                conversation_id=request.conversation_id,
                metadata=request.metadata,
            )

            customer_id = result['customer_id']
            conversation_id = result['conversation_id']
            message_id = result['message_id']
            ticket_id = result.get('ticket_id')  # May be None
            ticket_number = result.get('ticket_number')  # May be None

            # Send initial event with IDs
            yield f"event: start\n"
            yield f"data: {json.dumps({'conversation_id': conversation_id, 'customer_id': customer_id, 'message_id': message_id})}\n\n"

            # Send ticket created event only if ticket was pre-created
            if ticket_id and ticket_number:
                yield f"event: ticket_created\n"
                yield f"data: {json.dumps({'ticket_id': ticket_id, 'ticket_number': ticket_number})}\n\n"

            # Get router and run agent
            from src.agent.dual_mode_router import get_router as get_router_fresh
            router = get_router_fresh()

            agent_stream = router.run_streamed(
                user_input=request.message,
                customer_id=customer_id,
                conversation_id=conversation_id,
                channel='webform',
                context=request.metadata,
            )

            full_response = ""

            # Stream agent events
            async for event in agent_stream:
                event_type = event.get('type', 'unknown')
                logger.info(f"Received event from agent: {event_type} [cid: {conversation_id[:8]}]")

                if event['type'] == 'mode':
                    # Agent mode indicator (OpenAI primary, Groq fallback, etc.)
                    mode = event['data'].get('mode', 'unknown')
                    status = event['data'].get('status', 'unknown')
                    reason = event['data'].get('reason', '')

                    mode_display = {
                        'openai': '🤖 OpenAI GPT-4o-mini',
                        'groq': '⚡ Groq Llama 3.3 70B',
                    }
                    display_name = mode_display.get(mode, mode)

                    status_msg = f"Using {display_name}"
                    if status == 'fallback':
                        status_msg = f"Switched to {display_name} (fallback)"

                    yield f"event: mode\n"
                    yield f"data: {json.dumps({'mode': mode, 'status': status, 'display': status_msg, 'reason': reason})}\n\n"

                elif event['type'] == 'text_delta':
                    # Stream text chunks
                    text = event['data']
                    full_response += text
                    yield f"event: text\n"
                    yield f"data: {json.dumps({'content': text})}\n\n"

                elif event['type'] == 'tool_call':
                    # Show thinking status
                    tool_name = event['data'].get('tool_name', 'unknown')
                    tool_display = {
                        'search_knowledge_base': 'Searching knowledge base...',
                        'create_ticket': 'Creating support ticket...',
                        'get_customer_history': 'Retrieving your history...',
                        'escalate_to_human': 'Escalating to human agent...',
                        'send_response': 'Preparing response...',
                    }
                    status = tool_display.get(tool_name, f'Using {tool_name}...')

                    yield f"event: thinking\n"
                    yield f"data: {json.dumps({'tool': tool_name, 'status': status})}\n\n"

                elif event['type'] == 'tool_output':
                    # Tool completed
                    yield f"event: tool_complete\n"
                    yield f"data: {json.dumps({'output': 'Tool completed'})}\n\n"

                elif event['type'] == 'final':
                    # Agent finished - map to "done" for frontend
                    final_output = event['data']['final_output']
                    execution_time = event['data']['execution_time']

                    # Save agent response to DB
                    response_msg = await handler.send_response(
                        conversation_id=conversation_id,
                        content=final_output,
                        metadata={'execution_time': execution_time, 'streamed': True},
                    )

                    # Send completion event as "done" (frontend expects this)
                    yield f"event: done\n"
                    yield f"data: {json.dumps({'conversation_id': conversation_id, 'message_id': response_msg['message_id'], 'execution_time': execution_time})}\n\n"

            logger.info(f"Streaming completed for conversation {conversation_id}")

        except Exception as e:
            logger.error(f"Streaming failed: {e}", exc_info=True)
            yield f"event: error\n"
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


# ============================================
# WhatsApp Endpoints
# ============================================

@router.post("/whatsapp/webhook")
async def whatsapp_webhook_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    x_twilio_signature: Optional[str] = Header(None),
) -> Dict[str, str]:
    """
    Twilio WhatsApp webhook endpoint.

    Receives incoming WhatsApp messages from Twilio and processes them.
    Responds with TwiML (empty response to acknowledge receipt).
    """
    try:
        # Get form data
        form_data = await request.form()
        params = dict(form_data)

        logger.info(f"WhatsApp webhook received from {params.get('From')}")

        # Validate webhook signature (security)
        handler = get_whatsapp_handler()

        # In production, validate signature
        # if x_twilio_signature:
        #     url = str(request.url)
        #     if not handler.validate_webhook_signature(url, params, x_twilio_signature):
        #         logger.warning("Invalid Twilio webhook signature")
        #         raise HTTPException(status_code=403, detail="Invalid signature")

        # Extract message data
        message_sid = params.get('MessageSid')
        from_number = params.get('From')
        to_number = params.get('To')
        body = params.get('Body', '')
        profile_name = params.get('ProfileName')  # Sender's WhatsApp profile name
        num_media = int(params.get('NumMedia', 0))

        # Get media URLs if any
        media_urls = []
        for i in range(num_media):
            media_url = params.get(f'MediaUrl{i}')
            if media_url:
                media_urls.append(media_url)

        # Process message in background
        background_tasks.add_task(
            process_whatsapp_message,
            from_number=from_number,
            to_number=to_number,
            body=body,
            message_sid=message_sid,
            profile_name=profile_name,
            media_urls=media_urls if media_urls else None,
        )

        # Return empty TwiML response (acknowledge receipt)
        return {"status": "received"}

    except Exception as e:
        logger.error(f"WhatsApp webhook processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def process_whatsapp_message(
    from_number: str,
    to_number: str,
    body: str,
    message_sid: str,
    profile_name: Optional[str] = None,
    media_urls: Optional[list] = None,
) -> None:
    """
    Background task to process WhatsApp message through agent.

    Args:
        from_number: Sender's WhatsApp number
        to_number: Recipient's WhatsApp number
        body: Message body
        message_sid: Twilio message SID
        profile_name: Sender's WhatsApp profile name
        media_urls: List of media URLs
    """
    try:
        # Get handler
        handler = get_whatsapp_handler()

        # Process incoming message
        result = await handler.process_incoming_message(
            from_number=from_number,
            to_number=to_number,
            body=body,
            message_sid=message_sid,
            profile_name=profile_name,
            media_urls=media_urls,
        )

        customer_id = result['customer_id']
        conversation_id = result['conversation_id']

        # Publish message.received event
        if settings.KAFKA_ENABLED:
            await publish_message_received(
                message_id=result['message_id'],
                conversation_id=conversation_id,
                customer_id=customer_id,
                content=body,
                channel='whatsapp',
                sender_type='customer',
                channel_metadata={'message_sid': message_sid, 'media_urls': media_urls},
            )

        # Process through agent
        agent_result = await process_customer_message(
            user_input=body,
            customer_id=customer_id,
            conversation_id=conversation_id,
            channel='whatsapp',
            streaming=False,
        )

        # Save agent response to database first
        response_msg = await handler.send_response(
            conversation_id=conversation_id,
            content=agent_result['final_output'],
            metadata={'execution_time': agent_result['execution_time']},
        )

        # Send response via WhatsApp
        clean_from = from_number.replace('whatsapp:', '')
        success = await handler.send_message(
            to_number=clean_from,
            body=agent_result['final_output'],
        )

        # Publish message.sent event
        if settings.KAFKA_ENABLED:
            await publish_message_sent(
                message_id=result['message_id'],
                conversation_id=conversation_id,
                customer_id=customer_id,
                content=agent_result['final_output'],
                channel='whatsapp',
                delivery_status='sent' if success else 'failed',
            )

        # Publish agent.execution.completed event
        if settings.KAFKA_ENABLED:
            await publish_agent_execution_completed(
                conversation_id=conversation_id,
                customer_id=customer_id,
                message_id=result['message_id'],
                execution_time=agent_result['execution_time'],
                tools_used=[],
                success=True,
            )

        logger.info(f"WhatsApp message processed and response sent", extra={
            'customer_id': customer_id,
            'conversation_id': conversation_id,
        })

    except Exception as e:
        logger.error(f"Failed to process WhatsApp message in background: {e}", exc_info=True)


# ============================================
# Email Endpoints (Polling-based)
# ============================================

@router.post("/email/poll")
async def email_poll_endpoint(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Poll Gmail for new emails and process them.

    This endpoint should be called periodically (e.g., every 30 seconds)
    by a cron job or scheduler.
    """
    try:
        logger.info("Email polling triggered")

        # Get handler
        handler = get_gmail_handler()

        # Poll for new emails
        emails = await handler.poll_new_emails()

        if not emails:
            return {
                "status": "success",
                "emails_found": 0,
                "message": "No new emails"
            }

        logger.info(f"Found {len(emails)} new emails")

        # Process each email in background
        for email_data in emails:
            background_tasks.add_task(
                process_email_message,
                email_data=email_data,
            )

        return {
            "status": "success",
            "emails_found": len(emails),
            "message": f"Processing {len(emails)} emails"
        }

    except Exception as e:
        logger.error(f"Email polling failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def process_email_message(email_data: Dict[str, Any]) -> None:
    """
    Background task to process email through agent.

    Args:
        email_data: Parsed email data
    """
    try:
        # Get handler
        handler = get_gmail_handler()

        # Process incoming email
        result = await handler.process_email(email_data)

        customer_id = result['customer_id']
        conversation_id = result['conversation_id']

        # Publish message.received event
        if settings.KAFKA_ENABLED:
            await publish_message_received(
                message_id=result['message_id'],
                conversation_id=conversation_id,
                customer_id=customer_id,
                content=email_data['body'],
                channel='email',
                sender_type='customer',
                channel_metadata={'subject': email_data['subject'], 'gmail_message_id': email_data['message_id']},
            )

        # Process through agent
        agent_result = await process_customer_message(
            user_input=email_data['body'],
            customer_id=customer_id,
            conversation_id=conversation_id,
            channel='email',
            streaming=False,
        )

        # Send email response
        success = await handler.send_email(
            to_email=email_data['from'],
            subject=email_data['subject'],
            body=agent_result['final_output'],
            thread_id=email_data.get('thread_id'),
            in_reply_to=email_data.get('email_message_id'),  # For proper threading
        )

        # Publish message.sent event
        if settings.KAFKA_ENABLED:
            await publish_message_sent(
                message_id=result['message_id'],
                conversation_id=conversation_id,
                customer_id=customer_id,
                content=agent_result['final_output'],
                channel='email',
                delivery_status='sent' if success else 'failed',
            )

        # Publish agent.execution.completed event
        if settings.KAFKA_ENABLED:
            await publish_agent_execution_completed(
                conversation_id=conversation_id,
                customer_id=customer_id,
                message_id=result['message_id'],
                execution_time=agent_result['execution_time'],
                tools_used=[],
                success=True,
            )

        logger.info(f"Email processed and response sent", extra={
            'customer_id': customer_id,
            'conversation_id': conversation_id,
        })

    except Exception as e:
        logger.error(f"Failed to process email in background: {e}", exc_info=True)


# ============================================
# Channel Status Endpoints
# ============================================

@router.get("/status", response_model=Dict[str, ChannelStatusResponse])
async def channels_status_endpoint() -> Dict[str, ChannelStatusResponse]:
    """
    Get status of all channels.

    Returns:
        Status information for email, WhatsApp, and web form channels
    """
    from src.config import settings

    status = {}

    # Email status
    email_handler = get_gmail_handler()
    status['email'] = ChannelStatusResponse(
        channel='email',
        enabled=settings.GMAIL_ENABLED,
        status='ready' if email_handler.service else 'not_configured',
        details={
            'address': settings.GMAIL_ADDRESS if settings.GMAIL_ENABLED else None,
        }
    )

    # WhatsApp status
    whatsapp_handler = get_whatsapp_handler()
    status['whatsapp'] = ChannelStatusResponse(
        channel='whatsapp',
        enabled=settings.WHATSAPP_ENABLED,
        status='ready' if whatsapp_handler.client else 'not_configured',
        details={
            'number': settings.TWILIO_WHATSAPP_NUMBER if settings.WHATSAPP_ENABLED else None,
        }
    )

    # Web form status
    status['webform'] = ChannelStatusResponse(
        channel='webform',
        enabled=settings.WEBFORM_ENABLED,
        status='ready',
        details={
            'endpoint': '/api/v1/channels/webform/message',
        }
    )

    return status
