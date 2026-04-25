"""
Notification Service
Sends escalation alerts to admin email
"""

import os
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

from src.utils.logging import get_logger

logger = get_logger(__name__)

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "custora.admin.support@gmail.com")
SUPPORT_EMAIL = os.getenv("GMAIL_ADDRESS", "custora.support@gmail.com")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


async def send_escalation_notification(
    ticket_id: str,
    ticket_number: str,
    customer_name: str,
    customer_email: str,
    customer_phone: Optional[str],
    channel: str,
    priority: str,
    query: str,
    escalation_reason: str
) -> bool:
    """
    Send escalation notification email to admin

    FROM: custora.support@gmail.com
    TO: custora.admin.support@gmail.com
    """
    try:
        # Channel emoji mapping
        channel_icons = {
            "email": "📧",
            "whatsapp": "💬",
            "web_form": "🌐"
        }

        channel_icon = channel_icons.get(channel, "📋")

        # Priority color
        priority_label = priority.upper()
        if priority == "urgent":
            priority_label = "🔴 URGENT"
        elif priority == "high":
            priority_label = "🟠 HIGH"
        elif priority == "medium":
            priority_label = "🟡 MEDIUM"
        else:
            priority_label = "🟢 LOW"

        # Build email
        subject = f"🚨 Escalation Alert: Ticket #{ticket_number}"

        # HTML email body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8f9fa; padding: 20px; border: 1px solid #e9ecef; }}
                .ticket-info {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #2563EB; }}
                .info-row {{ margin: 10px 0; }}
                .label {{ font-weight: bold; color: #666; }}
                .value {{ color: #333; }}
                .query-box {{ background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #ffc107; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #2563EB; color: white; text-decoration: none; border-radius: 6px; margin: 15px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0;">🚨 Escalation Alert</h2>
                    <p style="margin: 5px 0 0 0;">A customer query requires human attention</p>
                </div>

                <div class="content">
                    <div class="ticket-info">
                        <h3 style="margin-top: 0;">Ticket Information</h3>

                        <div class="info-row">
                            <span class="label">Ticket ID:</span>
                            <span class="value">#{ticket_number}</span>
                        </div>

                        <div class="info-row">
                            <span class="label">Customer:</span>
                            <span class="value">{customer_name}</span>
                        </div>

                        <div class="info-row">
                            <span class="label">Email:</span>
                            <span class="value">{customer_email}</span>
                        </div>

                        {f'<div class="info-row"><span class="label">Phone:</span><span class="value">{customer_phone}</span></div>' if customer_phone else ''}

                        <div class="info-row">
                            <span class="label">Channel:</span>
                            <span class="value">{channel_icon} {channel.replace('_', ' ').title()}</span>
                        </div>

                        <div class="info-row">
                            <span class="label">Priority:</span>
                            <span class="value">{priority_label}</span>
                        </div>

                        <div class="info-row">
                            <span class="label">Escalation Reason:</span>
                            <span class="value">{escalation_reason}</span>
                        </div>
                    </div>

                    <div class="query-box">
                        <h4 style="margin-top: 0;">Customer Query:</h4>
                        <p style="margin: 0; white-space: pre-wrap;">{query}</p>
                    </div>

                    <div style="text-align: center;">
                        <a href="{FRONTEND_URL}/admin/tickets/{ticket_id}" class="button">
                            View Ticket in Admin Portal →
                        </a>
                    </div>

                    <div class="footer">
                        <p>This is an automated notification from Custora Support System</p>
                        <p>Please respond to this ticket through the admin portal</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        # Plain text version
        text_body = f"""
ESCALATION ALERT - Ticket #{ticket_number}

A customer query requires human attention.

TICKET INFORMATION:
-------------------
Ticket ID: #{ticket_number}
Customer: {customer_name}
Email: {customer_email}
{f'Phone: {customer_phone}' if customer_phone else ''}
Channel: {channel_icon} {channel.replace('_', ' ').title()}
Priority: {priority_label}
Escalation Reason: {escalation_reason}

CUSTOMER QUERY:
---------------
{query}

VIEW IN ADMIN PORTAL:
{FRONTEND_URL}/admin/tickets/{ticket_id}

---
This is an automated notification from Custora Support System.
Please respond to this ticket through the admin portal.
        """

        # Send email using Gmail API
        from src.channels.helpers import send_email

        success = await send_email(
            to_email=ADMIN_EMAIL,
            subject=subject,
            body_text=text_body,
            body_html=html_body,
            from_email=SUPPORT_EMAIL
        )

        if success:
            logger.info(f"Escalation notification sent to {ADMIN_EMAIL} for ticket {ticket_number}")
        else:
            logger.error(f"Failed to send escalation notification for ticket {ticket_number}")

        return success

    except Exception as e:
        logger.error(f"Error sending escalation notification: {e}", exc_info=True)
        return False
