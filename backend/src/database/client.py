"""
Custora Customer Success FTE - Database Client
Async PostgreSQL connection pool and query utilities
"""

import asyncpg
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import logging
import ssl

from src.config import settings

logger = logging.getLogger(__name__)

# Global connection pool
_pool: Optional[asyncpg.Pool] = None


async def init_db_pool() -> asyncpg.Pool:
    """
    Initialize database connection pool with retry logic for Neon serverless wake-up.

    Neon databases auto-suspend after inactivity. First connection attempt may fail
    while database is waking up. This function retries up to 3 times with delays.

    Returns:
        asyncpg.Pool: Database connection pool
    """
    global _pool

    if _pool is not None:
        logger.warning("Database pool already initialized")
        return _pool

    max_retries = 3
    retry_delay = 10  # seconds

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Initializing database connection pool (attempt {attempt}/{max_retries})...")
            logger.info(f"Host: {settings.POSTGRES_HOST}")
            logger.info(f"Database: {settings.POSTGRES_DB}")
            logger.info(f"Pool size: {settings.DB_POOL_MIN_SIZE}-{settings.DB_POOL_MAX_SIZE}")

            if attempt > 1:
                logger.info(f"Database may be waking up from sleep mode. Waiting {retry_delay}s before retry...")
                import asyncio
                await asyncio.sleep(retry_delay)

            # Create SSL context for Neon (skip certificate verification in development)
            # This matches the frontend behavior: ssl: { rejectUnauthorized: false }
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            async def init_connection(conn):
                """Initialize and validate each connection."""
                # Set statement timeout to prevent long-running queries
                await conn.execute("SET statement_timeout = '60s'")

            _pool = await asyncpg.create_pool(
                dsn=settings.DATABASE_URL,
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
                timeout=120,  # 2 minutes for initial connection (Neon wake-up time)
                command_timeout=60,
                max_inactive_connection_lifetime=240,  # Close idle connections after 4 minutes (before Neon's 5min timeout)
                max_cached_statement_lifetime=0,  # Disable statement caching to avoid stale prepared statements
                ssl=ssl_context,  # Use custom SSL context
                server_settings={
                    'application_name': 'custora_fte'
                },
                # Connection health check on acquire
                init=init_connection,
            )

            # Test connection
            async with _pool.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
                logger.info(f"[OK] Database connected: {version[:50]}...")

            logger.info("[OK] Database pool initialized successfully")
            return _pool

        except Exception as e:
            logger.error(f"[FAIL] Connection attempt {attempt}/{max_retries} failed: {e}")

            if attempt == max_retries:
                logger.error("All connection attempts failed. Database may be unavailable.")
                raise

            # Continue to next retry
            continue

    # Should never reach here, but just in case
    raise RuntimeError("Failed to initialize database pool after all retries")


async def close_db_pool():
    """Close database connection pool."""
    global _pool

    if _pool is None:
        return

    try:
        logger.info("Closing database connection pool...")
        await _pool.close()
        _pool = None
        logger.info("[OK] Database pool closed")
    except Exception as e:
        logger.error(f"Error closing database pool: {e}")


def get_db_pool() -> asyncpg.Pool:
    """
    Get database connection pool.

    Returns:
        asyncpg.Pool: Database connection pool

    Raises:
        RuntimeError: If pool is not initialized
    """
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db_pool() first.")
    return _pool


@asynccontextmanager
async def get_db_connection():
    """
    Context manager for database connections.

    Usage:
        async with get_db_connection() as conn:
            result = await conn.fetch("SELECT * FROM customers")
    """
    pool = get_db_pool()
    async with pool.acquire() as connection:
        yield connection


# ============================================
# Customer Queries
# ============================================

async def get_customer_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get customer by email."""
    async with get_db_connection() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM customers WHERE email = $1",
            email
        )
        return dict(row) if row else None


async def get_customer_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    """Get customer by phone."""
    async with get_db_connection() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM customers WHERE phone = $1",
            phone
        )
        return dict(row) if row else None


async def create_customer(email: Optional[str], phone: Optional[str], name: Optional[str]) -> str:
    """
    Create new customer.

    Returns:
        str: Customer UUID
    """
    async with get_db_connection() as conn:
        customer_id = await conn.fetchval(
            """
            INSERT INTO customers (email, phone, name)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            email, phone, name
        )
        return str(customer_id)


async def find_customer_by_identifier(identifier_type: str, identifier_value: str) -> Optional[str]:
    """
    Find customer by identifier (email, phone, whatsapp).

    Returns:
        Optional[str]: Customer UUID if found
    """
    async with get_db_connection() as conn:
        customer_id = await conn.fetchval(
            """
            SELECT customer_id FROM customer_identifiers
            WHERE identifier_type = $1 AND identifier_value = $2
            """,
            identifier_type, identifier_value
        )
        return str(customer_id) if customer_id else None


async def get_or_create_customer_identifier(
    customer_id: str,
    identifier_type: str,
    identifier_value: str
) -> str:
    """
    Get or create customer identifier mapping.

    Args:
        customer_id: Customer UUID
        identifier_type: Type of identifier (email, phone, whatsapp)
        identifier_value: Identifier value

    Returns:
        str: Customer identifier UUID
    """
    async with get_db_connection() as conn:
        # Try to get existing identifier
        identifier_id = await conn.fetchval(
            """
            SELECT id FROM customer_identifiers
            WHERE customer_id = $1 AND identifier_type = $2 AND identifier_value = $3
            """,
            customer_id, identifier_type, identifier_value
        )

        if identifier_id:
            return str(identifier_id)

        # Create new identifier
        identifier_id = await conn.fetchval(
            """
            INSERT INTO customer_identifiers (customer_id, identifier_type, identifier_value)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            customer_id, identifier_type, identifier_value
        )
        return str(identifier_id)


# ============================================
# Conversation Queries
# ============================================

async def create_conversation(customer_id: str, channel: str) -> str:
    """
    Create new conversation.

    Returns:
        str: Conversation UUID
    """
    async with get_db_connection() as conn:
        conversation_id = await conn.fetchval(
            """
            INSERT INTO conversations (customer_id, initial_channel, status)
            VALUES ($1, $2, 'active')
            RETURNING id
            """,
            customer_id, channel
        )
        return str(conversation_id)


async def get_active_conversation(customer_id: str) -> Optional[Dict[str, Any]]:
    """Get active conversation for customer (within last 24 hours)."""
    async with get_db_connection() as conn:
        row = await conn.fetchrow(
            """
            SELECT * FROM conversations
            WHERE customer_id = $1
              AND status = 'active'
              AND started_at > NOW() - INTERVAL '24 hours'
            ORDER BY started_at DESC
            LIMIT 1
            """,
            customer_id
        )
        return dict(row) if row else None


async def get_conversation_history(conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get messages in a conversation with optional limit."""
    async with get_db_connection() as conn:
        rows = await conn.fetch(
            """
            SELECT * FROM messages
            WHERE conversation_id = $1
            ORDER BY created_at ASC
            LIMIT $2
            """,
            conversation_id,
            limit
        )
        return [dict(row) for row in rows]


# ============================================
# Message Queries
# ============================================

async def create_message(
    conversation_id: str,
    role: str,
    content: str,
    channel: str,
    direction: str,
    channel_message_id: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> str:
    """
    Create new message.

    Returns:
        str: Message UUID
    """
    import json

    async with get_db_connection() as conn:
        # Convert metadata dict to JSON string for JSONB column
        metadata_json = json.dumps(metadata) if metadata else None

        message_id = await conn.fetchval(
            """
            INSERT INTO messages (conversation_id, role, content, channel, direction, channel_message_id, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)
            RETURNING id
            """,
            conversation_id, role, content, channel, direction, channel_message_id, metadata_json
        )
        return str(message_id)


# ============================================
# Ticket Queries
# ============================================

async def create_ticket(
    customer_id: str,
    conversation_id: Optional[str],
    category: str,
    priority: str,
    source_channel: str,
    resolution_notes: Optional[str] = None
) -> str:
    """
    Create new ticket.

    Returns:
        str: Ticket UUID
    """
    async with get_db_connection() as conn:
        ticket_id = await conn.fetchval(
            """
            INSERT INTO tickets (customer_id, conversation_id, category, priority, status, source_channel, resolution_notes)
            VALUES ($1, $2, $3, $4, 'open', $5, $6)
            RETURNING id
            """,
            customer_id, conversation_id, category, priority, source_channel, resolution_notes
        )
        return str(ticket_id)


async def update_ticket_status(ticket_id: str, status: str, resolution_notes: Optional[str] = None):
    """Update ticket status."""
    async with get_db_connection() as conn:
        await conn.execute(
            """
            UPDATE tickets
            SET status = $1,
                resolution_notes = COALESCE($2, resolution_notes),
                resolved_at = CASE WHEN $1 IN ('resolved', 'escalated') THEN NOW() ELSE resolved_at END
            WHERE id = $3
            """,
            status, resolution_notes, ticket_id
        )


async def get_ticket(ticket_id: str) -> Optional[Dict[str, Any]]:
    """Get ticket by ID."""
    async with get_db_connection() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM tickets WHERE id = $1",
            ticket_id
        )
        return dict(row) if row else None


# ============================================
# Knowledge Base Queries
# ============================================

async def search_knowledge_base(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search knowledge base (text search for now, vector search in Module 6).

    Returns:
        List of matching documents
    """
    async with get_db_connection() as conn:
        rows = await conn.fetch(
            """
            SELECT id, title, content, category
            FROM knowledge_base
            WHERE content ILIKE '%' || $1 || '%'
               OR title ILIKE '%' || $1 || '%'
            LIMIT $2
            """,
            query, limit
        )
        return [dict(row) for row in rows]


async def insert_knowledge_entry(title: str, content: str, category: str, embedding: Optional[List[float]] = None) -> str:
    """
    Insert knowledge base entry.

    Returns:
        str: Entry UUID
    """
    async with get_db_connection() as conn:
        entry_id = await conn.fetchval(
            """
            INSERT INTO knowledge_base (title, content, category, embedding)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            title, content, category, embedding
        )
        return str(entry_id)


# ============================================
# Health Check
# ============================================

async def update_conversation_status(conversation_id: int, status: str) -> Optional[Dict[str, Any]]:
    """Update conversation status."""
    async with get_db_connection() as conn:
        row = await conn.fetchrow(
            """
            UPDATE conversations
            SET status = $1, updated_at = NOW()
            WHERE conversation_id = $2
            RETURNING *
            """,
            status, conversation_id
        )
        return dict(row) if row else None


async def check_db_health() -> bool:
    """Check database health."""
    try:
        async with get_db_connection() as conn:
            await conn.fetchval("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
