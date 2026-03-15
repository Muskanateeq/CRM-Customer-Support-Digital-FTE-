"""
Kafka Topics Configuration
Defines all Kafka topics used in the system
"""

from typing import Dict, Any


# ============================================
# Topic Names
# ============================================

class KafkaTopics:
    """Kafka topic names."""

    # Message topics
    MESSAGE_RECEIVED = "custora.message.received"
    MESSAGE_SENT = "custora.message.sent"

    # Escalation topics
    ESCALATION_CREATED = "custora.escalation.created"

    # Ticket topics
    TICKET_CREATED = "custora.ticket.created"

    # Agent topics
    AGENT_EXECUTION_COMPLETED = "custora.agent.execution.completed"


# ============================================
# Topic Configuration
# ============================================

TOPIC_CONFIGS: Dict[str, Dict[str, Any]] = {
    KafkaTopics.MESSAGE_RECEIVED: {
        "num_partitions": 3,
        "replication_factor": 1,  # Use 3 in production
        "config": {
            "retention.ms": 604800000,  # 7 days
            "compression.type": "gzip",
        }
    },
    KafkaTopics.MESSAGE_SENT: {
        "num_partitions": 3,
        "replication_factor": 1,
        "config": {
            "retention.ms": 604800000,  # 7 days
            "compression.type": "gzip",
        }
    },
    KafkaTopics.ESCALATION_CREATED: {
        "num_partitions": 1,  # Low volume, single partition
        "replication_factor": 1,
        "config": {
            "retention.ms": 2592000000,  # 30 days
            "compression.type": "gzip",
        }
    },
    KafkaTopics.TICKET_CREATED: {
        "num_partitions": 2,
        "replication_factor": 1,
        "config": {
            "retention.ms": 2592000000,  # 30 days
            "compression.type": "gzip",
        }
    },
    KafkaTopics.AGENT_EXECUTION_COMPLETED: {
        "num_partitions": 3,
        "replication_factor": 1,
        "config": {
            "retention.ms": 604800000,  # 7 days
            "compression.type": "gzip",
        }
    },
}


def get_topic_for_event_type(event_type: str) -> str:
    """
    Get Kafka topic name for event type.

    Args:
        event_type: Event type identifier

    Returns:
        Kafka topic name

    Raises:
        ValueError: If event type not mapped to topic
    """
    event_to_topic = {
        "message.received": KafkaTopics.MESSAGE_RECEIVED,
        "message.sent": KafkaTopics.MESSAGE_SENT,
        "escalation.created": KafkaTopics.ESCALATION_CREATED,
        "ticket.created": KafkaTopics.TICKET_CREATED,
        "agent.execution.completed": KafkaTopics.AGENT_EXECUTION_COMPLETED,
    }

    if event_type not in event_to_topic:
        raise ValueError(f"No topic mapping for event type: {event_type}")

    return event_to_topic[event_type]
