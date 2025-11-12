"""ElevenLabs TTS client implementation."""

from typing import Optional
import httpx
from app.config import settings
from app.utils.logger import logger


class ElevenLabsClient:
    """Client for ElevenLabs Text-to-Speech API."""

    def __init__(self, api_key: Optional[str] = None, voice_id: Optional[str] = None):
        """
        Initialize ElevenLabs client.

        Args:
            api_key: ElevenLabs API key (defaults to settings)
            voice_id: Voice ID to use (defaults to settings)
        """
        self.api_key = api_key or settings.elevenlabs_api_key
        if not self.api_key:
            raise ValueError("ElevenLabs API key is required")

        self.voice_id = voice_id or settings.elevenlabs_voice_id
        self.base_url = "https://api.elevenlabs.io/v1"
        self.client = httpx.AsyncClient(
            headers={
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        logger.info(f"Initialized ElevenLabs client with voice: {self.voice_id}")

    async def text_to_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        model_id: str = "eleven_monolingual_v1",
        stability: float = 0.5,
        similarity_boost: float = 0.75
    ) -> bytes:
        """
        Convert text to speech audio.

        Args:
            text: Text to convert
            voice_id: Voice ID (defaults to instance voice_id)
            model_id: Model ID to use
            stability: Stability parameter (0.0-1.0)
            similarity_boost: Similarity boost parameter (0.0-1.0)

        Returns:
            Audio data as bytes (MP3 format)
        """
        try:
            voice = voice_id or self.voice_id
            url = f"{self.base_url}/text-to-speech/{voice}"

            payload = {
                "text": text,
                "model_id": model_id,
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost
                }
            }

            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            audio_data = response.content
            logger.debug(f"Generated TTS audio: {len(audio_data)} bytes for {len(text)} chars")
            return audio_data

        except httpx.HTTPStatusError as e:
            logger.error(f"ElevenLabs API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error in ElevenLabs TTS: {str(e)}", exc_info=True)
            raise

    async def get_voices(self) -> list:
        """
        Get list of available voices.

        Returns:
            List of voice dictionaries
        """
        try:
            url = f"{self.base_url}/voices"
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("voices", [])
        except Exception as e:
            logger.error(f"Error getting voices: {str(e)}", exc_info=True)
            raise

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

