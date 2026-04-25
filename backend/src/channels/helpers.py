"""
Channel Helper Functions
Wrapper functions for sending emails and WhatsApp messages
"""

from typing import Optional
from src.channels.email_handler import get_gmail_handler
from src.channels.whatsapp_handler import get_whatsapp_handler
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
    from_email: Optional[str] = None
) -> bool:
    """
    Send email via Gmail API

    Args:
        to_email: Recipient email address
        subject: Email subject
        body_text: Plain text email body
        body_html: HTML email body (optional)
        from_email: Sender email (defaults to GMAIL_ADDRESS)

    Returns:
        True if sent successfully
    """
    try:
        handler = get_gmail_handler()

        if body_html:
            # Send HTML email
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from src.config import settings
            import base64

            message = MIMEMultipart('alternative')
            message['To'] = to_email
            message['From'] = from_email or f"Custora Support <{settings.GMAIL_ADDRESS}>"
            message['Subject'] = subject

            # Add both plain text and HTML versions
            part1 = MIMEText(body_text, 'plain', 'utf-8')
            part2 = MIMEText(body_html, 'html', 'utf-8')

            message.attach(part1)
            message.attach(part2)

            # Send via Gmail API
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            if handler.service:
                handler.service.users().messages().send(
                    userId='me',
                    body={'raw': raw_message}
                ).execute()

                logger.info(f"HTML email sent to {to_email}")
                return True
            else:
                logger.error("Gmail service not initialized")
                return False
        else:
            # Send plain text email
            return await handler.send_email(
                to_email=to_email,
                subject=subject,
                body=body_text
            )

    except Exception as e:
        logger.error(f"Failed to send email: {e}", exc_info=True)
        return False


async def send_whatsapp_message(
    to_phone: str,
    message: str
) -> bool:
    """
    Send WhatsApp message via Twilio

    Args:
        to_phone: Recipient phone number (E.164 format)
        message: Message text

    Returns:
        True if sent successfully
    """
    try:
        handler = get_whatsapp_handler()

        if not handler.client:
            logger.error("Twilio client not initialized")
            return False

        from src.config import settings

        # Ensure phone number has + prefix
        if not to_phone.startswith('+'):
            to_phone = f"+{to_phone}"

        # Send via Twilio
        message_obj = handler.client.messages.create(
            from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
            to=f"whatsapp:{to_phone}",
            body=message
        )

        logger.info(f"WhatsApp message sent to {to_phone}, SID: {message_obj.sid}")
        return True

    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {e}", exc_info=True)
        return False
