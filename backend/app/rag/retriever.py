"""RAG retriever with query processing and re-ranking."""

from typing import List, Dict, Any, Optional
from app.rag.vectorstore import VectorStore
from app.utils.logger import logger
from app.utils.helpers import sanitize_input


class RAGRetriever:
    """Retriever for RAG with query preprocessing and context management."""

    def __init__(self, vector_store: Optional[VectorStore] = None):
        """
        Initialize RAG retriever.

        Args:
            vector_store: Optional vector store instance
        """
        self.vector_store = vector_store or VectorStore()
        logger.info("Initialized RAG retriever")

    def preprocess_query(self, query: str) -> str:
        """
        Preprocess search query.

        Args:
            query: Raw query string

        Returns:
            Preprocessed query
        """
        # Sanitize input
        query = sanitize_input(query, max_length=1000)

        # Remove extra whitespace
        query = " ".join(query.split())

        # Convert to lowercase for better matching (optional)
        # query = query.lower()

        return query

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filter
            min_score: Minimum similarity score threshold

        Returns:
            List of retrieved documents with scores
        """
        # Preprocess query
        processed_query = self.preprocess_query(query)

        # Search vector store
        results = self.vector_store.search(
            query=processed_query,
            top_k=top_k,
            filter_metadata=filter_metadata
        )

        # Convert distance to similarity score (ChromaDB uses distance, lower is better)
        for result in results:
            if result["distance"] is not None:
                # Convert distance to similarity (1 - normalized distance)
                # Assuming max distance is around 2.0 for cosine distance
                similarity = max(0.0, 1.0 - (result["distance"] / 2.0))
                result["score"] = similarity
            else:
                result["score"] = 1.0

        # Filter by minimum score
        if min_score is not None:
            results = [r for r in results if r.get("score", 0) >= min_score]

        logger.debug(f"Retrieved {len(results)} documents for query: {query[:50]}...")
        return results

    def retrieve_with_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        max_context_length: int = 4000,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve documents and format as context for LLM.

        Args:
            query: Search query
            top_k: Number of results to retrieve
            max_context_length: Maximum characters in context
            filter_metadata: Optional metadata filter

        Returns:
            Dictionary with context string and source documents
        """
        # Retrieve documents
        results = self.retrieve(query, top_k=top_k, filter_metadata=filter_metadata)

        # Build context string
        context_parts = []
        sources = []
        current_length = 0

        for result in results:
            doc_text = result["document"]
            doc_length = len(doc_text)

            if current_length + doc_length > max_context_length:
                break

            context_parts.append(doc_text)
            sources.append({
                "id": result["id"],
                "metadata": result.get("metadata", {}),
                "score": result.get("score", 0)
            })
            current_length += doc_length

        context = "\n\n".join(context_parts)

        return {
            "context": context,
            "sources": sources,
            "query": query,
            "num_sources": len(sources)
        }

    def rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Re-rank search results (simple implementation using existing scores).

        Args:
            query: Original query
            results: List of search results
            top_k: Number of top results to return

        Returns:
            Re-ranked results
        """
        # Sort by score (descending)
        sorted_results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)

        if top_k:
            sorted_results = sorted_results[:top_k]

        return sorted_results

    def format_context_for_llm(
        self,
        context_data: Dict[str, Any],
        include_sources: bool = True
    ) -> str:
        """
        Format retrieved context for LLM prompt.

        Args:
            context_data: Context data from retrieve_with_context
            include_sources: Whether to include source attribution

        Returns:
            Formatted context string
        """
        context = context_data["context"]
        sources = context_data.get("sources", [])

        if not context:
            return "No relevant context found."

        formatted = f"Relevant Context:\n\n{context}"

        if include_sources and sources:
            formatted += "\n\nSources:\n"
            for i, source in enumerate(sources, 1):
                source_id = source.get("id", "unknown")
                metadata = source.get("metadata", {})
                formatted += f"{i}. Document ID: {source_id}"
                if metadata.get("title"):
                    formatted += f" - {metadata['title']}"
                formatted += "\n"

        return formatted

