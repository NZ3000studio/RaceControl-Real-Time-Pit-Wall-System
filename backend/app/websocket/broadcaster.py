"""Telemetry broadcaster - sends updates to all connected WebSocket clients.

Operates at 20Hz (50ms intervals) via async task.
"""

import asyncio
import json
import logging

from app.models.telemetry import NormalizedTelemetry
from app.websocket.server import get_manager

logger = logging.getLogger(__name__)

# Broadcast interval: 50ms = 20Hz
BROADCAST_INTERVAL = 0.05


class TelemetryBroadcaster:
    """Broadcast telemetry to connected clients at 20Hz."""

    def __init__(self) -> None:
        """Initialize broadcaster."""
        self._latest_telemetry: NormalizedTelemetry | None = None
        self._running = False
        self._broadcast_task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start broadcaster background task."""
        if self._running:
            logger.warning("Broadcaster already running")
            return

        self._running = True
        self._broadcast_task = asyncio.create_task(self._broadcast_loop())
        logger.info("Telemetry broadcaster started")

    async def stop(self) -> None:
        """Stop broadcaster background task."""
        self._running = False
        if self._broadcast_task:
            await self._broadcast_task
        logger.info("Telemetry broadcaster stopped")

    async def update(self, telemetry: NormalizedTelemetry) -> None:
        """Update latest telemetry frame.

        Args:
            telemetry: NormalizedTelemetry frame
        """
        self._latest_telemetry = telemetry

    async def _broadcast_loop(self) -> None:
        """Main broadcast loop: send telemetry at 20Hz to all clients."""
        try:
            while self._running:
                if self._latest_telemetry is not None:
                    # Serialize to JSON
                    json_data = self._latest_telemetry.model_dump_json()

                    # Broadcast to all connected clients
                    manager = get_manager()
                    await manager.broadcast(json_data)

                    # Log connection count
                    conn_count = manager.get_connection_count()
                    if conn_count > 0:
                        logger.debug(f"Broadcast to {conn_count} clients (20Hz)")

                # Sleep until next broadcast
                await asyncio.sleep(BROADCAST_INTERVAL)

        except asyncio.CancelledError:
            logger.info("Broadcast loop cancelled")
        except Exception as e:
            logger.error(f"Broadcast loop error: {e}", exc_info=True)
        finally:
            self._running = False


# Global broadcaster instance
_broadcaster: TelemetryBroadcaster | None = None


async def get_broadcaster() -> TelemetryBroadcaster:
    """Get or create global broadcaster instance."""
    global _broadcaster
    if _broadcaster is None:
        _broadcaster = TelemetryBroadcaster()
    return _broadcaster
