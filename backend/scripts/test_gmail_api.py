"""
Test Gmail API - Direct Test Script
Tests if Gmail API can read emails
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import asyncio
from src.channels.email_handler import get_gmail_handler
from src.config import settings


async def test_gmail_api():
    """Test Gmail API directly."""
    print("=" * 70)
    print("Gmail API Test Script")
    print("=" * 70)
    print(f"Gmail Address: {settings.GMAIL_ADDRESS}")
    print(f"Gmail Enabled: {settings.GMAIL_ENABLED}")
    print("=" * 70)
    print()

    # Get handler
    handler = get_gmail_handler()

    if not handler.service:
        print("❌ Gmail service not initialized!")
        print("Check:")
        print("  1. GMAIL_ENABLED=true in .env")
        print("  2. GMAIL_TOKEN_JSON is set in .env")
        print("  3. Token is valid (not expired)")
        return

    print("✅ Gmail service initialized")
    print()

    # Test 1: List ALL emails (not just unread)
    print("Test 1: Listing ALL emails in inbox...")
    print("-" * 70)

    try:
        results = handler.service.users().messages().list(
            userId='me',
            maxResults=10
        ).execute()

        messages = results.get('messages', [])
        print(f"Total emails in inbox: {len(messages)}")

        if messages:
            print("\nRecent emails:")
            for i, msg in enumerate(messages[:5], 1):
                # Get message details
                message = handler.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()

                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')

                labels = message.get('labelIds', [])
                is_unread = 'UNREAD' in labels

                print(f"\n{i}. {subject}")
                print(f"   From: {from_email}")
                print(f"   Date: {date}")
                print(f"   Unread: {'Yes ✓' if is_unread else 'No'}")
                print(f"   Labels: {', '.join(labels)}")
        else:
            print("No emails found in inbox!")

    except Exception as e:
        print(f"❌ Error listing emails: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 70)

    # Test 2: List UNREAD emails
    print("\nTest 2: Listing UNREAD emails...")
    print("-" * 70)

    try:
        query = f"to:{settings.GMAIL_ADDRESS} is:unread"
        print(f"Query: {query}")
        print()

        results = handler.service.users().messages().list(
            userId='me',
            q=query,
            maxResults=10
        ).execute()

        messages = results.get('messages', [])
        print(f"Unread emails found: {len(messages)}")

        if messages:
            print("\nUnread emails:")
            for i, msg in enumerate(messages, 1):
                # Get message details
                message = handler.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()

                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')

                print(f"\n{i}. {subject}")
                print(f"   From: {from_email}")
                print(f"   Message ID: {msg['id']}")
        else:
            print("No unread emails found!")
            print("\nPossible reasons:")
            print("  1. All emails are already marked as read")
            print("  2. Emails are in Spam/Promotions (not in Primary inbox)")
            print("  3. No emails sent to this address yet")

    except Exception as e:
        print(f"❌ Error querying unread emails: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 70)

    # Test 3: Poll using handler method
    print("\nTest 3: Using poll_new_emails() method...")
    print("-" * 70)

    try:
        emails = await handler.poll_new_emails()
        print(f"Emails returned by poll_new_emails(): {len(emails)}")

        if emails:
            print("\nEmails found:")
            for i, email in enumerate(emails, 1):
                print(f"\n{i}. {email['subject']}")
                print(f"   From: {email['from']}")
                print(f"   Body preview: {email['body'][:100]}...")
        else:
            print("No emails returned by poll_new_emails()")

    except Exception as e:
        print(f"❌ Error in poll_new_emails(): {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 70)
    print("Test complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_gmail_api())
