"""Chat agent implementation using LLM."""

from typing import Any, Dict, List, Optional
from app.agents.base_agent import BaseAgent
from app.llm.llm_factory import LLMFactory
from app.utils.logger import logger
from app.utils.helpers import calculate_cost


class ChatAgent(BaseAgent):
    """Text-based chat agent using LLM."""

    def __init__(
        self,
        agent_id: str = "chat_agent",
        system_prompt: Optional[str] = None,
        llm_provider: Optional[str] = None,
        max_history: int = 50,
        max_tokens: int = 4000,
        temperature: float = 0.7
    ):
        """
        Initialize chat agent.

        Args:
            agent_id: Unique agent identifier
            system_prompt: Custom system prompt
            llm_provider: LLM provider to use ('claude' or 'openai')
            max_history: Maximum conversation history length
            max_tokens: Maximum tokens in context
            temperature: Sampling temperature
        """
        default_prompt = (
            "You are a helpful, knowledgeable, and friendly AI assistant. "
            "Provide accurate, concise, and helpful responses to user queries."
        )
        super().__init__(
            agent_id=agent_id,
            system_prompt=system_prompt or default_prompt,
            max_history=max_history,
            max_tokens=max_tokens
        )
        self.llm_provider = llm_provider
        self.temperature = temperature
        self.llm_client = None

    async def _get_llm_client(self):
        """Get or initialize LLM client."""
        if self.llm_client is None:
            self.llm_client = LLMFactory.get_client(self.llm_provider)
        return self.llm_client

    async def process(self, user_input: str, **kwargs) -> Dict[str, Any]:
        """
        Process user input and generate response.

        Args:
            user_input: User's input text
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Dictionary with response and metadata
        """
        try:
            # Add user message to history
            self.add_message("user", user_input)

            # Get conversation context
            context = self.get_conversation_context(
                max_tokens=kwargs.get("max_tokens", self.max_tokens)
            )

            # Get LLM client
            client = await self._get_llm_client()

            # Generate response
            temperature = kwargs.get("temperature", self.temperature)
            response = await client.chat(
                messages=context,
                system_prompt=self.system_prompt if not any(m.get("role") == "system" for m in context) else None,
                temperature=temperature,
                max_tokens=kwargs.get("max_tokens", 2048),
                stream=kwargs.get("stream", False)
            )

            # Extract content
            if isinstance(response, dict) and "stream" in response:
                # Handle streaming response
                content = ""
                async for chunk in response["stream"]:
                    if hasattr(chunk, "delta") and chunk.delta.content:
                        content += chunk.delta.content
                    elif isinstance(chunk, str):
                        content += chunk
                response_content = content
            else:
                response_content = response.get("content", "")

            # Add assistant response to history
            self.add_message("assistant", response_content, metadata={
                "model": response.get("model"),
                "usage": response.get("usage", {})
            })

            # Update token usage
            usage = response.get("usage", {})
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            self._update_token_usage(input_tokens + output_tokens)

            # Calculate cost (rough estimates)
            cost = 0.0
            if "claude" in response.get("model", "").lower():
                cost = calculate_cost(input_tokens, 0.003) + calculate_cost(output_tokens, 0.015)
            elif "gpt-4" in response.get("model", "").lower():
                cost = calculate_cost(input_tokens, 0.01) + calculate_cost(output_tokens, 0.03)

            self._update_token_usage(0, cost)

            return {
                "response": response_content,
                "agent_id": self.agent_id,
                "model": response.get("model"),
                "usage": usage,
                "metadata": {
                    "temperature": temperature,
                    "tool_calls": response.get("tool_calls") or response.get("tool_uses", [])
                }
            }

        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
            error_msg = "I apologize, but I encountered an error processing your request."
            self.add_message("assistant", error_msg)
            raise

    async def get_response(self, user_input: str, **kwargs) -> str:
        """
        Get text response for user input.

        Args:
            user_input: User's input text
            **kwargs: Additional parameters

        Returns:
            Response text
        """
        result = await self.process(user_input, **kwargs)
        return result["response"]

    async def stream_response(self, user_input: str, **kwargs) -> Any:
        """
        Stream response tokens.

        Args:
            user_input: User's input text
            **kwargs: Additional parameters

        Yields:
            Response text chunks
        """
        try:
            # Add user message
            self.add_message("user", user_input)

            # Get context
            context = self.get_conversation_context(
                max_tokens=kwargs.get("max_tokens", self.max_tokens)
            )

            # Get LLM client
            client = await self._get_llm_client()

            # Stream response
            full_response = ""
            async for chunk in client.stream_response(
                messages=context,
                system_prompt=self.system_prompt if not any(m.get("role") == "system" for m in context) else None,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", 2048)
            ):
                full_response += chunk
                yield chunk

            # Add complete response to history
            self.add_message("assistant", full_response)

        except Exception as e:
            logger.error(f"Error streaming response: {str(e)}", exc_info=True)
            raise

