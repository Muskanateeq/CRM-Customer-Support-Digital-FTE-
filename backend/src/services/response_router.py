"""
Response Router Service
Routes admin responses to correct channel (Email, WhatsApp, Web Form)
"""

import os
from typing import Optional

from src.utils.logging import get_logger

logger = get_logger(__name__)

SUPPORT_EMAIL = os.getenv("GMAIL_ADDRESS", "custora.support@gmail.com")


async def route_admin_response(
    ticket_id: str,
    customer_email: Optional[str],
    customer_phone: Optional[str],
    customer_name: str,
    channel: str,
    response_content: str
) -> bool:
    """
    Route admin response to correct channel

    Args:
        ticket_id: Ticket ID
        customer_email: Customer email address
        customer_phone: Customer phone number
        customer_name: Customer name
        channel: Original channel (email, whatsapp, web_form)
        response_content: Admin's response message

    Returns:
        True if sent successfully, False otherwise
    """
    try:
        logger.info(f"Routing admin response for ticket {ticket_id} via {channel}")

        if channel == "email":
            return await send_email_response(
                customer_email=customer_email,
                customer_name=customer_name,
                ticket_id=ticket_id,
                response_content=response_content
            )

        elif channel == "whatsapp":
            return await send_whatsapp_response(
                customer_phone=customer_phone,
                customer_name=customer_name,
                ticket_id=ticket_id,
                response_content=response_content
            )

        elif channel == "web_form":
            return await send_webform_response(
                customer_email=customer_email,
                customer_name=customer_name,
                ticket_id=ticket_id,
                response_content=response_content
            )

        else:
            logger.error(f"Unknown channel: {channel}")
            return False

    except Exception as e:
        logger.error(f"Error routing response: {e}", exc_info=True)
        return False


async def send_email_response(
    customer_email: str,
    customer_name: str,
    ticket_id: str,
    response_content: str
) -> bool:
    """
    Send response via email

    FROM: custora.support@gmail.com
    TO: customer email
    """
    try:
        from src.channels.helpers import send_email

        # Generate ticket number for display
        ticket_number = f"TKT-{ticket_id.replace('-', '').upper()[:8]}"

        subject = f"Re: Your Support Request #{ticket_number}"

        # HTML email body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8f9fa; padding: 20px; border: 1px solid #e9ecef; }}
                .response-box {{ background: white; padding: 20px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #2563EB; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e9ecef; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0;">Custora Support</h2>
                    <p style="margin: 5px 0 0 0;">Response to Your Support Request</p>
                </div>

                <div class="content">
                    <p>Hi {customer_name},</p>

                    <p>Thank you for contacting Custora Support. Here's our response to your inquiry:</p>

                    <div class="response-box">
                        <p style="margin: 0; white-space: pre-wrap;">{response_content}</p>
                    </div>

                    <p>If you have any additional questions, please feel free to reply to this email.</p>

                    <p>Best regards,<br>
                    Custora Support Team</p>

                    <div class="footer">
                        <p>Ticket Reference: #{ticket_number}</p>
                        <p>This email was sent from custora.support@gmail.com</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        # Plain text version
        text_body = f"""
Hi {customer_name},

Thank you for contacting Custora Support. Here's our response to your inquiry:

{response_content}

If you have any additional questions, please feel free to reply to this email.

Best regards,
Custora Support Team

---
Ticket Reference: #{ticket_number}
        """

        success = await send_email(
            to_email=customer_email,
            subject=subject,
            body_text=text_body,
            body_html=html_body,
            from_email=SUPPORT_EMAIL
        )

        if success:
            logger.info(f"Email response sent to {customer_email} for ticket {ticket_id}")
        else:
            logger.error(f"Failed to send email response to {customer_email}")

        return success

    except Exception as e:
        logger.error(f"Error sending email response: {e}", exc_info=True)
        return False


async def send_whatsapp_response(
    customer_phone: str,
    customer_name: str,
    ticket_id: str,
    response_content: str
) -> bool:
    """
    Send response via WhatsApp

    FROM: Twilio WhatsApp number
    TO: Customer phone
    """
    try:
        from src.channels.helpers import send_whatsapp_message

        # Generate ticket number
        ticket_number = f"TKT-{ticket_id.replace('-', '').upper()[:8]}"

        # Format WhatsApp message
        message = f"""*Custora Support Response*

Hi {customer_name},

{response_content}

If you have more questions, just reply to this message.

_Ticket: #{ticket_number}_"""

        success = await send_whatsapp_message(
            to_phone=customer_phone,
            message=message
        )

        if success:
            logger.info(f"WhatsApp response sent to {customer_phone} for ticket {ticket_id}")
        else:
            logger.error(f"Failed to send WhatsApp response to {customer_phone}")

        return success

    except Exception as e:
        logger.error(f"Error sending WhatsApp response: {e}", exc_info=True)
        return False


async def send_webform_response(
    customer_email: str,
    customer_name: str,
    ticket_id: str,
    response_content: str
) -> bool:
    """
    Send response for web form tickets

    Response is stored in database and customer can view in ticket portal
    Optionally send email notification
    """
    try:
        # Response is already stored in ticket_responses table by the API
        # Customer can view it in /tickets page

        # Optionally send email notification
        from src.channels.email_handler import send_email

        ticket_number = f"TKT-{ticket_id.replace('-', '').upper()[:8]}"

        subject = f"Response to Your Support Request #{ticket_number}"

        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8f9fa; padding: 20px; border: 1px solid #e9ecef; }}
                .response-box {{ background: white; padding: 20px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #2563EB; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #2563EB; color: white; text-decoration: none; border-radius: 6px; margin: 15px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e9ecef; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0;">Custora Support</h2>
                    <p style="margin: 5px 0 0 0;">We've Responded to Your Ticket</p>
                </div>

                <div class="content">
                    <p>Hi {customer_name},</p>

                    <p>Our support team has responded to your ticket #{ticket_number}.</p>

                    <div class="response-box">
                        <p style="margin: 0; white-space: pre-wrap;">{response_content}</p>
                    </div>

                    <div style="text-align: center;">
                        <a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/tickets/{ticket_id}" class="button">
                            View Full Ticket →
                        </a>
                    </div>

                    <p>You can also view your ticket history and continue the conversation in our support portal.</p>

                    <p>Best regards,<br>
                    Custora Support Team</p>

                    <div class="footer">
                        <p>Ticket Reference: #{ticket_number}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
Hi {customer_name},

Our support team has responded to your ticket #{ticket_number}.

{response_content}

View your full ticket at: {os.getenv('FRONTEND_URL', 'http://localhost:3000')}/tickets/{ticket_id}

Best regards,
Custora Support Team

---
Ticket Reference: #{ticket_number}
        """

        success = await send_email(
            to_email=customer_email,
            subject=subject,
            body_text=text_body,
            body_html=html_body,
            from_email=SUPPORT_EMAIL
        )

        if success:
            logger.info(f"Web form response notification sent to {customer_email} for ticket {ticket_id}")

        # Return True even if email fails, since response is in database
        return True

    except Exception as e:
        logger.error(f"Error sending web form response: {e}", exc_info=True)
        # Still return True since response is stored in database
        return True
