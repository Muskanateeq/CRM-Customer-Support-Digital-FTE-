"""
Vector Search - Semantic Search using pgvector
Implements cosine similarity search for embeddings in PostgreSQL
"""

import asyncio
from typing import List, Dict, Any, Optional
import numpy as np

from src.database.client import get_db_connection
from src.embeddings.service import get_embeddings_service
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def search_knowledge_base_semantic(
    query: str,
    limit: int = 5,
    similarity_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Perform semantic search on knowledge base using vector similarity.

    Uses cosine similarity with pgvector's <=> operator.
    Returns articles most similar to the query.

    Args:
        query: Search query text
        limit: Maximum number of results to return
        similarity_threshold: Minimum similarity score (0-1, default 0.7)

    Returns:
        List of matching articles with similarity scores
    """

    # TEMPORARY FIX: Skip vector search if embeddings not available
    # Use text-based search directly (faster and works without OpenAI API)
    logger.info(f"Using text-based search (embeddings disabled)", extra={
        'query_length': len(query),
        'limit': limit,
    })
    return await _fallback_text_search(query, limit)

    # Original vector search code (disabled temporarily)
    # Uncomment when OpenAI API quota is available
    """
    try:
        logger.info(f"Performing semantic search", extra={
            'query_length': len(query),
            'limit': limit,
            'threshold': similarity_threshold,
        })

        # Generate embedding for query
        embeddings_service = get_embeddings_service()
        query_embedding = await embeddings_service.generate_query_embedding(query)

        # Convert to PostgreSQL vector format
        query_vector = '[' + ','.join(map(str, query_embedding)) + ']'

        # Perform vector similarity search using pgvector
        async with get_db_connection() as conn:
            rows = await conn.fetch(
                \"\"\"
                SELECT
                    id,
                    title,
                    content,
                    category,
                    1 - (embedding <=> $1::vector) AS similarity
                FROM knowledge_base
                WHERE embedding IS NOT NULL
                    AND 1 - (embedding <=> $1::vector) >= $2
                ORDER BY embedding <=> $1::vector
                LIMIT $3
                \"\"\",
                query_vector,
                similarity_threshold,
                limit
            )

        results = [dict(row) for row in rows]

        logger.info(f"Semantic search completed", extra={
            'results_count': len(results),
            'top_similarity': results[0]['similarity'] if results else 0,
        })

        return results

    except Exception as e:
        logger.error(f"Semantic search failed: {e}", exc_info=True)
        # Fallback to text search
        logger.warning("Falling back to text-based search")
        return await _fallback_text_search(query, limit)
    """


async def _fallback_text_search(query: str, limit: int) -> List[Dict[str, Any]]:
    """
    Fallback to text-based search if vector search fails.

    Args:
        query: Search query
        limit: Maximum results

    Returns:
        List of matching articles
    """
    try:
        async with get_db_connection() as conn:
            rows = await conn.fetch(
                """
                SELECT id, title, content, category, 0.5 AS similarity
                FROM knowledge_base
                WHERE content ILIKE '%' || $1 || '%'
                   OR title ILIKE '%' || $1 || '%'
                LIMIT $2
                """,
                query, limit
            )
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Fallback text search failed: {e}", exc_info=True)
        return []


async def insert_knowledge_base_article(
    title: str,
    content: str,
    category: str,
    generate_embedding: bool = True
) -> str:
    """
    Insert article into knowledge base with optional embedding generation.

    Args:
        title: Article title
        content: Article content
        category: Article category
        generate_embedding: Whether to generate embedding (default True)

    Returns:
        Article ID (UUID)
    """
    try:
        logger.info(f"Inserting knowledge base article", extra={
            'title': title,
            'category': category,
            'generate_embedding': generate_embedding,
        })

        # Generate embedding if requested
        embedding = None
        if generate_embedding:
            embeddings_service = get_embeddings_service()
            # Combine title and content for embedding
            text_to_embed = f"{title}\n\n{content}"
            embedding_vector = await embeddings_service.generate_embedding(text_to_embed)
            # Convert to PostgreSQL vector format
            embedding = '[' + ','.join(map(str, embedding_vector)) + ']'

        # Insert into database
        async with get_db_connection() as conn:
            article_id = await conn.fetchval(
                """
                INSERT INTO knowledge_base (title, content, category, embedding)
                VALUES ($1, $2, $3, $4::vector)
                RETURNING id
                """,
                title, content, category, embedding
            )

        logger.info(f"Article inserted successfully", extra={
            'article_id': str(article_id),
            'has_embedding': embedding is not None,
        })

        return str(article_id)

    except Exception as e:
        logger.error(f"Failed to insert article: {e}", exc_info=True)
        raise


async def update_article_embedding(article_id: str) -> bool:
    """
    Generate and update embedding for an existing article.

    Args:
        article_id: Article UUID

    Returns:
        True if successful
    """
    try:
        logger.info(f"Updating embedding for article", extra={
            'article_id': article_id,
        })

        # Fetch article
        async with get_db_connection() as conn:
            row = await conn.fetchrow(
                "SELECT title, content FROM knowledge_base WHERE id = $1",
                article_id
            )

        if not row:
            logger.warning(f"Article not found: {article_id}")
            return False

        # Generate embedding
        embeddings_service = get_embeddings_service()
        text_to_embed = f"{row['title']}\n\n{row['content']}"
        embedding_vector = await embeddings_service.generate_embedding(text_to_embed)
        embedding = '[' + ','.join(map(str, embedding_vector)) + ']'

        # Update database
        async with get_db_connection() as conn:
            await conn.execute(
                """
                UPDATE knowledge_base
                SET embedding = $1::vector, updated_at = NOW()
                WHERE id = $2
                """,
                embedding, article_id
            )

        logger.info(f"Embedding updated successfully", extra={
            'article_id': article_id,
        })

        return True

    except Exception as e:
        logger.error(f"Failed to update embedding: {e}", exc_info=True)
        return False


async def batch_update_embeddings(batch_size: int = 50) -> Dict[str, Any]:
    """
    Generate embeddings for all articles without embeddings.

    Args:
        batch_size: Number of articles to process per batch

    Returns:
        Statistics about the update process
    """
    try:
        logger.info(f"Starting batch embedding update", extra={
            'batch_size': batch_size,
        })

        # Fetch articles without embeddings
        async with get_db_connection() as conn:
            rows = await conn.fetch(
                """
                SELECT id, title, content
                FROM knowledge_base
                WHERE embedding IS NULL
                ORDER BY created_at
                """
            )

        if not rows:
            logger.info("No articles need embedding updates")
            return {'total': 0, 'updated': 0, 'failed': 0}

        total = len(rows)
        logger.info(f"Found {total} articles without embeddings")

        # Prepare texts for batch embedding
        article_ids = [str(row['id']) for row in rows]
        texts = [f"{row['title']}\n\n{row['content']}" for row in rows]

        # Generate embeddings in batches
        embeddings_service = get_embeddings_service()
        all_embeddings = await embeddings_service.generate_embeddings_batch(
            texts, batch_size=batch_size
        )

        # Update database
        updated = 0
        failed = 0

        async with get_db_connection() as conn:
            for article_id, embedding_vector in zip(article_ids, all_embeddings):
                try:
                    # Convert to PostgreSQL vector format
                    embedding = '[' + ','.join(map(str, embedding_vector)) + ']'

                    await conn.execute(
                        """
                        UPDATE knowledge_base
                        SET embedding = $1::vector, updated_at = NOW()
                        WHERE id = $2
                        """,
                        embedding, article_id
                    )
                    updated += 1

                except Exception as e:
                    logger.error(f"Failed to update article {article_id}: {e}")
                    failed += 1

        logger.info(f"Batch embedding update completed", extra={
            'total': total,
            'updated': updated,
            'failed': failed,
        })

        return {
            'total': total,
            'updated': updated,
            'failed': failed,
        }

    except Exception as e:
        logger.error(f"Batch embedding update failed: {e}", exc_info=True)
        raise


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Similarity score (0-1, where 1 is identical)
    """
    vec1_np = np.array(vec1)
    vec2_np = np.array(vec2)

    dot_product = np.dot(vec1_np, vec2_np)
    norm1 = np.linalg.norm(vec1_np)
    norm2 = np.linalg.norm(vec2_np)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return float(dot_product / (norm1 * norm2))
