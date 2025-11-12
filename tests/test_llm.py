"""Tests for LLM clients."""

import pytest
from unittest.mock import AsyncMock, patch
from app.llm.claude_client import ClaudeClient
from app.llm.openai_client import OpenAIClient
from app.llm.llm_factory import LLMFactory


@pytest.mark.asyncio
async def test_claude_client_initialization():
    """Test Claude client initialization."""
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
        client = ClaudeClient(api_key="test-key")
        assert client.api_key == "test-key"


@pytest.mark.asyncio
async def test_openai_client_initialization():
    """Test OpenAI client initialization."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        client = OpenAIClient(api_key="test-key")
        assert client.api_key == "test-key"


@pytest.mark.asyncio
async def test_llm_factory_get_available_providers():
    """Test LLM factory provider detection."""
    providers = LLMFactory.get_available_providers()
    assert isinstance(providers, list)

