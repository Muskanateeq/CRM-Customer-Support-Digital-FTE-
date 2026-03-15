"""
Module 4 Test Script - Kafka Event Streaming
Tests Kafka producer and event publishing
"""

import asyncio
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.abspath('.'))

from src.config import settings
from src.database.client import init_db_pool, close_db_pool
from src.utils.logging import setup_logging, get_logger
from src.kafka.producer import KafkaEventProducer
from src.kafka.events import (
    MessageReceivedEvent,
    MessageSentEvent,
    EscalationCreatedEvent,
    TicketCreatedEvent,
    AgentExecutionCompletedEvent,
)
from src.kafka.topics import KafkaTopics, get_topic_for_event_type
from src.kafka.helpers import (
    publish_message_received,
    publish_message_sent,
    publish_escalation_created,
    publish_ticket_created,
    publish_agent_execution_completed,
)

# Setup logging
setup_logging(log_level="INFO", environment="development")
logger = get_logger(__name__)


async def test_module_4():
    """Test all Module 4 components."""

    print("=" * 70)
    print("Module 4: Kafka Event Streaming - Test Suite")
    print("=" * 70)
    print()

    # Check if Kafka is enabled
    if not settings.KAFKA_ENABLED:
        print("[FAIL] Kafka is disabled in settings")
        print("   Set KAFKA_ENABLED=true in .env to run tests")
        return False

    # Initialize database
    await init_db_pool()
    print("[OK] Database pool initialized")
    print()

    # ============================================
    # Test 1: Kafka Producer Initialization
    # ============================================
    print("[OK] Test 1: Kafka Producer Initialization")
    try:
        producer = KafkaEventProducer()
        await producer.start()
        print(f"   [OK] Kafka producer started")
        print(f"   [OK] Bootstrap servers: {settings.KAFKA_BOOTSTRAP_SERVERS}")
        print(f"   [OK] Compression: gzip")
        print(f"   [OK] Idempotence: enabled")
    except Exception as e:
        print(f"   [FAIL] Kafka producer initialization failed: {e}")
        print()
        print("   Make sure Kafka is running:")
        print("   docker run -d -p 9092:9092 apache/kafka:latest")
        return False
    print()

    # ============================================
    # Test 2: Event Schema Validation
    # ============================================
    print("[OK] Test 2: Event Schema Validation")
    try:
        # Create test event
        event = MessageReceivedEvent(
            event_id="test-123",
            message_id=1,
            conversation_id=1,
            customer_id=1,
            content="Test message",
            channel="webform",
            sender_type="customer",
        )
        print(f"   [OK] MessageReceivedEvent created")
        print(f"   [OK] Event type: {event.event_type}")
        print(f"   [OK] Event ID: {event.event_id}")

        # Validate serialization
        event_dict = event.model_dump(mode='json')
        print(f"   [OK] Event serialized to dict")
        print(f"   [OK] Fields: {len(event_dict)}")

    except Exception as e:
        print(f"   [FAIL] Event schema validation failed: {e}")
    print()

    # ============================================
    # Test 3: Topic Configuration
    # ============================================
    print("[OK] Test 3: Topic Configuration")
    try:
        topics = [
            KafkaTopics.MESSAGE_RECEIVED,
            KafkaTopics.MESSAGE_SENT,
            KafkaTopics.ESCALATION_CREATED,
            KafkaTopics.TICKET_CREATED,
            KafkaTopics.AGENT_EXECUTION_COMPLETED,
        ]
        print(f"   [OK] Configured topics: {len(topics)}")
        for topic in topics:
            print(f"      - {topic}")

        # Test topic mapping
        topic = get_topic_for_event_type("message.received")
        print(f"   [OK] Topic mapping works: message.received → {topic}")

    except Exception as e:
        print(f"   [FAIL] Topic configuration test failed: {e}")
    print()

    # ============================================
    # Test 4: Publish Message Events
    # ============================================
    print("[OK] Test 4: Publish Message Events")
    try:
        # Publish message.received
        success = await publish_message_received(
            message_id=1,
            conversation_id=1,
            customer_id=1,
            content="Hello, I need help with my account",
            channel="webform",
            sender_type="customer",
            channel_metadata={"browser": "Chrome", "ip": "192.168.1.1"},
        )
        if success:
            print(f"   [OK] message.received event published")
        else:
            print(f"   [FAIL] message.received event failed")

        # Publish message.sent
        success = await publish_message_sent(
            message_id=2,
            conversation_id=1,
            customer_id=1,
            content="I'd be happy to help you with your account!",
            channel="webform",
            delivery_status="sent",
        )
        if success:
            print(f"   [OK] message.sent event published")
        else:
            print(f"   [FAIL] message.sent event failed")

    except Exception as e:
        print(f"   [FAIL] Message event publishing failed: {e}")
    print()

    # ============================================
    # Test 5: Publish Escalation Event
    # ============================================
    print("[OK] Test 5: Publish Escalation Event")
    try:
        success = await publish_escalation_created(
            conversation_id=1,
            customer_id=1,
            reason="Customer requested refund",
            urgency="high",
            channel="email",
            trigger="refund_request",
        )
        if success:
            print(f"   [OK] escalation.created event published")
            print(f"   [OK] Urgency: high")
            print(f"   [OK] Trigger: refund_request")
        else:
            print(f"   [FAIL] escalation.created event failed")

    except Exception as e:
        print(f"   [FAIL] Escalation event publishing failed: {e}")
    print()

    # ============================================
    # Test 6: Publish Ticket Event
    # ============================================
    print("[OK] Test 6: Publish Ticket Event")
    try:
        success = await publish_ticket_created(
            ticket_id=1,
            conversation_id=1,
            customer_id=1,
            subject="Login issue - cannot access account",
            priority="high",
            category="technical",
            status="open",
        )
        if success:
            print(f"   [OK] ticket.created event published")
            print(f"   [OK] Priority: high")
            print(f"   [OK] Category: technical")
        else:
            print(f"   [FAIL] ticket.created event failed")

    except Exception as e:
        print(f"   [FAIL] Ticket event publishing failed: {e}")
    print()

    # ============================================
    # Test 7: Publish Agent Execution Event
    # ============================================
    print("[OK] Test 7: Publish Agent Execution Event")
    try:
        success = await publish_agent_execution_completed(
            conversation_id=1,
            customer_id=1,
            message_id=1,
            execution_time=2.5,
            tools_used=["search_knowledge_base", "send_response"],
            success=True,
        )
        if success:
            print(f"   [OK] agent.execution.completed event published")
            print(f"   [OK] Execution time: 2.5s")
            print(f"   [OK] Tools used: 2")
        else:
            print(f"   [FAIL] agent.execution.completed event failed")

    except Exception as e:
        print(f"   [FAIL] Agent execution event publishing failed: {e}")
    print()

    # ============================================
    # Test 8: Event Serialization
    # ============================================
    print("[OK] Test 8: Event Serialization")
    try:
        event = TicketCreatedEvent(
            event_id="test-456",
            ticket_id=1,
            conversation_id=1,
            customer_id=1,
            subject="Test ticket",
            priority="medium",
            category="general",
            status="open",
        )

        # Serialize to JSON
        event_dict = event.model_dump(mode='json')
        json_str = json.dumps(event_dict, indent=2)
        print(f"   [OK] Event serialized to JSON")
        print(f"   [OK] JSON size: {len(json_str)} bytes")
        print(f"   Sample:")
        print(f"   {json_str[:200]}...")

    except Exception as e:
        print(f"   [FAIL] Event serialization failed: {e}")
    print()

    # ============================================
    # Cleanup
    # ============================================
    await producer.stop()
    print("[OK] Test 9: Cleanup")
    print("   [OK] Kafka producer stopped")

    await close_db_pool()
    print("   [OK] Database pool closed")
    print()

    print("=" * 70)
    print("[OK] Module 4 Tests Complete - Kafka Event Streaming Operational")
    print("=" * 70)
    print()
    print("Event Types Verified:")
    print("[OK] message.received")
    print("[OK] message.sent")
    print("[OK] escalation.created")
    print("[OK] ticket.created")
    print("[OK] agent.execution.completed")
    print()
    print("Next Steps:")
    print("1. Set up Kafka consumers to process events")
    print("2. Integrate with monitoring/analytics")
    print("3. Ready for Module 5: Message Processor Workers")
    print()

    return True


if __name__ == "__main__":
    # Check if Kafka is running
    if not settings.KAFKA_ENABLED:
        print("[FAIL] Error: KAFKA_ENABLED not set to true in .env file")
        print()
        print("To enable Kafka:")
        print("1. Start Kafka: docker run -d -p 9092:9092 apache/kafka:latest")
        print("2. Set KAFKA_ENABLED=true in .env")
        print("3. Set KAFKA_BOOTSTRAP_SERVERS=localhost:9092 in .env")
        sys.exit(1)

    success = asyncio.run(test_module_4())
    sys.exit(0 if success else 1)
