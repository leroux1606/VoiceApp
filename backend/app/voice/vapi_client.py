"""Vapi client implementation."""

from typing import Dict, Any, Optional
import httpx
from app.config import settings
from app.utils.logger import logger


class VapiClient:
    """Client for Vapi voice API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Vapi client.

        Args:
            api_key: Vapi API key (defaults to settings)
        """
        self.api_key = api_key or settings.vapi_api_key
        if not self.api_key:
            raise ValueError("Vapi API key is required")

        self.base_url = settings.vapi_api_url
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        logger.info("Initialized Vapi client")

    async def create_call(
        self,
        phone_number: str,
        assistant_id: Optional[str] = None,
        assistant_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a voice call.

        Args:
            phone_number: Phone number to call
            assistant_id: Optional assistant ID
            assistant_config: Optional assistant configuration

        Returns:
            Call creation response
        """
        try:
            url = f"{self.base_url}/call"

            payload: Dict[str, Any] = {
                "phoneNumberId": phone_number
            }

            if assistant_id:
                payload["assistantId"] = assistant_id
            elif assistant_config:
                payload["assistant"] = assistant_config

            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Created Vapi call: {result.get('id')}")
            return result

        except httpx.HTTPStatusError as e:
            logger.error(f"Vapi API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error creating Vapi call: {str(e)}", exc_info=True)
            raise

    async def get_call(self, call_id: str) -> Dict[str, Any]:
        """
        Get call status.

        Args:
            call_id: Call ID

        Returns:
            Call information
        """
        try:
            url = f"{self.base_url}/call/{call_id}"
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting call: {str(e)}", exc_info=True)
            raise

    async def end_call(self, call_id: str) -> Dict[str, Any]:
        """
        End a call.

        Args:
            call_id: Call ID

        Returns:
            Call end response
        """
        try:
            url = f"{self.base_url}/call/{call_id}/end"
            response = await self.client.post(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error ending call: {str(e)}", exc_info=True)
            raise

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

