"""Base agent class with conversation management and memory."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from app.utils.logger import logger
from app.utils.helpers import calculate_token_estimate, generate_message_id


class Message:
    """Represents a single message in the conversation."""

    def __init__(
        self,
        role: str,
        content: str,
        message_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a message.

        Args:
            role: Message role (user, assistant, system)
            content: Message content
            message_id: Optional unique message ID
            metadata: Optional metadata dictionary
        """
        self.id = message_id or generate_message_id()
        self.role = role
        self.content = content
        self.timestamp = datetime.now()
        self.metadata = metadata or {}
        self.token_count = calculate_token_estimate(content)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "token_count": self.token_count
        }


class BaseAgent(ABC):
    """Abstract base class for all AI agents."""

    def __init__(
        self,
        agent_id: str,
        system_prompt: Optional[str] = None,
        max_history: int = 50,
        max_tokens: int = 4000
    ):
        """
        Initialize the base agent.

        Args:
            agent_id: Unique identifier for the agent
            system_prompt: System prompt for the agent
            max_history: Maximum number of messages to keep in history
            max_tokens: Maximum tokens to use in context window
        """
        self.agent_id = agent_id
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        self.max_history = max_history
        self.max_tokens = max_tokens
        self.conversation_history: List[Message] = []
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.created_at = datetime.now()

        # Add system message if provided
        if self.system_prompt:
            system_msg = Message("system", self.system_prompt)
            self.conversation_history.append(system_msg)

        logger.info(f"Initialized agent: {self.agent_id}")

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """
        Add a message to the conversation history.

        Args:
            role: Message role
            content: Message content
            metadata: Optional metadata

        Returns:
            Created message object
        """
        message = Message(role, content, metadata=metadata)
        self.conversation_history.append(message)

        # Trim history if too long
        if len(self.conversation_history) > self.max_history:
            # Keep system message and recent messages
            system_msgs = [msg for msg in self.conversation_history if msg.role == "system"]
            other_msgs = [msg for msg in self.conversation_history if msg.role != "system"]
            self.conversation_history = system_msgs + other_msgs[-self.max_history + len(system_msgs):]

        logger.debug(f"Added {role} message to agent {self.agent_id}")
        return message

    def get_conversation_context(self, max_tokens: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get conversation context formatted for LLM.

        Args:
            max_tokens: Maximum tokens to include (defaults to self.max_tokens)

        Returns:
            List of message dictionaries
        """
        max_tokens = max_tokens or self.max_tokens
        context = []
        current_tokens = 0

        # Start from most recent messages and work backwards
        for message in reversed(self.conversation_history):
            if current_tokens + message.token_count > max_tokens:
                break
            context.insert(0, {"role": message.role, "content": message.content})
            current_tokens += message.token_count

        return context

    def clear_history(self, keep_system: bool = True) -> None:
        """
        Clear conversation history.

        Args:
            keep_system: Whether to keep system messages
        """
        if keep_system:
            self.conversation_history = [
                msg for msg in self.conversation_history if msg.role == "system"
            ]
        else:
            self.conversation_history = []

        logger.info(f"Cleared history for agent {self.agent_id}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get agent statistics.

        Returns:
            Dictionary with agent statistics
        """
        return {
            "agent_id": self.agent_id,
            "message_count": len(self.conversation_history),
            "total_tokens_used": self.total_tokens_used,
            "total_cost": self.total_cost,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.conversation_history[-1].timestamp.isoformat() if self.conversation_history else None
        }

    @abstractmethod
    async def process(self, user_input: str, **kwargs) -> Dict[str, Any]:
        """
        Process user input and generate response.

        Args:
            user_input: User's input text
            **kwargs: Additional parameters

        Returns:
            Dictionary with response and metadata
        """
        pass

    @abstractmethod
    async def get_response(self, user_input: str, **kwargs) -> str:
        """
        Get text response for user input.

        Args:
            user_input: User's input text
            **kwargs: Additional parameters

        Returns:
            Response text
        """
        pass

    def _update_token_usage(self, tokens: int, cost: float = 0.0) -> None:
        """
        Update token usage and cost tracking.

        Args:
            tokens: Number of tokens used
            cost: Cost in dollars
        """
        self.total_tokens_used += tokens
        self.total_cost += cost
        logger.debug(f"Agent {self.agent_id} used {tokens} tokens, cost: ${cost:.4f}")

