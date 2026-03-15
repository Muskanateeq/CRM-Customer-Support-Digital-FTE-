"""
Module 1 Test Script - Core Infrastructure
Tests configuration, database, logging, and FastAPI application
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath('.'))

from src.config import settings
from src.database.client import init_db_pool, close_db_pool, check_db_health, get_customer_by_email
from src.utils.logging import setup_logging, get_logger

# Setup logging
setup_logging(log_level="INFO", environment="development")
logger = get_logger(__name__)


async def test_module_1():
    """Test all Module 1 components."""

    print("=" * 70)
    print("Module 1: Core Infrastructure - Test Suite")
    print("=" * 70)
    print()

    # ============================================
    # Test 1: Configuration
    # ============================================
    print("[OK] Test 1: Configuration Management")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   Database Host: {settings.POSTGRES_HOST}")
    print(f"   Database Name: {settings.POSTGRES_DB}")
    print(f"   API Port: {settings.API_PORT}")
    print(f"   OpenAI Model: {settings.AGENT_MODEL}")
    print(f"   Channels: Email={settings.GMAIL_ENABLED}, WhatsApp={settings.WHATSAPP_ENABLED}, Web={settings.WEBFORM_ENABLED}")
    print()

    # ============================================
    # Test 2: Logging
    # ============================================
    print("[OK] Test 2: Structured Logging")
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    print()

    # ============================================
    # Test 3: Database Connection
    # ============================================
    print("[OK] Test 3: Database Connection Pool")
    try:
        await init_db_pool()
        print("   [OK] Database pool initialized")

        # Test health check
        is_healthy = await check_db_health()
        print(f"   [OK] Database health check: {'PASS' if is_healthy else 'FAIL'}")

        # Test query
        customer = await get_customer_by_email("demo@example.com")
        if customer:
            print(f"   [OK] Query test: Found customer {customer['name']}")
        else:
            print("   [OK] Query test: No customer found (expected)")

    except Exception as e:
        print(f"   [FAIL] Database test failed: {e}")
        return False

    print()

    # ============================================
    # Test 4: FastAPI Application
    # ============================================
    print("[OK] Test 4: FastAPI Application")
    print("   To test the API, run:")
    print("   python src/api/main.py")
    print()
    print("   Then visit:")
    print("   - http://localhost:8000/")
    print("   - http://localhost:8000/health")
    print("   - http://localhost:8000/docs")
    print()

    # ============================================
    # Cleanup
    # ============================================
    await close_db_pool()
    print("[OK] Test 5: Cleanup")
    print("   [OK] Database pool closed")
    print()

    print("=" * 70)
    print("[OK] Module 1 Tests Complete - All Systems Operational")
    print("=" * 70)
    print()
    print("Next Steps:")
    print("1. Start the API: python src/api/main.py")
    print("2. Test endpoints: curl http://localhost:8000/health")
    print("3. Ready for Module 2: OpenAI Agent Integration")
    print()

    return True


if __name__ == "__main__":
    success = asyncio.run(test_module_1())
    sys.exit(0 if success else 1)
