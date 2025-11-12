"""Vector store implementation using ChromaDB."""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings
from app.rag.embeddings import EmbeddingGenerator
from app.utils.logger import logger
from app.utils.helpers import chunk_text


class VectorStore:
    """Vector store for document embeddings using ChromaDB."""

    def __init__(
        self,
        collection_name: Optional[str] = None,
        embedding_generator: Optional[EmbeddingGenerator] = None
    ):
        """
        Initialize vector store.

        Args:
            collection_name: Name of the ChromaDB collection
            embedding_generator: Optional embedding generator instance
        """
        self.collection_name = collection_name or settings.chroma_collection_name
        self.embedding_generator = embedding_generator or EmbeddingGenerator()

        # Initialize ChromaDB client
        try:
            self.client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port
            )
            logger.info(f"Connected to ChromaDB at {settings.chroma_host}:{settings.chroma_port}")
        except Exception as e:
            logger.warning(f"Failed to connect to ChromaDB, using persistent client: {e}")
            # Fallback to persistent client
            self.client = chromadb.PersistentClient(path="./chroma_db")

        # Get or create collection
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        """Get existing collection or create new one."""
        try:
            collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Retrieved existing collection: {self.collection_name}")
            return collection
        except Exception:
            # Collection doesn't exist, create it
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "AI Agent System Document Store"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
            return collection

    def add_document(
        self,
        text: str,
        document_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a single document to the vector store.

        Args:
            text: Document text
            document_id: Optional document ID
            metadata: Optional metadata dictionary

        Returns:
            Document ID
        """
        # Generate embedding
        embedding = self.embedding_generator.generate(text)

        # Generate document ID if not provided
        if not document_id:
            document_id = self.embedding_generator.generate_document_id(text, metadata)

        # Prepare metadata
        doc_metadata = metadata or {}
        doc_metadata["text_length"] = len(text)

        # Add to collection
        self.collection.add(
            ids=[document_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[doc_metadata]
        )

        logger.debug(f"Added document {document_id} to vector store")
        return document_id

    def add_documents(
        self,
        texts: List[str],
        document_ids: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """
        Add multiple documents to the vector store.

        Args:
            texts: List of document texts
            document_ids: Optional list of document IDs
            metadatas: Optional list of metadata dictionaries

        Returns:
            List of document IDs
        """
        # Generate embeddings in batch
        embeddings = self.embedding_generator.generate_batch(texts)

        # Generate IDs if not provided
        if not document_ids:
            document_ids = [
                self.embedding_generator.generate_document_id(text, metadata)
                for text, metadata in zip(texts, metadatas or [None] * len(texts))
            ]

        # Prepare metadatas
        if not metadatas:
            metadatas = [{"text_length": len(text)} for text in texts]
        else:
            for i, metadata in enumerate(metadatas):
                metadata["text_length"] = len(texts[i])

        # Add to collection
        self.collection.add(
            ids=document_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

        logger.info(f"Added {len(texts)} documents to vector store")
        return document_ids

    def add_document_chunked(
        self,
        text: str,
        document_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ) -> List[str]:
        """
        Add a document split into chunks.

        Args:
            text: Document text
            document_id: Base document ID
            metadata: Optional metadata
            chunk_size: Chunk size (defaults to settings)
            chunk_overlap: Chunk overlap (defaults to settings)

        Returns:
            List of chunk IDs
        """
        chunk_size = chunk_size or settings.rag_chunk_size
        chunk_overlap = chunk_overlap or settings.rag_chunk_overlap

        # Split into chunks
        chunks = chunk_text(text, chunk_size, chunk_overlap)

        # Generate chunk IDs
        base_id = document_id or self.embedding_generator.generate_document_id(text, metadata)
        chunk_ids = [f"{base_id}_chunk_{i}" for i in range(len(chunks))]

        # Prepare metadata for each chunk
        chunk_metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_meta = (metadata or {}).copy()
            chunk_meta.update({
                "chunk_index": i,
                "total_chunks": len(chunks),
                "base_document_id": base_id
            })
            chunk_metadatas.append(chunk_meta)

        # Add chunks
        return self.add_documents(chunks, chunk_ids, chunk_metadatas)

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query: Search query text
            top_k: Number of results to return
            filter_metadata: Optional metadata filter

        Returns:
            List of search results with documents, metadata, and distances
        """
        top_k = top_k or settings.rag_top_k

        # Generate query embedding
        query_embedding = self.embedding_generator.generate(query)

        # Perform search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata
        )

        # Format results
        formatted_results = []
        if results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None
                })

        logger.debug(f"Found {len(formatted_results)} results for query")
        return formatted_results

    def delete_document(self, document_id: str) -> None:
        """
        Delete a document from the vector store.

        Args:
            document_id: Document ID to delete
        """
        self.collection.delete(ids=[document_id])
        logger.info(f"Deleted document {document_id}")

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document dictionary or None if not found
        """
        results = self.collection.get(ids=[document_id])
        if results["ids"]:
            return {
                "id": results["ids"][0],
                "document": results["documents"][0],
                "metadata": results["metadatas"][0]
            }
        return None

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.

        Returns:
            Dictionary with collection statistics
        """
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "embedding_dimension": self.embedding_generator.get_embedding_dimension()
        }

