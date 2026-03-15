"""
Embeddings Service - OpenAI Embeddings API Integration
Generates vector embeddings for text using OpenAI's embedding models
"""

import asyncio
from typing import List, Optional
import openai
from openai import AsyncOpenAI

from src.config import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


class EmbeddingsService:
    """
    Service for generating text embeddings using OpenAI API.
    Uses text-embedding-3-small model (1536 dimensions, cost-effective).
    """

    def __init__(self):
        """Initialize embeddings service with AsyncOpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "text-embedding-3-small"  # 1536 dimensions
        self.dimensions = 1536
        self.max_tokens = 8191  # Max tokens for text-embedding-3-small

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed (max 8191 tokens)

        Returns:
            List of floats (1536-dimensional embedding vector)

        Raises:
            openai.APIError: If API call fails
        """
        try:
            # Clean text (remove excessive whitespace)
            text = ' '.join(text.split())

            # Truncate if too long (rough estimate: 4 chars per token)
            max_chars = self.max_tokens * 4
            if len(text) > max_chars:
                text = text[:max_chars]
                logger.warning(f"Text truncated to {max_chars} chars for embedding")

            logger.debug(f"Generating embedding", extra={
                'text_length': len(text),
                'model': self.model,
            })

            # Call OpenAI Embeddings API
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"
            )

            # Extract embedding from response
            embedding = response.data[0].embedding

            logger.debug(f"Embedding generated", extra={
                'dimensions': len(embedding),
            })

            return embedding

        except openai.APIConnectionError as e:
            logger.error(f"OpenAI connection error: {e.__cause__}", exc_info=True)
            raise
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit (429): {e.message}", exc_info=True)
            raise
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI authentication error (401): {e.message}", exc_info=True)
            raise
        except openai.BadRequestError as e:
            logger.error(f"OpenAI bad request (400): {e.message}", exc_info=True)
            raise
        except openai.APIStatusError as e:
            logger.error(f"OpenAI API error {e.status_code}: {e.message}", extra={
                'request_id': e.request_id,
            }, exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating embedding: {e}", exc_info=True)
            raise

    async def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts per batch (max 2048 for OpenAI)

        Returns:
            List of embedding vectors (same order as input)

        Raises:
            openai.APIError: If API call fails
        """
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts", extra={
                'batch_size': batch_size,
                'model': self.model,
            })

            all_embeddings = []

            # Process in batches
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_num = i // batch_size + 1
                total_batches = (len(texts) + batch_size - 1) // batch_size

                logger.info(f"Processing batch {batch_num}/{total_batches}", extra={
                    'batch_start': i,
                    'batch_size': len(batch),
                })

                # Clean texts
                cleaned_batch = [' '.join(text.split()) for text in batch]

                # Truncate long texts
                max_chars = self.max_tokens * 4
                cleaned_batch = [
                    text[:max_chars] if len(text) > max_chars else text
                    for text in cleaned_batch
                ]

                # Call OpenAI API
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=cleaned_batch,
                    encoding_format="float"
                )

                # Extract embeddings (maintain order)
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)

                logger.info(f"Batch {batch_num}/{total_batches} completed", extra={
                    'embeddings_count': len(batch_embeddings),
                })

                # Rate limiting (avoid hitting API limits)
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.2)  # 200ms delay between batches

            logger.info(f"All embeddings generated successfully", extra={
                'total_embeddings': len(all_embeddings),
            })

            return all_embeddings

        except openai.RateLimitError as e:
            logger.error(f"Rate limit hit during batch processing: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}", exc_info=True)
            raise

    async def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.
        Alias for generate_embedding() for clarity in search contexts.

        Args:
            query: Search query text

        Returns:
            Embedding vector (1536 dimensions)
        """
        return await self.generate_embedding(query)

    def get_embedding_dimensions(self) -> int:
        """Get the number of dimensions in embeddings."""
        return self.dimensions

    def get_model_name(self) -> str:
        """Get the embedding model name."""
        return self.model


# Global service instance (singleton)
_embeddings_service: Optional[EmbeddingsService] = None


def get_embeddings_service() -> EmbeddingsService:
    """
    Get or create global embeddings service instance.

    Returns:
        EmbeddingsService instance
    """
    global _embeddings_service

    if _embeddings_service is None:
        _embeddings_service = EmbeddingsService()

    return _embeddings_service


async def generate_embedding(text: str) -> List[float]:
    """
    Convenience function to generate embedding.

    Args:
        text: Text to embed

    Returns:
        Embedding vector
    """
    service = get_embeddings_service()
    return await service.generate_embedding(text)


async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Convenience function to generate batch embeddings.

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors
    """
    service = get_embeddings_service()
    return await service.generate_embeddings_batch(texts)
