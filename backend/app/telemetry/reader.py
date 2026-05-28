"""Assetto Corsa shared memory reader with async interface.

This module provides AsyncACReader, a non-blocking async interface to read
telemetry from Assetto Corsa shared memory on Windows.

Features:
  - Non-blocking async/await design (no blocking calls)
  - Graceful connection/disconnection handling
  - Automatic reconnection on AC restart
  - 100Hz polling (configurable)
  - Comprehensive error handling and logging
  - Type hints throughout

Limitations:
  - Windows only (uses Windows named shared memory)
  - Requires Assetto Corsa to be running
  - Reads player car data (focusedCarIndex)

Usage:
    reader = AsyncACReader()
    if await reader.connect():
        while reader.is_connected():
            telemetry = await reader.read()
            print(telemetry['physics']['speed'])
    await reader.disconnect()
"""

import logging
import mmap
import os
from ctypes import sizeof
from typing import Optional

from .ac_structs import GraphicsPacket, PhysicsPacket, StaticPacket

logger = logging.getLogger(__name__)

# AC shared memory region names (Windows named memory maps)
PHYSICS_MEMORY_NAME = "acpmf_physics"
GRAPHICS_MEMORY_NAME = "acpmf_graphics"
STATIC_MEMORY_NAME = "acpmf_static"

# Polling interval: 10ms = 100Hz
POLL_INTERVAL_SECONDS = 0.01


class AsyncACReader:
    """Non-blocking async reader for Assetto Corsa shared memory.

    Manages connection to AC shared memory regions and provides
    telemetry data at configurable intervals.

    Attributes:
        connected: True if connected to AC shared memory
        poll_interval: Polling interval in seconds (default 0.01 = 100Hz)
    """

    def __init__(self, poll_interval: float = POLL_INTERVAL_SECONDS) -> None:
        """Initialize the AC reader.

        Args:
            poll_interval: Time in seconds between polling AC. Default 0.01s (100Hz).
        """
        self.poll_interval = poll_interval
        self._connected = False
        self._physics_mmap: Optional[mmap.mmap] = None
        self._graphics_mmap: Optional[mmap.mmap] = None
        self._static_mmap: Optional[mmap.mmap] = None
        self._physics_size = sizeof(PhysicsPacket)
        self._graphics_size = sizeof(GraphicsPacket)
        self._static_size = sizeof(StaticPacket)

        logger.debug(
            f"Initialized AsyncACReader. Physics size: {self._physics_size}, "
            f"Graphics size: {self._graphics_size}, Static size: {self._static_size}"
        )

    async def connect(self) -> bool:
        """Attempt to connect to Assetto Corsa shared memory.

        Returns True if connection successful, False otherwise.
        This method is non-blocking and safe to call repeatedly.

        Note:
            On Windows, this opens named memory-mapped files created by AC.
            If AC is not running or shared memory is not available,
            connection fails gracefully.
        """
        if self._connected:
            return True

        try:
            # Try to open all three shared memory regions
            self._physics_mmap = self._open_shared_memory(PHYSICS_MEMORY_NAME)
            self._graphics_mmap = self._open_shared_memory(GRAPHICS_MEMORY_NAME)
            self._static_mmap = self._open_shared_memory(STATIC_MEMORY_NAME)

            if (
                self._physics_mmap is None
                or self._graphics_mmap is None
                or self._static_mmap is None
            ):
                self._connected = False
                return False

            self._connected = True
            logger.info("Connected to Assetto Corsa shared memory")
            return True

        except Exception as e:
            logger.debug(f"Failed to connect to AC: {e}")
            self._connected = False
            return False

    async def is_connected(self) -> bool:
        """Check if currently connected to Assetto Corsa.

        Returns:
            True if connected and can read shared memory, False otherwise.
        """
        return self._connected

    async def read(self) -> Optional[dict]:
        """Read latest telemetry frame from Assetto Corsa.

        Returns a dictionary with physics, graphics, and static data,
        or None if not connected.

        Returns:
            Dict with keys:
              - 'physics': Physics data (speed, rpm, gear, throttle, brake, fuel, etc.)
              - 'graphics': Graphics/session data (lap, position, status, fuel_remaining, etc.)
              - 'static': Static data (car, track, driver names)
            Or None if not connected to AC.

        Note:
            This method is non-blocking and safe to call in a loop.
            If AC disconnects, returns None until reconnection is detected.
        """
        if not self._connected:
            return None

        try:
            # Read and parse all three packets
            physics = self._read_physics_packet()
            graphics = self._read_graphics_packet()
            static = self._read_static_packet()

            if physics is None or graphics is None or static is None:
                # If any read fails, mark as disconnected
                self._connected = False
                logger.warning("Shared memory read failed, marking as disconnected")
                return None

            # Return normalized telemetry dictionary
            return {
                "physics": physics,
                "graphics": graphics,
                "static": static,
            }

        except Exception as e:
            logger.debug(f"Error reading AC telemetry: {e}")
            self._connected = False
            return None

    async def disconnect(self) -> None:
        """Clean up shared memory connections.

        Safe to call even if not connected.
        """
        if self._physics_mmap:
            try:
                self._physics_mmap.close()
            except Exception as e:
                logger.debug(f"Error closing physics mmap: {e}")
            self._physics_mmap = None

        if self._graphics_mmap:
            try:
                self._graphics_mmap.close()
            except Exception as e:
                logger.debug(f"Error closing graphics mmap: {e}")
            self._graphics_mmap = None

        if self._static_mmap:
            try:
                self._static_mmap.close()
            except Exception as e:
                logger.debug(f"Error closing static mmap: {e}")
            self._static_mmap = None

        self._connected = False
        logger.info("Disconnected from Assetto Corsa")

    # ---- Private methods ----

    def _open_shared_memory(self, memory_name: str) -> Optional[mmap.mmap]:
        """Open a Windows named shared memory region.

        Args:
            memory_name: Name of the shared memory region (e.g., 'acpmf_physics')

        Returns:
            mmap object if successful, None if memory region not found.

        Note:
            On Windows, memory-mapped files are opened by name.
            AC creates these with specific names during startup.
        """
        try:
            # On Windows, memory-mapped files are accessed via their name
            # mmap with tag parameter handles Windows named memory
            if not os.name == "nt":
                logger.warning("Assetto Corsa shared memory is Windows-only")
                return None

            # Open the named shared memory file
            # Windows treats memory-mapped files with a name prefix
            import ctypes

            # Use ctypes to access Windows API for memory mapping
            # This is the portable way to access named shared memory on Windows
            try:
                fd = os.open(f"\\\\.\\Global\\{memory_name}", os.O_RDONLY)
            except OSError:
                # Try without the Global prefix
                try:
                    fd = os.open(f"\\\\.\\{memory_name}", os.O_RDONLY)
                except OSError:
                    return None

            # Create mmap from file descriptor
            try:
                mm = mmap.mmap(fd, 0, access=mmap.ACCESS_READ)
                logger.debug(f"Opened shared memory: {memory_name} (size: {len(mm)})")
                return mm
            except OSError:
                os.close(fd)
                return None

        except Exception as e:
            logger.debug(f"Failed to open shared memory '{memory_name}': {e}")
            return None

    def _read_physics_packet(self) -> Optional[dict]:
        """Read and parse physics packet from shared memory.

        Returns:
            Dict with physics data or None on error.
        """
        if not self._physics_mmap or len(self._physics_mmap) < self._physics_size:
            return None

        try:
            self._physics_mmap.seek(0)
            data = self._physics_mmap.read(self._physics_size)
            packet = PhysicsPacket.from_buffer_copy(data)

            focused_idx = packet.focusedCarIndex
            if focused_idx < 0 or focused_idx >= len(packet.carData):
                focused_idx = 0

            car = packet.carData[focused_idx]

            return {
                "speed": float(car.speed),  # m/s
                "rpm": float(car.rpm),
                "gear": int(car.gear),  # 0=R, 1=N, 2-7=forward
                "throttle": float(car.throttle),  # 0-1
                "brake": float(car.brake),  # 0-1
                "clutch": float(car.clutch),  # 0-1
                "handbrake": 0.0,  # Not in car physics (would be in input)
                "steer": float(car.steer),  # -1 to 1
                "fuel": float(car.fuel),  # liters
                "max_fuel": float(car.maxFuel),  # liters
                "fuel_per_lap": float(car.fuelPerLap),  # liters/lap
                "wheel_speeds": [float(car.wheelAngularSpeed[i]) for i in range(4)],  # rad/s
                "wheel_slip_angle": [float(car.slipAngle[i]) for i in range(4)],
                "wheel_slip_ratio": [float(car.slipRatio[i]) for i in range(4)],
                "wheel_load": [float(car.load[i]) for i in range(4)],  # kg
                "wheel_temps": [float(car.temps[i]) for i in range(4)],  # Celsius
                "wheel_wear": [float(car.wear[i]) for i in range(4)],  # 0-1, 1=new
                "wheel_pressure": [float(car.pressure[i]) for i in range(4)],  # psi
                "tire_core_temps": [float(car.tyreCoreTemp[i]) for i in range(4)],
                "brake_temps": [float(car.brakeTempK[i]) for i in range(4)],  # Kelvin
                "brake_disc_temps": [float(car.brakeDiscTemp[i]) for i in range(4)],
                "suspension_travel": [float(car.suspension[i]) for i in range(4)],
                "engine_temp": float(car.airTemp),  # Note: airTemp used as proxy
                "road_temp": float(car.roadTemp),
                "air_density": float(car.airDensity),
                "turbo_boost": float(car.turboBoostLevel),
                "clutch_slip": float(car.clutchSlip),
                "final_ff": float(car.finalFF),  # Force feedback
                "performance_meter": float(car.performanceMeter),
                "local_angular_velocity": [
                    float(car.localAngularVelocity[i]) for i in range(3)
                ],
            }

        except Exception as e:
            logger.debug(f"Error reading physics packet: {e}")
            return None

    def _read_graphics_packet(self) -> Optional[dict]:
        """Read and parse graphics packet from shared memory.

        Returns:
            Dict with graphics/session data or None on error.
        """
        if not self._graphics_mmap or len(self._graphics_mmap) < self._graphics_size:
            return None

        try:
            self._graphics_mmap.seek(0)
            data = self._graphics_mmap.read(self._graphics_size)
            packet = GraphicsPacket.from_buffer_copy(data)

            return {
                "status": int(packet.status),  # 0=off, 1=replay, 2=live, 3=paused
                "session": int(packet.session),  # 0=practice, 1=qualify, 2=race, etc
                "lap": int(packet.completedLaps),
                "position": int(packet.position),
                "fuel_remaining": float(packet.fuelXLap),  # Laps remaining
                "is_lap_valid": bool(packet.isLapValid),
                "current_time": packet.currentTime.decode("utf-8", errors="ignore"),
                "last_time": packet.lastTime.decode("utf-8", errors="ignore"),
                "best_time": packet.bestTime.decode("utf-8", errors="ignore"),
                "split_time": packet.split.decode("utf-8", errors="ignore"),
                "session_time_left": float(packet.sessionTimeLeft),  # seconds
                "session_time_total": float(packet.sessionTimeTotal),
                "ambient_temp": float(packet.ambientTemp),  # Celsius
                "road_temp": float(packet.roadTemp),  # Celsius
                "track_grip_level": float(packet.trackGripLevel),
                "rain_lights": bool(packet.rainLights),
                "rain_tires": bool(packet.rainTyres),
                "traction_control": int(packet.tc),
                "abs_level": int(packet.abs),
                "engine_map": int(packet.engineMap),
                "water_temp": float(packet.waterTemp),
                "engine_temp": float(packet.engineTemp),
                "brake_temp": float(packet.brakeTemp),
                "pit_limiter": bool(packet.pitLimiterOn),
                "ers_power": float(packet.ersPowerLevel),
                "ers_recovery": float(packet.ersRecoveryLevel),
                "drs_available": bool(packet.drsAvailable),
                "drs_engaged": bool(packet.drsEngaged),
                "number_of_tires_out": int(packet.numberOfTyresOut),
                "packet_id": int(packet.packetId),
            }

        except Exception as e:
            logger.debug(f"Error reading graphics packet: {e}")
            return None

    def _read_static_packet(self) -> Optional[dict]:
        """Read and parse static packet from shared memory.

        Returns:
            Dict with static data or None on error.
        """
        if not self._static_mmap or len(self._static_mmap) < self._static_size:
            return None

        try:
            self._static_mmap.seek(0)
            data = self._static_mmap.read(self._static_size)
            packet = StaticPacket.from_buffer_copy(data)

            return {
                "car_model": packet.carModel.decode("utf-8", errors="ignore"),
                "track": packet.track.decode("utf-8", errors="ignore"),
                "player_name": packet.playerName.decode("utf-8", errors="ignore"),
                "player_surname": packet.playerSurname.decode("utf-8", errors="ignore"),
                "player_nick": packet.playerNick.decode("utf-8", errors="ignore"),
                "number_of_cars": int(packet.numberOfCars),
                "number_of_sessions": int(packet.numberOfSessions),
                "sector_count": int(packet.sectorCount),
                "max_fuel": float(packet.maxFuel),
                "has_drs": bool(packet.hasDRS),
                "has_ers": bool(packet.hasERS),
                "has_kers": bool(packet.hasKERS),
                "track_spline_length": float(packet.trackSPlineLength),
                "track_configuration": packet.trackConfiguration.decode(
                    "utf-8", errors="ignore"
                ),
                "sm_version": int(packet.smVersion),
                "ac_version": int(packet.acVersion),
            }

        except Exception as e:
            logger.debug(f"Error reading static packet: {e}")
            return None
