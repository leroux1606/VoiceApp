"""Tests for agents."""

import pytest
from app.agents.chat_agent import ChatAgent
from app.agents.voice_agent import VoiceAgent
from app.agents.base_agent import BaseAgent, Message


@pytest.mark.asyncio
async def test_message_creation():
    """Test message creation."""
    message = Message("user", "Hello, world!")
    assert message.role == "user"
    assert message.content == "Hello, world!"
    assert message.id is not None


@pytest.mark.asyncio
async def test_base_agent_initialization():
    """Test base agent initialization."""
    agent = ChatAgent(agent_id="test_agent")
    assert agent.agent_id == "test_agent"
    assert len(agent.conversation_history) > 0  # Should have system message


@pytest.mark.asyncio
async def test_chat_agent_add_message():
    """Test adding messages to chat agent."""
    agent = ChatAgent(agent_id="test_agent")
    agent.add_message("user", "Test message")
    assert len(agent.conversation_history) == 2  # System + user message


@pytest.mark.asyncio
async def test_chat_agent_get_context():
    """Test getting conversation context."""
    agent = ChatAgent(agent_id="test_agent")
    agent.add_message("user", "Hello")
    context = agent.get_conversation_context()
    assert len(context) >= 1


def test_agent_stats():
    """Test agent statistics."""
    agent = ChatAgent(agent_id="test_agent")
    stats = agent.get_stats()
    assert "agent_id" in stats
    assert "message_count" in stats
    assert "total_tokens_used" in stats

