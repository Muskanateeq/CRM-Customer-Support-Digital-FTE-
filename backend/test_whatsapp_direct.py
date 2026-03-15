"""
Direct test of WhatsApp webhook processing
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_whatsapp_webhook():
    """Test WhatsApp webhook processing with proper initialization."""

    # Initialize database pool first
    from src.database.client import init_db_pool, close_db_pool
    from src.api.channels import process_whatsapp_message

    print("=" * 70)
    print("WhatsApp Webhook Direct Test")
    print("=" * 70)

    try:
        # Initialize database
        print("\n[1/3] Initializing database pool...")
        await init_db_pool()
        print("[OK] Database pool initialized")

        # Test webhook processing
        print("\n[2/3] Processing WhatsApp message...")
        await process_whatsapp_message(
            from_number='whatsapp:+923152068370',
            to_number='whatsapp:+14155238886',
            body='I need help with my order #12345',
            message_sid='TEST_DIRECT_001',
            media_urls=None
        )
        print("[OK] WhatsApp message processed successfully")

        # Cleanup
        print("\n[3/3] Closing database pool...")
        await close_db_pool()
        print("[OK] Database pool closed")

        print("\n" + "=" * 70)
        print("SUCCESS: WhatsApp webhook test completed!")
        print("=" * 70)

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

        # Cleanup on error
        try:
            await close_db_pool()
        except:
            pass

if __name__ == '__main__':
    asyncio.run(test_whatsapp_webhook())
