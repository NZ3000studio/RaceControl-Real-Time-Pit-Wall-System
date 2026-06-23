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
        Reconnects automatically when AC starts or restarts.
        """
        last_broadcast = 0.0
        last_reconnect_attempt = 0.0
        RECONNECT_INTERVAL = 2.0  # Try reconnect every 2 seconds

        try:
            while self._running:
                now = asyncio.get_event_loop().time()

                # Attempt reconnection if not connected
                if not await self._reader.is_connected():
                    if now - last_reconnect_attempt >= RECONNECT_INTERVAL:
                        logger.debug("Attempting reconnection to AC shared memory...")
                        await self._reader.connect()
                        last_reconnect_attempt = now

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
        from math import sqrt

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

        # Create wheel data with 3-layer temps, brake detail, tire forces
        wheels = [
            WheelData(
                temperature=physics_raw["wheel_temps"][i],
                wear=physics_raw["wheel_wear"][i],
                load=physics_raw["wheel_load"][i],
                slip=physics_raw["wheel_slip_ratio"][i],
                brake_temperature=physics_raw["brake_temps"][i],
                pressure=physics_raw["wheel_pressure"][i],
                tire_core_temp=physics_raw["tire_core_temps"][i],
                temp_inner=physics_raw.get("tyre_temp_inner", [0, 0, 0, 0])[i],
                temp_middle=physics_raw.get("tyre_temp_middle", [0, 0, 0, 0])[i],
                temp_outer=physics_raw.get("tyre_temp_outer", [0, 0, 0, 0])[i],
                brake_pressure=physics_raw.get("brake_pressure", [0, 0, 0, 0])[i],
                pad_life=physics_raw.get("pad_life", [0, 0, 0, 0])[i],
                disc_life=physics_raw.get("disc_life", [0, 0, 0, 0])[i],
                tyre_force_x=physics_raw.get("tyre_force_x", [0, 0, 0, 0])[i],
                tyre_force_y=physics_raw.get("tyre_force_y", [0, 0, 0, 0])[i],
                self_aligning_torque=physics_raw.get("self_aligning_torque", [0, 0, 0, 0])[i],
            )
            for i in range(4)
        ]

        # max_rpm: use real value from static struct, fall back to estimate
        max_rpm = float(
            static_raw.get("max_rpm", 0)
            or max(physics_raw["rpm"] * 1.5, 9000.0)
        )

        # Create engine data with ERS/KERS
        engine = EngineData(
            rpm=physics_raw["rpm"],
            max_rpm=max_rpm,
            throttle=physics_raw["throttle"],
            brake=physics_raw["brake"],
            clutch=physics_raw["clutch"],
            kers_charge=physics_raw.get("kers_charge", 0.0),
            kers_current_kj=physics_raw.get("kers_current_kj", 0.0),
            ers_power_level=physics_raw.get("ers_power_level", 0),
            ers_recovery_level=physics_raw.get("ers_recovery_level", 0),
            ers_is_charging=bool(physics_raw.get("ers_is_charging", 0)),
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

        # Use millisecond-precision last sector time if available
        last_sector_ms = graphics_raw.get("last_sector_time", 0)
        last_sector_time = float(last_sector_ms) / 1000.0 if last_sector_ms else 0.0

        # If we didn't get ms value, fall back to parsing the string
        if last_sector_time == 0.0:
            split_time_str = graphics_raw.get("split_time", "")
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

        # Speed from reader (m/s)
        speed = physics_raw["speed"]

        # Real 3D velocity from AC
        vel = physics_raw.get("velocity", [0.0, 0.0, 0.0])
        vx, vy, vz = float(vel[0]), float(vel[1]), float(vel[2])

        # Real 3D acceleration (G-force) from AC
        acc = physics_raw.get("acc_g", [0.0, 0.0, 0.0])
        ax, ay, az = float(acc[0]), float(acc[1]), float(acc[2])
        g_force = sqrt(ax * ax + ay * ay + az * az)

        # Create physics data with orientation, damage, brake bias
        physics = PhysicsData(
            speed=speed,
            velocity_x=vx,
            velocity_y=vy,
            velocity_z=vz,
            acceleration_x=ax,
            acceleration_y=ay,
            acceleration_z=az,
            rpm=physics_raw["rpm"],
            gear=physics_raw["gear"],
            throttle=physics_raw["throttle"],
            brake=physics_raw["brake"],
            handbrake=physics_raw.get("handbrake", 0.0),
            steering=physics_raw["steer"],
            fuel=physics_raw["fuel"],
            max_fuel=static_raw.get("max_fuel", 0.0),
            wheels=wheels,
            engine=engine,
            velocity=speed,
            g_force=g_force,
            heading=physics_raw.get("heading", 0.0),
            pitch=physics_raw.get("pitch", 0.0),
            roll=physics_raw.get("roll", 0.0),
            car_damage=physics_raw.get("car_damage", [0.0, 0.0, 0.0, 0.0, 0.0]),
            suspension_damage=physics_raw.get("suspension_damage", [0.0, 0.0, 0.0, 0.0]),
            brake_bias=physics_raw.get("brake_bias", 0.0),
        )

        # Create graphics data with delta, fuel rate, penalties, stint
        graphics = GraphicsData(
            session_type=graphics_raw["session"],
            session_status=graphics_raw["status"],
            completed_laps=graphics_raw["lap"],
            current_lap=current_lap,
            current_sector=graphics_raw.get("current_sector_index", 0),
            last_sector_time=last_sector_time,
            lap_time=lap_time,
            position=graphics_raw["position"],
            num_cars=static_raw.get("number_of_cars", 1),
            fuel_estimate_remaining_laps=graphics_raw["fuel_remaining"],
            abs=graphics_raw["abs_level"],
            tc=graphics_raw["traction_control"],
            track_grip_level=graphics_raw.get("track_grip_level", 1.0),
            drs_available=physics_raw.get("drs_available", False),
            drs_engaged=physics_raw.get("drs_engaged", False),
            tc_in_action=physics_raw.get("tc_in_action", False),
            abs_in_action=physics_raw.get("abs_in_action", False),
            rain_lights=graphics_raw.get("rain_lights", False),
            rain_tires=graphics_raw.get("rain_tires", False),
            wind_speed=graphics_raw.get("wind_speed", 0.0),
            wind_direction=graphics_raw.get("wind_direction", 0.0),
            flag=graphics_raw.get("flag", 0),
            pit_limiter=graphics_raw.get("pit_limiter", False),
            tyre_compound=graphics_raw.get("tyre_compound", ""),
            delta_lap_time=graphics_raw.get("i_delta_lap_time", 0),
            is_delta_positive=graphics_raw.get("is_delta_positive", False),
            fuel_used_per_lap=graphics_raw.get("fuel_used_per_lap", 0.0),
            penalty_time=graphics_raw.get("penalty_time", 0.0),
            penalty=int(graphics_raw.get("penalty", 0)),
            stint_time_left=int(graphics_raw.get("driver_stint_time_left", 0)),
            number_of_laps=int(graphics_raw.get("number_of_laps", 0)),
            tc_cut=int(graphics_raw.get("tc_cut", 0)),
            clock=graphics_raw.get("clock", 0.0),
            mandatory_pit_done=bool(graphics_raw.get("mandatory_pit_done", False)),
        )

        # Create static data with pit window, car specs, ERS capacity
        static = StaticData(
            car_model=static_raw["car_model"],
            track_name=static_raw["track"],
            player_name=static_raw["player_name"],
            air_temp=physics_raw.get("air_temp", 0.0),
            road_temp=physics_raw.get("road_temp", 0.0),
            pit_window_start=int(static_raw.get("pit_window_start", 0)),
            pit_window_end=int(static_raw.get("pit_window_end", 0)),
            max_power=static_raw.get("max_power", 0.0),
            max_torque=static_raw.get("max_torque", 0.0),
            kers_max_j=static_raw.get("kers_max_j", 0.0),
            ers_max_j=static_raw.get("ers_max_j", 0.0),
            is_timed_race=bool(static_raw.get("is_timed_race", False)),
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
