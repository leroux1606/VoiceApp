"""Embedding generation using sentence-transformers."""

from typing import List, Optional
import hashlib
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.utils.logger import logger


class EmbeddingGenerator:
    """Generate embeddings for text using sentence-transformers."""

    _model_cache: Optional[SentenceTransformer] = None

    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        """
        Initialize embedding generator.

        Args:
            model_name: Name of the sentence-transformer model
            device: Device to use ('cpu' or 'cuda')
        """
        self.model_name = model_name or settings.embedding_model
        self.device = device or settings.embedding_device
        self.model = self._get_model()
        logger.info(f"Initialized embedding generator with model: {self.model_name}")

    @classmethod
    def _get_model(cls) -> SentenceTransformer:
        """Get or create model instance (singleton pattern)."""
        if cls._model_cache is None:
            cls._model_cache = SentenceTransformer(
                settings.embedding_model,
                device=settings.embedding_device
            )
        return cls._model_cache

    def generate(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text

        Returns:
            Embedding vector as list of floats
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}", exc_info=True)
            raise

    def generate_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of input texts
            batch_size: Batch size for processing

        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 10
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}", exc_info=True)
            raise

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings.

        Returns:
            Embedding dimension
        """
        # Get dimension by encoding a dummy text
        dummy_embedding = self.generate("test")
        return len(dummy_embedding)

    @staticmethod
    def compute_similarity(embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score between 0 and 1
        """
        import numpy as np

        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    @staticmethod
    def generate_document_id(text: str, metadata: Optional[dict] = None) -> str:
        """
        Generate a unique document ID based on content and metadata.

        Args:
            text: Document text
            metadata: Optional metadata dictionary

        Returns:
            Unique document ID
        """
        content = text
        if metadata:
            content += str(sorted(metadata.items()))
        hash_obj = hashlib.sha256(content.encode())
        return hash_obj.hexdigest()[:16]

