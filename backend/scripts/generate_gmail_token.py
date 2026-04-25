"""
Gmail OAuth Token Generator for Custora AI
Generates fresh OAuth tokens and updates .env file automatically
"""

import json
import re
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def generate_token():
    """Generate fresh Gmail OAuth token from .env credentials."""

    print("=" * 70)
    print("Gmail OAuth Token Generator - Custora AI")
    print("=" * 70)
    print()

    # Load credentials from .env
    env_path = Path(__file__).parent.parent / '.env'

    if not env_path.exists():
        print("[ERROR] .env file not found at:", env_path)
        return

    print("[1/4] Reading .env file...")
    with open(env_path, 'r', encoding='utf-8') as f:
        env_content = f.read()

    # Extract GMAIL_CREDENTIALS_JSON
    creds_match = re.search(r'GMAIL_CREDENTIALS_JSON=(.+)', env_content)

    if not creds_match:
        print("[ERROR] GMAIL_CREDENTIALS_JSON not found in .env")
        print("Please add your Gmail OAuth credentials to .env file")
        return

    creds_json_str = creds_match.group(1)

    try:
        credentials_info = json.loads(creds_json_str)
        print("[OK] Loaded OAuth credentials from .env")
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in GMAIL_CREDENTIALS_JSON: {e}")
        return

    print()
    print("[2/4] Starting OAuth flow...")
    print()
    print("IMPORTANT:")
    print("  - A browser window will open")
    print("  - Sign in to: mahu.in.456@gmail.com")
    print("  - Click 'Allow' to grant Gmail access")
    print("  - If you see 'This app isn't verified', click 'Advanced' → 'Go to app (unsafe)'")
    print()
    input("Press Enter to open browser...")
    print()

    try:
        flow = InstalledAppFlow.from_client_config(
            credentials_info,
            SCOPES
        )

        # Run local server to receive OAuth callback
        print("Opening browser for authentication...")
        creds = flow.run_local_server(port=0)

        print()
        print("[3/4] OAuth authentication successful!")
        print()

        # Convert credentials to dict
        token_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes,
            'universe_domain': getattr(creds, 'universe_domain', 'googleapis.com'),
            'account': '',
            'expiry': creds.expiry.isoformat() if creds.expiry else None
        }

        # Format as JSON string for .env
        token_json_str = json.dumps(token_data)

        print("[4/4] Updating .env file...")
        print()

        # Replace GMAIL_TOKEN_JSON in .env
        new_env_content = re.sub(
            r'GMAIL_TOKEN_JSON=.+',
            f'GMAIL_TOKEN_JSON={token_json_str}',
            env_content
        )

        # Write updated .env
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(new_env_content)

        print("=" * 70)
        print("SUCCESS! Gmail OAuth token generated and saved to .env")
        print("=" * 70)
        print()
        print("Token Details:")
        print(f"  - Expires: {token_data['expiry']}")
        print(f"  - Scopes: {', '.join(token_data['scopes'])}")
        print()
        print("Next Steps:")
        print("  1. Restart your backend server (Ctrl+C and restart)")
        print("  2. Run the email polling script: start_email_polling.bat")
        print("  3. Send a test email to: custora.support@gmail.com")
        print()
        print("=" * 70)

    except Exception as e:
        print()
        print(f"[ERROR] OAuth flow failed: {e}")
        print()
        print("Common Issues:")
        print("  - OAuth consent screen not configured in Google Cloud Console")
        print("  - Redirect URI not set to http://localhost")
        print("  - Gmail API not enabled in Google Cloud Console")
        print("  - Credentials are invalid or expired")
        print()
        print("Solution:")
        print("  1. Go to: https://console.cloud.google.com")
        print("  2. Enable Gmail API")
        print("  3. Configure OAuth consent screen")
        print("  4. Add http://localhost to authorized redirect URIs")
        print()


if __name__ == '__main__':
    generate_token()
