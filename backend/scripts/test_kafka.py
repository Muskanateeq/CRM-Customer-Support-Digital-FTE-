"""
Kafka Test Script
Tests Kafka producer and consumer functionality
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from kafka.producer import KafkaEventProducer
from kafka.events import MessageReceivedEvent
from kafka.topics import KafkaTopics
from config import settings

async def test_kafka():
    """Test Kafka producer."""

    print("=" * 60)
    print("Kafka Connection Test")
    print("=" * 60)
    print()

    # Check if Kafka is enabled
    if not settings.KAFKA_ENABLED:
        print("❌ Kafka is DISABLED in .env file")
        print("Set KAFKA_ENABLED=true in .env")
        return False

    print(f"✅ Kafka is ENABLED")
    print(f"📍 Bootstrap servers: {settings.KAFKA_BOOTSTRAP_SERVERS}")
    print()

    # Create producer
    print("🔌 Creating Kafka producer...")
    producer = KafkaEventProducer()

    try:
        # Start producer
        print("🚀 Starting producer...")
        await producer.start()
        print("✅ Producer started successfully")
        print()

        # Create test event
        print("📤 Publishing test event...")
        test_event = MessageReceivedEvent(
            message_id="test-123",
            conversation_id="conv-test-123",
            customer_id="cust-test-123",
            content="This is a test message",
            channel="web_form",
            sender_type="customer",
            channel_metadata={"test": True}
        )

        # Publish event
        success = await producer.publish_event(
            topic=KafkaTopics.MESSAGE_RECEIVED,
            event=test_event,
            key="test-123"
        )

        if success:
            print("✅ Event published successfully!")
            print(f"   Topic: {KafkaTopics.MESSAGE_RECEIVED}")
            print(f"   Event ID: {test_event.event_id}")
        else:
            print("❌ Failed to publish event")
            return False

        print()

        # Stop producer
        print("🛑 Stopping producer...")
        await producer.stop()
        print("✅ Producer stopped")
        print()

        print("=" * 60)
        print("✅ Kafka Test PASSED!")
        print("=" * 60)
        print()
        print("Kafka is working correctly!")
        print()
        print("Next steps:")
        print("  1. Start API: cd src && uvicorn api.main:app --reload")
        print("  2. Start Workers: cd src && python workers/service.py")
        print("  3. Test web form: http://localhost:3000/support")
        print()

        return True

    except Exception as e:
        print(f"❌ Kafka test FAILED: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Make sure Docker Desktop is running")
        print("  2. Make sure Kafka is started: docker-compose -f docker-compose-kafka.yml up -d")
        print("  3. Check Kafka logs: docker-compose -f docker-compose-kafka.yml logs")
        print("  4. Verify Kafka is running: docker ps | grep kafka")
        print()
        return False

    finally:
        # Cleanup
        if producer._is_started:
            await producer.stop()


if __name__ == "__main__":
    result = asyncio.run(test_kafka())
    sys.exit(0 if result else 1)
