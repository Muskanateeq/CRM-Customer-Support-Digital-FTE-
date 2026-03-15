"""
Generate Embeddings for Knowledge Base
Runs batch embedding generation for all articles without embeddings
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.client import init_db_pool, close_db_pool
from src.embeddings.vector_search import batch_update_embeddings
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def main():
    """Generate embeddings for all knowledge base articles."""

    print("=" * 60)
    print("Knowledge Base Embeddings Generator")
    print("=" * 60)
    print()

    try:
        # Initialize database pool
        print("Connecting to database...")
        await init_db_pool()
        print("Connected!")
        print()

        # Generate embeddings
        print("Generating embeddings for knowledge base articles...")
        print("This may take a few minutes depending on the number of articles.")
        print()

        result = await batch_update_embeddings(batch_size=50)

        print()
        print("=" * 60)
        print("Results:")
        print(f"  Total articles processed: {result['total']}")
        print(f"  Successfully updated: {result['updated']}")
        print(f"  Failed: {result['failed']}")
        print("=" * 60)
        print()

        if result['updated'] > 0:
            print("Success! Embeddings generated successfully.")
            print("Your agent can now perform semantic search on the knowledge base.")
        else:
            print("No articles needed embedding updates.")

    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"Embedding generation failed: {e}", exc_info=True)
        sys.exit(1)

    finally:
        # Close database pool
        await close_db_pool()
        print()
        print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
