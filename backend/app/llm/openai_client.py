"""OpenAI API client implementation."""

from typing import AsyncIterator, Dict, List, Optional, Any
from openai import AsyncOpenAI
from app.config import settings
from app.utils.logger import logger


class OpenAIClient:
    """Client for interacting with OpenAI API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key (defaults to settings)
        """
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = settings.openai_model
        logger.info(f"Initialized OpenAI client with model: {self.model}")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send chat completion request to OpenAI.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: Optional system prompt (added as system message)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            functions: Optional list of function definitions
            function_call: Function calling mode
            stream: Whether to stream the response

        Returns:
            Response dictionary with content and metadata
        """
        try:
            # Prepare messages
            chat_messages = messages.copy()
            if system_prompt:
                # Insert system message at the beginning
                chat_messages.insert(0, {"role": "system", "content": system_prompt})

            # Prepare request parameters
            params: Dict[str, Any] = {
                "model": self.model,
                "messages": chat_messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            if functions:
                params["tools"] = [{"type": "function", "function": func} for func in functions]
                if function_call:
                    params["tool_choice"] = function_call

            if stream:
                return await self._stream_chat(params)

            # Non-streaming request
            response = await self.client.chat.completions.create(**params)

            # Extract content
            content = response.choices[0].message.content or ""
            tool_calls = []

            if response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    tool_calls.append({
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    })

            result = {
                "content": content,
                "tool_calls": tool_calls,
                "model": response.model,
                "usage": {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }

            logger.debug(f"OpenAI response: {len(content)} chars, {result['usage']['output_tokens']} tokens")
            return result

        except Exception as e:
            logger.error(f"Error in OpenAI chat: {str(e)}", exc_info=True)
            raise

    async def _stream_chat(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle streaming chat response.

        Args:
            params: Request parameters

        Returns:
            Response dictionary with stream iterator
        """
        stream = await self.client.chat.completions.create(**params, stream=True)
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
            chat_messages = messages.copy()
            if system_prompt:
                chat_messages.insert(0, {"role": "system", "content": system_prompt})

            params = {
                "model": self.model,
                "messages": chat_messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True
            }

            stream = await self.client.chat.completions.create(**params)
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error in OpenAI stream: {str(e)}", exc_info=True)
            raise

    async def get_embeddings(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        """
        Get embeddings for text using OpenAI embeddings API.

        Args:
            text: Input text
            model: Embedding model to use

        Returns:
            List of embedding values
        """
        try:
            response = await self.client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting OpenAI embeddings: {str(e)}", exc_info=True)
            raise

