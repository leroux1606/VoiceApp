"""Voice agent implementation with audio handling."""

from typing import Any, Dict, List, Optional
from app.agents.chat_agent import ChatAgent
from app.voice.elevenlabs_client import ElevenLabsClient
from app.utils.logger import logger


class VoiceAgent(ChatAgent):
    """Voice-enabled agent with TTS capabilities."""

    def __init__(
        self,
        agent_id: str = "voice_agent",
        system_prompt: Optional[str] = None,
        llm_provider: Optional[str] = None,
        max_history: int = 50,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        voice_id: Optional[str] = None
    ):
        """
        Initialize voice agent.

        Args:
            agent_id: Unique agent identifier
            system_prompt: Custom system prompt
            llm_provider: LLM provider to use
            max_history: Maximum conversation history length
            max_tokens: Maximum tokens in context
            temperature: Sampling temperature
            voice_id: ElevenLabs voice ID for TTS
        """
        voice_prompt = (
            "You are a helpful, conversational AI assistant with a natural speaking style. "
            "Keep responses concise and conversational, suitable for voice interaction. "
            "Avoid overly long explanations unless specifically requested."
        )
        super().__init__(
            agent_id=agent_id,
            system_prompt=system_prompt or voice_prompt,
            llm_provider=llm_provider,
            max_history=max_history,
            max_tokens=max_tokens,
            temperature=temperature
        )
        self.tts_client = None
        self.voice_id = voice_id

    async def _get_tts_client(self):
        """Get or initialize TTS client."""
        if self.tts_client is None:
            self.tts_client = ElevenLabsClient(voice_id=self.voice_id)
        return self.tts_client

    async def process(self, user_input: str, **kwargs) -> Dict[str, Any]:
        """
        Process user input and generate response with audio.

        Args:
            user_input: User's input text (from STT)
            **kwargs: Additional parameters

        Returns:
            Dictionary with response, text, and audio metadata
        """
        # Get text response from parent class
        result = await super().process(user_input, **kwargs)
        response_text = result["response"]

        # Generate audio if requested
        if kwargs.get("generate_audio", True):
            try:
                tts_client = await self._get_tts_client()
                audio_data = await tts_client.text_to_speech(
                    text=response_text,
                    voice_id=self.voice_id
                )
                result["audio"] = {
                    "data": audio_data,
                    "format": "mp3",
                    "voice_id": self.voice_id
                }
            except Exception as e:
                logger.warning(f"Failed to generate audio: {str(e)}")
                result["audio"] = None

        return result

    async def text_to_speech(self, text: str, voice_id: Optional[str] = None) -> bytes:
        """
        Convert text to speech audio.

        Args:
            text: Text to convert
            voice_id: Optional voice ID override

        Returns:
            Audio data as bytes
        """
        tts_client = await self._get_tts_client()
        voice = voice_id or self.voice_id
        return await tts_client.text_to_speech(text=text, voice_id=voice)

    async def process_audio_input(self, audio_data: bytes, **kwargs) -> Dict[str, Any]:
        """
        Process audio input (requires STT integration).

        Args:
            audio_data: Audio data bytes
            **kwargs: Additional parameters

        Returns:
            Response dictionary with audio
        """
        # Note: This is a placeholder - actual STT would be integrated here
        # For now, assume text input is provided separately
        logger.warning("Audio input processing requires STT integration")
        raise NotImplementedError("STT integration required for audio input processing")

