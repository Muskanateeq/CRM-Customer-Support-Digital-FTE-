"""
Email Polling Script for Custora AI
Polls Gmail API every 30 seconds for new customer emails
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import requests
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(backend_path / ".env")

EMAIL_POLL_SECRET = os.getenv("EMAIL_POLL_SECRET")


def get_backend_url() -> str:
    """Return the configured API URL or this service's local Render URL."""
    configured_url = os.getenv("BACKEND_URL")
    if configured_url:
        return configured_url.rstrip("/")

    # Render injects PORT for web services. The local development default is
    # the same port used by the backend's uvicorn configuration.
    port = os.getenv("PORT", "8000")
    return f"http://127.0.0.1:{port}"


def poll_emails():
    """Poll the email endpoint."""
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Polling for new emails...")

        response = requests.post(
            f"{get_backend_url()}/api/v1/channels/email/poll",
            headers={"X-Email-Poll-Secret": EMAIL_POLL_SECRET or ""},
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
    if not EMAIL_POLL_SECRET:
        raise RuntimeError("EMAIL_POLL_SECRET is required")

    print("=" * 60)
    print("Custora AI - Email Polling Service")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend URL: {get_backend_url()}")
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
