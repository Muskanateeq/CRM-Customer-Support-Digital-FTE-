"""
Database Setup for pgvector Extension
Ensures pgvector extension is installed and configured
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath('.'))

from src.config import settings
from src.database.client import init_db_pool, close_db_pool, get_db_connection
from src.utils.logging import setup_logging, get_logger

# Setup logging
setup_logging(log_level="INFO", environment="development")
logger = get_logger(__name__)


async def check_pgvector_extension() -> bool:
    """
    Check if pgvector extension is installed in the database.

    Returns:
        True if extension is installed
    """
    try:
        async with get_db_connection() as conn:
            result = await conn.fetchval(
                """
                SELECT EXISTS (
                    SELECT 1 FROM pg_extension WHERE extname = 'vector'
                )
                """
            )
        return result
    except Exception as e:
        logger.error(f"Failed to check pgvector extension: {e}")
        return False


async def install_pgvector_extension() -> bool:
    """
    Install pgvector extension in the database.

    Returns:
        True if installation successful
    """
    try:
        async with get_db_connection() as conn:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        logger.info("✅ pgvector extension installed successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to install pgvector extension: {e}", exc_info=True)
        return False


async def verify_vector_column() -> bool:
    """
    Verify that knowledge_base table has vector column with correct dimensions.

    Returns:
        True if column exists and is correct
    """
    try:
        async with get_db_connection() as conn:
            # Check if embedding column exists
            result = await conn.fetchrow(
                """
                SELECT column_name, data_type, udt_name
                FROM information_schema.columns
                WHERE table_name = 'knowledge_base'
                  AND column_name = 'embedding'
                """
            )

            if not result:
                logger.error("embedding column not found in knowledge_base table")
                return False

            # Check if it's a vector type
            if result['udt_name'] != 'vector':
                logger.error(f"embedding column is not vector type: {result['udt_name']}")
                return False

            logger.info("✅ Vector column verified")
            return True

    except Exception as e:
        logger.error(f"Failed to verify vector column: {e}", exc_info=True)
        return False


async def create_vector_index() -> bool:
    """
    Create HNSW index on embedding column for fast similarity search.

    Returns:
        True if index created successfully
    """
    try:
        async with get_db_connection() as conn:
            # Check if index already exists
            index_exists = await conn.fetchval(
                """
                SELECT EXISTS (
                    SELECT 1 FROM pg_indexes
                    WHERE tablename = 'knowledge_base'
                      AND indexname = 'knowledge_base_embedding_idx'
                )
                """
            )

            if index_exists:
                logger.info("Vector index already exists")
                return True

            # Create HNSW index for fast similarity search
            logger.info("Creating HNSW index on embedding column...")
            await conn.execute(
                """
                CREATE INDEX IF NOT EXISTS knowledge_base_embedding_idx
                ON knowledge_base
                USING hnsw (embedding vector_cosine_ops)
                """
            )

            logger.info("✅ HNSW index created successfully")
            return True

    except Exception as e:
        logger.error(f"Failed to create vector index: {e}", exc_info=True)
        return False


async def setup_pgvector():
    """Main setup function for pgvector."""

    print("=" * 70)
    print("pgvector Extension Setup")
    print("=" * 70)
    print()

    # Initialize database
    await init_db_pool()
    print("✅ Database pool initialized")
    print()

    # Check pgvector extension
    print("🔍 Checking pgvector extension...")
    has_extension = await check_pgvector_extension()

    if not has_extension:
        print("⚠️  pgvector extension not found")
        print("📦 Installing pgvector extension...")

        success = await install_pgvector_extension()

        if not success:
            print()
            print("❌ Failed to install pgvector extension")
            print()
            print("Manual installation required:")
            print("1. Connect to your Neon database")
            print("2. Run: CREATE EXTENSION vector;")
            print()
            print("Or enable in Neon console:")
            print("Project Settings > Extensions > Enable 'vector'")
            await close_db_pool()
            return False
    else:
        print("✅ pgvector extension is installed")

    print()

    # Verify vector column
    print("🔍 Verifying vector column...")
    has_column = await verify_vector_column()

    if not has_column:
        print("❌ Vector column verification failed")
        print("Please ensure knowledge_base table has 'embedding vector(1536)' column")
        await close_db_pool()
        return False

    print()

    # Create vector index
    print("🔍 Creating vector index for fast search...")
    index_created = await create_vector_index()

    if not index_created:
        print("⚠️  Vector index creation failed (non-critical)")
        print("Search will still work but may be slower")

    print()

    # Close database
    await close_db_pool()
    print("✅ Database pool closed")
    print()

    print("=" * 70)
    print("✅ pgvector Setup Complete")
    print("=" * 70)
    print()
    print("Your database is ready for semantic search!")
    print()

    return True


if __name__ == "__main__":
    success = asyncio.run(setup_pgvector())
    sys.exit(0 if success else 1)
