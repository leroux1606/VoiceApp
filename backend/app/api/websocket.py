"""WebSocket endpoints for real-time communication."""

from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.agents.chat_agent import ChatAgent
from app.utils.logger import logger
import json

router = APIRouter()

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """
        Accept WebSocket connection.

        Args:
            websocket: WebSocket connection
            client_id: Client identifier
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket client connected: {client_id}")

    def disconnect(self, client_id: str):
        """
        Remove WebSocket connection.

        Args:
            client_id: Client identifier
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket client disconnected: {client_id}")

    async def send_personal_message(self, message: dict, client_id: str):
        """
        Send message to specific client.

        Args:
            message: Message dictionary
            client_id: Client identifier
        """
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {str(e)}")
                self.disconnect(client_id)

    async def broadcast(self, message: dict):
        """
        Broadcast message to all connected clients.

        Args:
            message: Message dictionary
        """
        disconnected = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {str(e)}")
                disconnected.append(client_id)

        for client_id in disconnected:
            self.disconnect(client_id)


manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time chat.

    Args:
        websocket: WebSocket connection
        client_id: Client identifier
    """
    await manager.connect(websocket, client_id)

    # Create or get agent for this client
    agent = ChatAgent(agent_id=f"ws_{client_id}")

    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "connection",
            "message": "Connected to AI Agent System",
            "client_id": client_id
        }, client_id)

        while True:
            # Receive message
            data = await websocket.receive_json()

            message_type = data.get("type", "message")
            user_message = data.get("message", "")

            if message_type == "message":
                # Process message with agent
                try:
                    result = await agent.process(user_message)

                    # Send response
                    await manager.send_personal_message({
                        "type": "response",
                        "message": result["response"],
                        "agent_id": result["agent_id"],
                        "model": result.get("model"),
                        "usage": result.get("usage")
                    }, client_id)

                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}", exc_info=True)
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Error processing message: {str(e)}"
                    }, client_id)

            elif message_type == "ping":
                # Respond to ping
                await manager.send_personal_message({
                    "type": "pong"
                }, client_id)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"WebSocket client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
        manager.disconnect(client_id)

