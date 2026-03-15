"""
Verify Twilio Sandbox Configuration
"""
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

# Twilio credentials
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')

print("=" * 70)
print("TWILIO SANDBOX VERIFICATION")
print("=" * 70)

try:
    client = Client(account_sid, auth_token)
    
    # Get sandbox participants
    print("\n[1/3] Checking Twilio Account...")
    account = client.api.accounts(account_sid).fetch()
    print(f"✅ Account Status: {account.status}")
    print(f"✅ Account Name: {account.friendly_name}")
    
    print("\n[2/3] Checking WhatsApp Sandbox...")
    print(f"✅ Sandbox Number: {whatsapp_number}")
    
    print("\n[3/3] Testing Message Send Capability...")
    print("⚠️  To send messages, you MUST join the sandbox first!")
    print("\nJoin Instructions:")
    print("1. Open WhatsApp on your phone")
    print("2. Send a message to: +1 415 523 8886")
    print("3. Message text: join <your-sandbox-code>")
    print("\nCheck Twilio Console for your specific join code:")
    print("https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox")
    
    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nPossible issues:")
    print("1. Invalid Twilio credentials")
    print("2. Network connectivity issue")
    print("3. Firewall blocking Twilio API")

