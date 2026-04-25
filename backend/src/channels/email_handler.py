"""
Email Channel Handler - Gmail API Integration
Handles incoming emails and sends responses via Gmail API
"""

import base64
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.config import settings
from src.utils.logging import get_logger
from src.database.client import (
    get_customer_by_email,
    create_customer,
    get_or_create_customer_identifier,
    create_conversation,
    get_active_conversation,
    create_message,
)

logger = get_logger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


class GmailHandler:
    """
    Gmail API handler for email channel.
    Polls for new emails and sends responses.
    """

    def __init__(self):
        """Initialize Gmail handler."""
        self.service = None
        self.credentials = None
        self._initialize_gmail_service()

    def _initialize_gmail_service(self) -> None:
        """Initialize Gmail API service with OAuth2 credentials."""
        try:
            if not settings.GMAIL_ENABLED:
                logger.warning("Gmail integration is disabled in settings")
                return

            # Load credentials from .env
            if not settings.GMAIL_CREDENTIALS_JSON or not settings.GMAIL_TOKEN_JSON:
                logger.error("Gmail credentials not configured in .env")
                return

            logger.info("Initializing Gmail service with OAuth credentials")

            # Parse token JSON from .env
            import json
            token_data = json.loads(settings.GMAIL_TOKEN_JSON)

            # Create credentials object
            self.credentials = Credentials(
                token=token_data.get('token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes', SCOPES)
            )

            # Refresh token if expired
            if self.credentials.expired and self.credentials.refresh_token:
                logger.info("Access token expired, refreshing...")
                self.credentials.refresh(Request())
                logger.info("Access token refreshed successfully")

            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=self.credentials)

            logger.info("Gmail service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Gmail service: {e}", exc_info=True)
            raise

    async def poll_new_emails(self) -> List[Dict[str, Any]]:
        """
        Poll Gmail for new unread emails to support address.

        Returns:
            List of new email messages
        """
        if not self.service:
            logger.warning("Gmail service not initialized, skipping poll")
            return []

        try:
            logger.info("Polling Gmail for new emails")

            # Query for unread emails to support address
            query = f"to:{settings.GMAIL_ADDRESS} is:unread"

            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                logger.debug("No new emails found")
                return []

            logger.info(f"Found {len(messages)} new emails")

            # Fetch full message details
            email_messages = []
            for msg in messages:
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()

                email_messages.append(self._parse_email_message(message))

            return email_messages

        except HttpError as e:
            logger.error(f"Gmail API error: {e}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"Failed to poll emails: {e}", exc_info=True)
            return []

    def _parse_email_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Gmail API message into structured format.

        Args:
            message: Gmail API message object

        Returns:
            Parsed email data
        """
        headers = message['payload']['headers']

        # Extract headers
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        from_email = next((h['value'] for h in headers if h['name'] == 'From'), '')
        to_email = next((h['value'] for h in headers if h['name'] == 'To'), '')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        message_id = next((h['value'] for h in headers if h['name'] == 'Message-ID'), None)

        # Extract email address and name from "Name <email@example.com>" format
        import re
        email_match = re.search(r'<(.+?)>', from_email)
        sender_email = email_match.group(1) if email_match else from_email

        # Extract sender name
        sender_name = self._extract_name_from_header(from_email, sender_email)

        # Extract body
        body = self._get_email_body(message['payload'])

        return {
            'message_id': message['id'],
            'thread_id': message['threadId'],
            'subject': subject,
            'from': sender_email,
            'from_name': sender_name,
            'to': to_email,
            'date': date,
            'body': body,
            'snippet': message.get('snippet', ''),
            'email_message_id': message_id,  # RFC 822 Message-ID for threading
        }

    def _get_email_body(self, payload: Dict[str, Any]) -> str:
        """
        Extract email body from Gmail message payload.

        Args:
            payload: Gmail message payload

        Returns:
            Email body text
        """
        if 'body' in payload and 'data' in payload['body']:
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    # Fallback to HTML if plain text not available
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')

        return ""

    def _extract_name_from_header(self, from_header: str, email_address: str) -> str:
        """
        Extract sender name from email From header.

        Args:
            from_header: Full From header (e.g., "John Doe <john@example.com>")
            email_address: Extracted email address

        Returns:
            Sender name or fallback
        """
        import re

        # Try to extract name from "Name <email>" format
        name_match = re.match(r'^(.+?)\s*<.+>$', from_header.strip())
        if name_match:
            name = name_match.group(1).strip()
            # Remove quotes if present
            name = name.strip('"').strip("'")
            if name:
                return name

        # Fallback: use email username part
        username = email_address.split('@')[0]
        # Convert dots/underscores to spaces and title case
        name = username.replace('.', ' ').replace('_', ' ').title()
        return name

    async def process_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming email and create database records.

        Args:
            email_data: Parsed email data

        Returns:
            Processing result with customer_id and conversation_id
        """
        try:
            logger.info(f"Processing email from {email_data['from']}")

            # Get or create customer
            customer = await get_customer_by_email(email_data['from'])

            if not customer:
                # Use extracted name from email header
                name = email_data.get('from_name', 'Unknown')

                customer_id = await create_customer(
                    email=email_data['from'],
                    phone=None,
                    name=name,
                )
                logger.info(f"Created new customer: {customer_id}")
            else:
                customer_id = str(customer['id'])

            # Ensure customer identifier exists
            await get_or_create_customer_identifier(
                customer_id=customer_id,
                identifier_type='email',
                identifier_value=email_data['from'],
            )

            # Get or create conversation
            conversation = await get_active_conversation(customer_id)

            if not conversation:
                conversation_id = await create_conversation(
                    customer_id=customer_id,
                    channel='email',
                )
                logger.info(f"Created new conversation: {conversation_id}")
            else:
                conversation_id = str(conversation['id'])

            # Create message record
            message_id = await create_message(
                conversation_id=conversation_id,
                role='customer',
                content=email_data['body'],
                channel='email',
                direction='inbound',
                channel_message_id=email_data['message_id'],
                metadata={
                    'subject': email_data['subject'],
                    'gmail_thread_id': email_data['thread_id'],
                }
            )

            logger.info(f"Email processed successfully", extra={
                'customer_id': customer_id,
                'conversation_id': conversation_id,
                'message_id': message_id
            })

            # Mark email as read
            if self.service:
                self._mark_as_read(email_data['message_id'])

            return {
                'customer_id': customer_id,
                'conversation_id': conversation_id,
                'message_id': message_id,
                'email_data': email_data,
            }

        except Exception as e:
            logger.error(f"Failed to process email: {e}", exc_info=True)
            raise

    def _mark_as_read(self, message_id: str) -> None:
        """Mark Gmail message as read."""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            logger.debug(f"Marked email {message_id} as read")
        except Exception as e:
            logger.warning(f"Failed to mark email as read: {e}")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        thread_id: Optional[str] = None,
        in_reply_to: Optional[str] = None
    ) -> bool:
        """
        Send email response via Gmail API with proper authentication headers.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            thread_id: Gmail thread ID for replies
            in_reply_to: Message-ID of the email being replied to

        Returns:
            True if sent successfully
        """
        if not self.service:
            logger.error("Gmail service not initialized, cannot send email")
            return False

        try:
            logger.info(f"Sending email to {to_email}")

            # Create message with proper headers
            message = MIMEText(body, 'plain', 'utf-8')
            message['To'] = to_email
            message['From'] = f"Custora AI Support <{settings.GMAIL_ADDRESS}>"
            message['Subject'] = subject if not thread_id else f"Re: {subject}"

            # Add authentication and threading headers
            from email.utils import formatdate, make_msgid
            message['Date'] = formatdate(localtime=True)
            message['Message-ID'] = make_msgid(domain=settings.GMAIL_ADDRESS.split('@')[1])

            # Add reply headers for threading (helps with authentication)
            if in_reply_to:
                message['In-Reply-To'] = in_reply_to
                message['References'] = in_reply_to

            # Add standard headers to improve deliverability
            message['X-Mailer'] = 'Custora AI Customer Support System'
            message['X-Priority'] = '3'  # Normal priority
            message['Importance'] = 'Normal'

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            # Send message
            send_body = {'raw': raw_message}
            if thread_id:
                send_body['threadId'] = thread_id

            result = self.service.users().messages().send(
                userId='me',
                body=send_body
            ).execute()

            logger.info(f"Email sent successfully", extra={
                'message_id': result['id'],
                'thread_id': result.get('threadId')
            })

            return True

        except HttpError as e:
            logger.error(f"Gmail API error while sending: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {e}", exc_info=True)
            return False


# Global handler instance
_gmail_handler: Optional[GmailHandler] = None


def get_gmail_handler() -> GmailHandler:
    """
    Get or create global Gmail handler instance.

    Returns:
        GmailHandler instance
    """
    global _gmail_handler

    if _gmail_handler is None:
        _gmail_handler = GmailHandler()

    return _gmail_handler
