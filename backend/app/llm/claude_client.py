"""Anthropic Claude API client implementation."""

import asyncio
from typing import AsyncIterator, Dict, List, Optional, Any
from anthropic import AsyncAnthropic
from anthropic.types import MessageParam, ToolParam
from app.config import settings
from app.utils.logger import logger


class ClaudeClient:
    """Client for interacting with Anthropic Claude API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key (defaults to settings)
        """
        self.api_key = api_key or settings.anthropic_api_key
        if not self.api_key:
            raise ValueError("Anthropic API key is required")

        self.client = AsyncAnthropic(api_key=self.api_key)
        self.model = settings.anthropic_model
        logger.info(f"Initialized Claude client with model: {self.model}")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        tools: Optional[List[ToolParam]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send chat completion request to Claude.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            tools: Optional list of tools for function calling
            stream: Whether to stream the response

        Returns:
            Response dictionary with content and metadata
        """
        try:
            # Convert messages to Claude format
            claude_messages: List[MessageParam] = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
            ]

            # Prepare request parameters
            params: Dict[str, Any] = {
                "model": self.model,
                "messages": claude_messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            if system_prompt:
                params["system"] = system_prompt

            if tools:
                params["tools"] = tools

            if stream:
                return await self._stream_chat(params)

            # Non-streaming request
            response = await self.client.messages.create(**params)

            # Extract content
            content = ""
            tool_uses = []

            if response.content:
                for block in response.content:
                    if block.type == "text":
                        content += block.text
                    elif block.type == "tool_use":
                        tool_uses.append({
                            "id": block.id,
                            "name": block.name,
                            "input": block.input
                        })

            result = {
                "content": content,
                "tool_uses": tool_uses,
                "model": response.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                },
                "stop_reason": response.stop_reason
            }

            logger.debug(f"Claude response: {len(content)} chars, {result['usage']['output_tokens']} tokens")
            return result

        except Exception as e:
            logger.error(f"Error in Claude chat: {str(e)}", exc_info=True)
            raise

    async def _stream_chat(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle streaming chat response.

        Args:
            params: Request parameters

        Returns:
            Response dictionary with stream iterator
        """
        stream = await self.client.messages.stream(**params)
        return {
            "stream": stream,
            "model": self.model
        }

    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """
        Stream chat response tokens.

        Args:
            messages: List of message dictionaries
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Yields:
            Text chunks from the stream
        """
        try:
            claude_messages: List[MessageParam] = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
            ]

            params: Dict[str, Any] = {
                "model": self.model,
                "messages": claude_messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            if system_prompt:
                params["system"] = system_prompt

            async with self.client.messages.stream(**params) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Error in Claude stream: {str(e)}", exc_info=True)
            raise

    async def get_embeddings(self, text: str) -> List[float]:
        """
        Get embeddings for text (Note: Claude doesn't have embeddings API,
        this is a placeholder for compatibility).

        Args:
            text: Input text

        Returns:
            Empty list (Claude doesn't support embeddings)
        """
        logger.warning("Claude API does not support embeddings")
        return []

