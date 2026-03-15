"""
Email Polling Script for Custora AI
Polls Gmail API every 30 seconds for new customer emails
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import requests
import time
from datetime import datetime


def poll_emails():
    """Poll the email endpoint."""
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Polling for new emails...")

        response = requests.post(
            "http://localhost:8001/api/v1/channels/email/poll",
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            emails_found = data.get('emails_found', 0)

            if emails_found > 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Found {emails_found} new email(s) - Processing...")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ No new emails")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Error: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Cannot connect to backend (is it running?)")
    except requests.exceptions.Timeout:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Request timeout")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Error: {e}")


def main():
    """Main polling loop."""
    print("=" * 60)
    print("Custora AI - Email Polling Service")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend URL: http://localhost:8001")
    print(f"Poll interval: 30 seconds")
    print("=" * 60)
    print("\nPress Ctrl+C to stop\n")

    try:
        while True:
            poll_emails()
            time.sleep(30)  # Poll every 30 seconds

    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("Email polling service stopped")
        print("=" * 60)


if __name__ == "__main__":
    main()
