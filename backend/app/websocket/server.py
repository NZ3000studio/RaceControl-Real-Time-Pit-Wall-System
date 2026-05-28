"""FastAPI WebSocket endpoint for telemetry streaming.

Manages WebSocket connections, heartbeats, and error handling.
"""

import logging
from typing import Set

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket client connections."""

    def __init__(self) -> None:
        """Initialize connection manager."""
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register WebSocket connection.

        Args:
            websocket: WebSocket connection object
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket) -> None:
        """Unregister WebSocket connection.

        Args:
            websocket: WebSocket connection object
        """
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, data: str) -> None:
        """Broadcast JSON string to all connected clients.

        Args:
            data: JSON string to send

        Disconnects clients that fail to receive.
        """
        dead_connections = set()

        for connection in self.active_connections:
            try:
                await connection.send_text(data)
            except Exception as e:
                logger.debug(f"Failed to send to client: {e}")
                dead_connections.add(connection)

        # Clean up dead connections
        for connection in dead_connections:
            await self.disconnect(connection)

    def get_connection_count(self) -> int:
        """Get active connection count.

        Returns:
            Number of connected clients
        """
        return len(self.active_connections)


# Global connection manager
_manager: ConnectionManager | None = None


def get_manager() -> ConnectionManager:
    """Get or create global connection manager."""
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager


async def telemetry_websocket_handler(websocket: WebSocket) -> None:
    """WebSocket endpoint handler for telemetry streaming.

    Handles:
    - Client connections
    - Heartbeat mechanism
    - Graceful disconnection
    - Error recovery

    Args:
        websocket: FastAPI WebSocket connection
    """
    manager = get_manager()
    await manager.connect(websocket)

    try:
        while True:
            # Wait for client messages (implements heartbeat/ping)
            # In browser, this allows connection to stay alive
            data = await websocket.receive_text()
            # Ignore client messages for now (MVP: server-only broadcast)
            logger.debug(f"Received from client: {data}")

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket)
