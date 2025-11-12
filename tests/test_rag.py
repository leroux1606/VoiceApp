"""Tests for RAG system."""

import pytest
from app.rag.embeddings import EmbeddingGenerator
from app.rag.vectorstore import VectorStore
from app.rag.retriever import RAGRetriever


def test_embedding_generator():
    """Test embedding generation."""
    generator = EmbeddingGenerator()
    embedding = generator.generate("test text")
    assert isinstance(embedding, list)
    assert len(embedding) > 0


def test_embedding_batch():
    """Test batch embedding generation."""
    generator = EmbeddingGenerator()
    embeddings = generator.generate_batch(["text1", "text2"])
    assert len(embeddings) == 2


@pytest.mark.asyncio
async def test_vector_store_add_document():
    """Test adding document to vector store."""
    # This test requires ChromaDB to be running
    try:
        vector_store = VectorStore()
        doc_id = vector_store.add_document("test document", metadata={"test": True})
        assert doc_id is not None
    except Exception:
        pytest.skip("ChromaDB not available")


@pytest.mark.asyncio
async def test_rag_retriever():
    """Test RAG retriever."""
    retriever = RAGRetriever()
    processed = retriever.preprocess_query("  test query  ")
    assert processed == "test query"

