"""LiveKit WebRTC client implementation."""

from typing import Dict, Any, Optional, List
from livekit import api
from app.config import settings
from app.utils.logger import logger


class LiveKitClient:
    """Client for LiveKit WebRTC integration."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        ws_url: Optional[str] = None
    ):
        """
        Initialize LiveKit client.

        Args:
            api_key: LiveKit API key (defaults to settings)
            api_secret: LiveKit API secret (defaults to settings)
            ws_url: WebSocket URL (defaults to settings)
        """
        self.api_key = api_key or settings.livekit_api_key
        self.api_secret = api_secret or settings.livekit_api_secret
        self.ws_url = ws_url or settings.livekit_ws_url

        if not self.api_key or not self.api_secret:
            raise ValueError("LiveKit API key and secret are required")

        # Extract base URL for API
        base_url = self.ws_url.replace("ws://", "http://").replace("wss://", "https://")
        self.livekit_api = api.LiveKitAPI(
            url=base_url,
            api_key=self.api_key,
            api_secret=self.api_secret
        )
        logger.info(f"Initialized LiveKit client: {self.ws_url}")

    def create_access_token(
        self,
        room_name: str,
        participant_name: str,
        participant_identity: Optional[str] = None,
        permissions: Optional[Dict[str, bool]] = None
    ) -> str:
        """
        Create access token for LiveKit room.

        Args:
            room_name: Room name
            participant_name: Participant name
            participant_identity: Optional participant identity
            permissions: Optional permissions dictionary

        Returns:
            JWT access token
        """
        try:
            # Default permissions
            if permissions is None:
                permissions = {
                    "canSubscribe": True,
                    "canPublish": True,
                    "canPublishData": True
                }

            # Create token
            token = api.AccessToken(self.api_key, self.api_secret) \
                .with_identity(participant_identity or participant_name) \
                .with_name(participant_name) \
                .with_grants(
                    api.VideoGrants(
                        room_join=True,
                        room=room_name,
                        can_publish=permissions.get("canPublish", True),
                        can_subscribe=permissions.get("canSubscribe", True),
                        can_publish_data=permissions.get("canPublishData", True)
                    )
                )

            jwt_token = token.to_jwt()
            logger.debug(f"Created LiveKit access token for room: {room_name}")
            return jwt_token

        except Exception as e:
            logger.error(f"Error creating LiveKit token: {str(e)}", exc_info=True)
            raise

    async def create_room(
        self,
        room_name: str,
        empty_timeout: int = 300,
        max_participants: int = 10
    ) -> Dict[str, Any]:
        """
        Create a LiveKit room.

        Args:
            room_name: Room name
            empty_timeout: Empty room timeout in seconds
            max_participants: Maximum participants

        Returns:
            Room information
        """
        try:
            room = await self.livekit_api.room.create_room(
                api.CreateRoomRequest(
                    name=room_name,
                    empty_timeout=empty_timeout,
                    max_participants=max_participants
                )
            )

            logger.info(f"Created LiveKit room: {room_name}")
            return {
                "name": room.name,
                "sid": room.sid,
                "empty_timeout": room.empty_timeout,
                "max_participants": room.max_participants,
                "creation_time": room.creation_time
            }

        except Exception as e:
            logger.error(f"Error creating LiveKit room: {str(e)}", exc_info=True)
            raise

    async def list_rooms(self) -> List[Dict[str, Any]]:
        """
        List all active rooms.

        Returns:
            List of room dictionaries
        """
        try:
            rooms = await self.livekit_api.room.list_rooms()
            return [
                {
                    "name": room.name,
                    "sid": room.sid,
                    "num_participants": room.num_participants,
                    "creation_time": room.creation_time
                }
                for room in rooms.rooms
            ]
        except Exception as e:
            logger.error(f"Error listing rooms: {str(e)}", exc_info=True)
            raise

    async def get_room(self, room_name: str) -> Optional[Dict[str, Any]]:
        """
        Get room information.

        Args:
            room_name: Room name

        Returns:
            Room information or None if not found
        """
        try:
            rooms = await self.list_rooms()
            for room in rooms:
                if room["name"] == room_name:
                    return room
            return None
        except Exception as e:
            logger.error(f"Error getting room: {str(e)}", exc_info=True)
            raise

    async def delete_room(self, room_name: str) -> None:
        """
        Delete a room.

        Args:
            room_name: Room name
        """
        try:
            await self.livekit_api.room.delete_room(api.DeleteRoomRequest(room=room_name))
            logger.info(f"Deleted LiveKit room: {room_name}")
        except Exception as e:
            logger.error(f"Error deleting room: {str(e)}", exc_info=True)
            raise

