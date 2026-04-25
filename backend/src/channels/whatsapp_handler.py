"""
WhatsApp Channel Handler - Twilio API Integration
Handles incoming WhatsApp messages and sends responses via Twilio
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from functools import partial

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from twilio.http.http_client import TwilioHttpClient

from src.config import settings
from src.utils.logging import get_logger
from src.database.client import (
    get_customer_by_phone,
    create_customer,
    get_or_create_customer_identifier,
    create_conversation,
    get_active_conversation,
    create_message,
)

logger = get_logger(__name__)


class WhatsAppHandler:
    """
    Twilio WhatsApp handler for WhatsApp channel.
    Receives webhooks and sends messages via Twilio API.
    """

    def __init__(self):
        """Initialize WhatsApp handler with Twilio client."""
        self.client: Optional[Client] = None
        self._initialize_twilio_client()

    def _initialize_twilio_client(self) -> None:
        """Initialize Twilio client with credentials and timeout configuration."""
        try:
            if not settings.WHATSAPP_ENABLED:
                logger.warning("WhatsApp integration is disabled in settings")
                return

            if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
                logger.warning("Twilio credentials not configured")
                return

            # Create HTTP client with timeout configuration
            http_client = TwilioHttpClient(timeout=60)  # 60 second timeout

            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN,
                http_client=http_client
            )

            logger.info("Twilio WhatsApp client initialized successfully with 60s timeout")

        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {e}", exc_info=True)
            raise

    def _generate_subject_from_message(self, body: str) -> str:
        """
        Generate a meaningful subject line from WhatsApp message content.

        Args:
            body: Message body text

        Returns:
            Generated subject (max 100 chars)
        """
        # Clean the message
        clean_body = body.strip()

        # Remove media attachment text
        if '[' in clean_body and 'media attachment' in clean_body:
            clean_body = clean_body.split('[')[0].strip()

        # Take first 100 chars or first sentence
        if len(clean_body) <= 100:
            return clean_body

        # Try to find first sentence
        for delimiter in ['. ', '! ', '? ', '\n']:
            if delimiter in clean_body[:100]:
                subject = clean_body.split(delimiter)[0] + delimiter.strip()
                if len(subject) <= 100:
                    return subject

        # Fallback: truncate at 97 chars and add ellipsis
        return clean_body[:97] + "..."

    async def process_incoming_message(
        self,
        from_number: str,
        to_number: str,
        body: str,
        message_sid: str,
        profile_name: Optional[str] = None,
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process incoming WhatsApp message from Twilio webhook.

        Args:
            from_number: Sender's WhatsApp number (whatsapp:+1234567890)
            to_number: Recipient's WhatsApp number (our number)
            body: Message body text
            message_sid: Twilio message SID
            media_urls: List of media URLs if any

        Returns:
            Processing result with customer_id and conversation_id
        """
        try:
            # Remove 'whatsapp:' prefix from phone numbers
            clean_from = from_number.replace('whatsapp:', '')
            clean_to = to_number.replace('whatsapp:', '')

            logger.info(f"Processing WhatsApp message from {clean_from}")

            # Get or create customer by phone
            customer = await get_customer_by_phone(clean_from)

            if not customer:
                # Use ProfileName from Twilio or fallback to phone-based name
                if profile_name and profile_name.strip():
                    customer_name = profile_name.strip()
                else:
                    customer_name = f"WhatsApp User {clean_from[-4:]}"

                customer_id = await create_customer(
                    email=None,
                    phone=clean_from,
                    name=customer_name,
                )
                logger.info(f"Created new customer: {customer_id}")
            else:
                customer_id = str(customer['id'])

            # Ensure customer identifier exists
            await get_or_create_customer_identifier(
                customer_id=customer_id,
                identifier_type='phone',
                identifier_value=clean_from,
            )

            # Also create WhatsApp identifier
            await get_or_create_customer_identifier(
                customer_id=customer_id,
                identifier_type='whatsapp',
                identifier_value=clean_from,
            )

            # Get or create conversation
            conversation = await get_active_conversation(customer_id)

            if not conversation:
                conversation_id = await create_conversation(
                    customer_id=customer_id,
                    channel='whatsapp',
                )
                logger.info(f"Created new conversation: {conversation_id}")
            else:
                conversation_id = str(conversation['id'])

            # Generate subject from message content
            subject = self._generate_subject_from_message(body)

            # Prepare metadata
            metadata = {
                'twilio_message_sid': message_sid,
                'from_number': clean_from,
                'to_number': clean_to,
                'subject': subject,
            }

            if profile_name:
                metadata['profile_name'] = profile_name

            if media_urls:
                metadata['media_urls'] = media_urls
                body += f"\n[{len(media_urls)} media attachment(s)]"

            # Create message record
            message_id = await create_message(
                conversation_id=conversation_id,
                role='customer',
                content=body,
                channel='whatsapp',
                direction='inbound',
                channel_message_id=message_sid,
                metadata=metadata
            )

            logger.info(f"WhatsApp message processed successfully", extra={
                'customer_id': customer_id,
                'conversation_id': conversation_id,
                'message_id': message_id
            })

            return {
                'customer_id': customer_id,
                'conversation_id': conversation_id,
                'message_id': message_id,
                'from_number': clean_from,
                'body': body,
            }

        except Exception as e:
            logger.error(f"Failed to process WhatsApp message: {e}", exc_info=True)
            raise

    async def send_message(
        self,
        to_number: str,
        body: str,
        media_url: Optional[str] = None,
        max_retries: int = 3
    ) -> bool:
        """
        Send WhatsApp message via Twilio API with retry logic.

        Args:
            to_number: Recipient's phone number (without whatsapp: prefix)
            body: Message body text (max 1600 chars for WhatsApp)
            media_url: Optional media URL to send
            max_retries: Maximum number of retry attempts

        Returns:
            True if sent successfully
        """
        if not self.client:
            logger.error("Twilio client not initialized, cannot send WhatsApp message")
            return False

        # Ensure phone number has whatsapp: prefix
        if not to_number.startswith('whatsapp:'):
            to_number = f'whatsapp:{to_number}'

        from_number = f'whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}'

        # Truncate body if too long (WhatsApp limit is 1600 chars)
        if len(body) > 1600:
            body = body[:1597] + "..."
            logger.warning("Message truncated to 1600 chars for WhatsApp")

        # Prepare message parameters
        message_params = {
            'from_': from_number,
            'to': to_number,
            'body': body,
        }

        if media_url:
            message_params['media_url'] = [media_url]

        # Retry logic
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Sending WhatsApp message to {to_number} (attempt {attempt}/{max_retries})")

                # Run blocking Twilio call in thread pool to avoid blocking event loop
                loop = asyncio.get_event_loop()
                message = await loop.run_in_executor(
                    None,
                    partial(self.client.messages.create, **message_params)
                )

                logger.info(f"WhatsApp message sent successfully", extra={
                    'message_sid': message.sid,
                    'status': message.status,
                    'attempt': attempt
                })

                return True

            except TwilioRestException as e:
                logger.error(f"Twilio API error (attempt {attempt}/{max_retries}): {e.code} - {e.msg}")

                # Don't retry on certain errors
                if e.code in [21211, 21614, 63007]:  # Invalid number, unsubscribed, not in sandbox
                    logger.error(f"Non-retryable Twilio error: {e.code}")
                    return False

                if attempt < max_retries:
                    wait_time = attempt * 2  # Exponential backoff: 2s, 4s, 6s
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries} attempts failed")
                    return False

            except Exception as e:
                logger.error(f"Failed to send WhatsApp message (attempt {attempt}/{max_retries}): {e}", exc_info=True)

                if attempt < max_retries:
                    wait_time = attempt * 2
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries} attempts failed")
                    return False

        return False

    async def send_response(
        self,
        conversation_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Save agent response message to database for WhatsApp channel.

        Args:
            conversation_id: Conversation ID
            content: Response content
            metadata: Additional metadata

        Returns:
            Created message record
        """
        try:
            logger.info(f"Saving WhatsApp response to conversation {conversation_id}")

            # Prepare metadata
            msg_metadata = metadata or {}
            msg_metadata['source'] = 'whatsapp'
            msg_metadata['ai_generated'] = True

            # Create message record
            message_id = await create_message(
                conversation_id=conversation_id,
                role='agent',
                content=content,
                channel='whatsapp',
                direction='outbound',
                metadata=msg_metadata
            )

            logger.info(f"WhatsApp response saved successfully", extra={
                'message_id': message_id
            })

            return {
                'message_id': message_id,
                'content': content
            }

        except Exception as e:
            logger.error(f"Failed to save WhatsApp response: {e}", exc_info=True)
            raise

    def validate_webhook_signature(
        self,
        url: str,
        params: Dict[str, str],
        signature: str
    ) -> bool:
        """
        Validate Twilio webhook signature for security.

        Args:
            url: Full webhook URL
            params: POST parameters from webhook
            signature: X-Twilio-Signature header value

        Returns:
            True if signature is valid
        """
        try:
            from twilio.request_validator import RequestValidator

            validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
            return validator.validate(url, params, signature)

        except Exception as e:
            logger.error(f"Failed to validate webhook signature: {e}", exc_info=True)
            return False


# Global handler instance
_whatsapp_handler: Optional[WhatsAppHandler] = None


def get_whatsapp_handler() -> WhatsAppHandler:
    """
    Get or create global WhatsApp handler instance.

    Returns:
        WhatsAppHandler instance
    """
    global _whatsapp_handler

    if _whatsapp_handler is None:
        _whatsapp_handler = WhatsAppHandler()

    return _whatsapp_handler
