"""Factory for LLM client selection and management."""

from typing import Optional, Dict, Any, List
from enum import Enum
from app.llm.claude_client import ClaudeClient
from app.llm.openai_client import OpenAIClient
from app.config import settings
from app.utils.logger import logger


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    CLAUDE = "claude"
    OPENAI = "openai"


class LLMFactory:
    """Factory for creating and managing LLM clients."""

    _clients: Dict[str, Any] = {}
    _default_provider: LLMProvider = LLMProvider.CLAUDE

    @classmethod
    def get_client(cls, provider: Optional[str] = None) -> Any:
        """
        Get LLM client instance.

        Args:
            provider: Provider name ('claude' or 'openai'), defaults to configured provider

        Returns:
            LLM client instance
        """
        provider = provider or cls._default_provider.value

        if provider not in cls._clients:
            if provider == LLMProvider.CLAUDE.value:
                if not settings.anthropic_api_key:
                    raise ValueError("Anthropic API key not configured")
                cls._clients[provider] = ClaudeClient()
            elif provider == LLMProvider.OPENAI.value:
                if not settings.openai_api_key:
                    raise ValueError("OpenAI API key not configured")
                cls._clients[provider] = OpenAIClient()
            else:
                raise ValueError(f"Unknown LLM provider: {provider}")

        return cls._clients[provider]

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """
        Get list of available providers based on configured API keys.

        Returns:
            List of available provider names
        """
        available = []
        if settings.anthropic_api_key:
            available.append(LLMProvider.CLAUDE.value)
        if settings.openai_api_key:
            available.append(LLMProvider.OPENAI.value)
        return available

    @classmethod
    def get_fallback_client(cls) -> Any:
        """
        Get fallback client if primary fails.

        Returns:
            Fallback LLM client instance
        """
        available = cls.get_available_providers()
        if not available:
            raise ValueError("No LLM providers configured")

        # Try to get a different provider than default
        default = cls._default_provider.value
        for provider in available:
            if provider != default:
                try:
                    return cls.get_client(provider)
                except Exception as e:
                    logger.warning(f"Failed to get fallback client {provider}: {e}")

        # Fall back to default if no alternative available
        return cls.get_client()

    @classmethod
    async def chat_with_fallback(
        cls,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Chat with automatic fallback on failure.

        Args:
            messages: List of message dictionaries
            provider: Preferred provider
            **kwargs: Additional chat parameters

        Returns:
            Response dictionary
        """
        try:
            client = cls.get_client(provider)
            return await client.chat(messages, **kwargs)
        except Exception as e:
            logger.warning(f"Primary provider failed: {e}, trying fallback")
            fallback_client = cls.get_fallback_client()
            return await fallback_client.chat(messages, **kwargs)

    @classmethod
    def set_default_provider(cls, provider: str) -> None:
        """
        Set default LLM provider.

        Args:
            provider: Provider name
        """
        if provider not in [p.value for p in LLMProvider]:
            raise ValueError(f"Invalid provider: {provider}")
        cls._default_provider = LLMProvider(provider)
        logger.info(f"Set default LLM provider to: {provider}")

