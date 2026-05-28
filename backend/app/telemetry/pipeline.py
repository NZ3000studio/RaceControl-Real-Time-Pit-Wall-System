"""Async telemetry pipeline: read → normalize → buffer → throttle.

Coordinates AC shared memory reader, normalization, session tracking,
and throttled output for WebSocket broadcast.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from app.models.telemetry import NormalizedTelemetry
from app.session.manager import SessionManager
from app.telemetry.reader import AsyncACReader

logger = logging.getLogger(__name__)

# Poll every 10ms (100Hz)
POLL_INTERVAL = 0.01

# Throttle broadcast to 20Hz (50ms)
BROADCAST_INTERVAL = 0.05


class TelemetryPipeline:
    """Pipeline coordinating telemetry ingestion and output."""

    def __init__(self) -> None:
        """Initialize pipeline."""
        self._reader = AsyncACReader()
        self._session_manager = SessionManager()
        self._latest_telemetry: Optional[NormalizedTelemetry] = None
        self._lock = asyncio.Lock()
        self._running = False

    async def start(self) -> None:
        """Start the telemetry pipeline."""
        if self._running:
            logger.warning("Pipeline already running")
            return

        self._running = True
        logger.info("Telemetry pipeline starting")

        try:
            # Start reader connection attempt
            connect_task = asyncio.create_task(self._reader.connect())
            await asyncio.wait_for(connect_task, timeout=2.0)
        except asyncio.TimeoutError:
            logger.warning("Initial connection attempt timed out, will retry")

        # Start main polling loop
        await self._poll_loop()

    async def stop(self) -> None:
        """Stop the telemetry pipeline."""
        self._running = False
        await self._reader.disconnect()
        logger.info("Telemetry pipeline stopped")

    async def get_latest(self) -> Optional[NormalizedTelemetry]:
        """Get latest buffered telemetry frame.

        Returns:
            Latest NormalizedTelemetry, or None if not available
        """
        async with self._lock:
            return self._latest_telemetry

    async def _poll_loop(self) -> None:
        """Main polling loop: read and buffer telemetry.

        Runs continuously, polling AC at 100Hz, buffering output.
        """
        last_broadcast = 0.0

        try:
            while self._running:
                now = asyncio.get_event_loop().time()

                # Try to read telemetry
                raw_data = await self._reader.read()

                if raw_data is not None:
                    # Normalize and process
                    telem = await self._normalize(raw_data)

                    # Update session state
                    session_state = self._session_manager.update(
                        session_type=raw_data["graphics"]["session"],
                        session_status=raw_data["graphics"]["status"],
                        lap=raw_data["graphics"]["lap"],
                        completed_laps=raw_data["graphics"]["lap"],
                        position=raw_data["graphics"]["position"],
                        fuel=raw_data["physics"]["fuel"],
                        max_fuel=raw_data["physics"]["max_fuel"],
                        driver=raw_data["static"]["player_name"],
                        car=raw_data["static"]["car_model"],
                        track=raw_data["static"]["track"],
                    )

                    # Buffer for broadcast (throttled)
                    if now - last_broadcast >= BROADCAST_INTERVAL:
                        async with self._lock:
                            self._latest_telemetry = telem

                        # Push to broadcaster for WebSocket delivery
                        from app.websocket.broadcaster import get_broadcaster

                        broadcaster = await get_broadcaster()
                        await broadcaster.update(telem)

                        last_broadcast = now

                # Sleep before next poll
                await asyncio.sleep(POLL_INTERVAL)

        except asyncio.CancelledError:
            logger.info("Poll loop cancelled")
        except Exception as e:
            logger.error(f"Poll loop error: {e}", exc_info=True)
        finally:
            self._running = False

    async def _normalize(self, raw_data: dict) -> NormalizedTelemetry:
        """Normalize raw AC data to NormalizedTelemetry.

        Args:
            raw_data: Raw telemetry dict from reader

        Returns:
            NormalizedTelemetry model
        """
        from app.models.telemetry import (
            PhysicsData,
            GraphicsData,
            StaticData,
            WheelData,
            EngineData,
        )

        physics_raw = raw_data["physics"]
        graphics_raw = raw_data["graphics"]
        static_raw = raw_data["static"]

        # Create wheel data from reader's flat array keys
        wheels = [
            WheelData(
                temperature=physics_raw["wheel_temps"][i],
                wear=physics_raw["wheel_wear"][i],
                load=physics_raw["wheel_load"][i],
                slip=physics_raw["wheel_slip_ratio"][i],
                brake_temperature=physics_raw["brake_temps"][i],
            )
            for i in range(4)
        ]

        # max_rpm not available from reader; approximate from current rpm
        max_rpm = max(physics_raw["rpm"] * 1.5, 9000.0)

        # Create engine data
        engine = EngineData(
            rpm=physics_raw["rpm"],
            max_rpm=max_rpm,
            throttle=physics_raw["throttle"],
            brake=physics_raw["brake"],
            clutch=physics_raw["clutch"],
        )

        # Parse lap time from AC string format "M:SS.mmm" or "SS.mmm"
        lap_time_str = graphics_raw.get("current_time", "")
        lap_time = 0.0
        if lap_time_str:
            try:
                parts = lap_time_str.split(":")
                if len(parts) == 2:
                    lap_time = float(parts[0]) * 60.0 + float(parts[1])
                else:
                    lap_time = float(parts[0])
            except (ValueError, IndexError):
                lap_time = 0.0

        # Parse split/last sector time from AC string format
        split_time_str = graphics_raw.get("split_time", "")
        last_sector_time = 0.0
        if split_time_str:
            try:
                parts = split_time_str.split(":")
                if len(parts) == 2:
                    last_sector_time = float(parts[0]) * 60.0 + float(parts[1])
                else:
                    last_sector_time = float(parts[0])
            except (ValueError, IndexError):
                last_sector_time = 0.0

        # Current lap: 1-based from reader's 0-based completed lap count
        lap = graphics_raw["lap"]
        current_lap = lap + 1 if lap > 0 else 1

        # Speed from reader (m/s) — same value used for velocity magnitude
        speed = physics_raw["speed"]

        # Create physics data
        physics = PhysicsData(
            speed=speed,
            velocity_x=0.0,
            velocity_y=0.0,
            velocity_z=0.0,
            acceleration_x=0.0,
            acceleration_y=0.0,
            acceleration_z=0.0,
            rpm=physics_raw["rpm"],
            gear=physics_raw["gear"],
            throttle=physics_raw["throttle"],
            brake=physics_raw["brake"],
            handbrake=physics_raw["handbrake"],
            steering=physics_raw["steer"],
            fuel=physics_raw["fuel"],
            max_fuel=physics_raw["max_fuel"],
            wheels=wheels,
            engine=engine,
            velocity=speed,
            g_force=0.0,
        )

        # Create graphics data
        graphics = GraphicsData(
            session_type=graphics_raw["session"],
            session_status=graphics_raw["status"],
            completed_laps=graphics_raw["lap"],
            current_lap=current_lap,
            current_sector=0,
            last_sector_time=last_sector_time,
            lap_time=lap_time,
            position=graphics_raw["position"],
            num_cars=static_raw.get("number_of_cars", 1),
            fuel_estimate_remaining_laps=graphics_raw["fuel_remaining"],
            abs=graphics_raw["abs_level"],
            tc=graphics_raw["traction_control"],
        )

        # Create static data (air/road temp from graphics packet)
        static = StaticData(
            car_model=static_raw["car_model"],
            track_name=static_raw["track"],
            player_name=static_raw["player_name"],
            air_temp=graphics_raw["ambient_temp"],
            road_temp=graphics_raw["road_temp"],
        )

        # Combine into normalized telemetry
        return NormalizedTelemetry(
            physics=physics,
            graphics=graphics,
            static=static,
            timestamp=datetime.now(),
        )


# Global pipeline instance
_pipeline: Optional[TelemetryPipeline] = None


async def get_pipeline() -> TelemetryPipeline:
    """Get or create global pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = TelemetryPipeline()
    return _pipeline
