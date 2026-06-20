"""Assetto Corsa shared memory reader with async interface.

Uses Windows OpenFileMappingW + MapViewOfFile to access AC shared memory.
"""

import asyncio
import ctypes
import logging
import os
from ctypes import wintypes
from typing import Optional

from .ac_structs import (
    SPageFilePhysics,
    SPageFileGraphic,
    SPageFileStatic,
    wchar_to_str,
)

logger = logging.getLogger(__name__)

PHYSICS_MEMORY_NAME = "Local\\acpmf_physics"
GRAPHICS_MEMORY_NAME = "Local\\acpmf_graphics"
STATIC_MEMORY_NAME = "Local\\acpmf_static"
POLL_INTERVAL_SECONDS = 0.01  # 100Hz

# Windows API setup
_kernel32 = ctypes.windll.kernel32
_kernel32.OpenFileMappingW.restype = wintypes.HANDLE
_kernel32.OpenFileMappingW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
_kernel32.MapViewOfFile.restype = wintypes.LPVOID
_kernel32.MapViewOfFile.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
    ctypes.c_size_t,
]
_kernel32.UnmapViewOfFile.restype = wintypes.BOOL
_kernel32.UnmapViewOfFile.argtypes = [wintypes.LPCVOID]
_kernel32.CloseHandle.restype = wintypes.BOOL
_kernel32.CloseHandle.argtypes = [wintypes.HANDLE]

FILE_MAP_READ = 0x0004


def _open_shared_memory(name: str, size: int) -> Optional[int]:
    """Open a named shared memory region and map it into our address space.

    Returns the mapped view pointer, or None on failure.
    """
    if not os.name == "nt":
        logger.warning("Assetto Corsa shared memory is Windows-only")
        return None

    handle = _kernel32.OpenFileMappingW(FILE_MAP_READ, False, name)
    if not handle:
        return None

    view = _kernel32.MapViewOfFile(handle, FILE_MAP_READ, 0, 0, size)
    _kernel32.CloseHandle(handle)  # handle not needed after MapViewOfFile

    if not view:
        return None

    return view


def _close_shared_memory(view: Optional[int], size: int) -> None:
    """Unmap a shared memory view."""
    if view:
        _kernel32.UnmapViewOfFile(view)


class AsyncACReader:
    """Non-blocking async reader for Assetto Corsa shared memory.

    Uses Windows named shared memory (OpenFileMappingW + MapViewOfFile)
    to read telemetry from AC without polling overhead from os.open.
    """

    def __init__(self, poll_interval: float = POLL_INTERVAL_SECONDS) -> None:
        self.poll_interval = poll_interval
        self._connected = False
        self._physics_view: Optional[int] = None
        self._graphics_view: Optional[int] = None
        self._static_view: Optional[int] = None

        self._physics_size = ctypes.sizeof(SPageFilePhysics)
        self._graphics_size = ctypes.sizeof(SPageFileGraphic)
        self._static_size = ctypes.sizeof(SPageFileStatic)

        logger.debug(
            f"AsyncACReader: physics={self._physics_size}B, "
            f"graphics={self._graphics_size}B, static={self._static_size}B"
        )

    async def connect(self) -> bool:
        """Connect to AC shared memory. Safe to call repeatedly."""
        if self._connected:
            return True

        try:
            self._physics_view = _open_shared_memory(
                PHYSICS_MEMORY_NAME, self._physics_size
            )
            self._graphics_view = _open_shared_memory(
                GRAPHICS_MEMORY_NAME, self._graphics_size
            )
            self._static_view = _open_shared_memory(
                STATIC_MEMORY_NAME, self._static_size
            )

            if (
                self._physics_view is None
                or self._graphics_view is None
                or self._static_view is None
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
        return self._connected

    async def read(self) -> Optional[dict]:
        """Read latest telemetry frame from AC shared memory.

        Returns dict with physics, graphics, static keys, or None if not connected.
        """
        if not self._connected:
            return None

        try:
            physics = self._read_physics_packet()
            graphics = self._read_graphics_packet()
            static = self._read_static_packet()

            if physics is None or graphics is None or static is None:
                self._connected = False
                logger.warning("Shared memory read failed, disconnected")
                return None

            return {"physics": physics, "graphics": graphics, "static": static}

        except Exception as e:
            logger.debug(f"Error reading AC telemetry: {e}")
            self._connected = False
            return None

    async def disconnect(self) -> None:
        for view in [self._physics_view, self._graphics_view, self._static_view]:
            if view:
                try:
                    _kernel32.UnmapViewOfFile(view)
                except Exception as e:
                    logger.debug(f"Error unmapping view: {e}")
        self._physics_view = None
        self._graphics_view = None
        self._static_view = None
        self._connected = False
        logger.info("Disconnected from Assetto Corsa")

    # ---- Private readers ----

    def _read_physics_packet(self) -> Optional[dict]:
        if not self._physics_view:
            return None
        try:
            ArrayType = ctypes.c_ubyte * self._physics_size
            buf = ctypes.cast(
                self._physics_view, ctypes.POINTER(ArrayType)
            ).contents
            pkt = SPageFilePhysics.from_buffer_copy(buf)

            return {
                "speed": float(pkt.speed_kmh / 3.6),  # km/h -> m/s
                "rpm": float(pkt.rpm),
                "gear": int(pkt.gear),  # 0=R, 1=N, 2-7=fwd
                "throttle": float(pkt.gas),  # 0-1
                "brake": float(pkt.brake),  # 0-1
                "clutch": float(pkt.clutch),  # 0-1
                "handbrake": 0.0,
                "steer": float(pkt.steer_angle),  # rad, -1 to 1
                "fuel": float(pkt.fuel),  # liters
                "max_fuel": 0.0,  # from static
                "fuel_per_lap": 0.0,
                "wheel_speeds": [float(pkt.wheel_angular_speed[i]) for i in range(4)],
                "wheel_slip_angle": [float(pkt.slip_angle[i]) for i in range(4)],
                "wheel_slip_ratio": [float(pkt.slip_ratio[i]) for i in range(4)],
                "wheel_load": [float(pkt.wheel_load[i]) for i in range(4)],
                "wheel_temps": [float(pkt.tyre_temp[i]) for i in range(4)],
                "wheel_wear": [float(pkt.tyre_wear[i]) for i in range(4)],
                "wheel_pressure": [float(pkt.wheels_pressure[i]) for i in range(4)],
                "tire_core_temps": [float(pkt.tyre_core_temperature[i]) for i in range(4)],
                "brake_temps": [float(pkt.brake_temp[i]) for i in range(4)],
                "brake_disc_temps": [float(pkt.disc_life[i]) for i in range(4)],
                "suspension_travel": [float(pkt.suspension_travel[i]) for i in range(4)],
                "engine_temp": float(pkt.water_temp),
                "road_temp": float(pkt.road_temp),
                "air_density": float(pkt.air_density),
                "turbo_boost": float(pkt.turbo_boost),
                "clutch_slip": float(pkt.clutch),
                "final_ff": float(pkt.final_ff),
                "performance_meter": float(pkt.performance_meter),
                "local_angular_velocity": [
                    float(pkt.local_angular_vel[i]) for i in range(3)
                ],
            }
        except Exception as e:
            logger.debug(f"Error reading physics packet: {e}")
            return None

    def _read_graphics_packet(self) -> Optional[dict]:
        if not self._graphics_view:
            return None
        try:
            ArrayType = ctypes.c_ubyte * self._graphics_size
            buf = ctypes.cast(
                self._graphics_view, ctypes.POINTER(ArrayType)
            ).contents
            pkt = SPageFileGraphic.from_buffer_copy(buf)

            return {
                "status": int(pkt.status),
                "session": int(pkt.session),
                "lap": int(pkt.completed_laps),
                "position": int(pkt.position),
                "fuel_remaining": float(pkt.fuel_estimated_laps),
                "is_lap_valid": bool(pkt.is_valid_lap),
                "current_time": wchar_to_str(pkt.current_time),
                "last_time": wchar_to_str(pkt.last_time),
                "best_time": wchar_to_str(pkt.best_time),
                "split_time": wchar_to_str(pkt.split),
                "session_time_left": float(pkt.session_time_left),
                "session_time_total": 0.0,
                "ambient_temp": 0.0,  # not in this struct
                "road_temp": 0.0,
                "track_grip_level": float(pkt.surface_grip),
                "rain_lights": bool(pkt.rain_lights),
                "rain_tires": bool(pkt.rain_tyres),
                "traction_control": int(pkt.tc),
                "abs_level": int(pkt.abs),
                "engine_map": int(pkt.engine_map),
                "water_temp": 0.0,
                "engine_temp": float(pkt.exhaust_temperature),
                "brake_temp": 0.0,
                "pit_limiter": bool(pkt.is_in_pit_lane),
                "ers_power": 0.0,
                "ers_recovery": 0.0,
                "drs_available": False,
                "drs_engaged": False,
                "number_of_tires_out": 0,
                "packet_id": int(pkt.packet_id),
            }
        except Exception as e:
            logger.debug(f"Error reading graphics packet: {e}")
            return None

    def _read_static_packet(self) -> Optional[dict]:
        if not self._static_view:
            return None
        try:
            ArrayType = ctypes.c_ubyte * self._static_size
            buf = ctypes.cast(
                self._static_view, ctypes.POINTER(ArrayType)
            ).contents
            pkt = SPageFileStatic.from_buffer_copy(buf)

            return {
                "car_model": wchar_to_str(pkt.car_model),
                "track": wchar_to_str(pkt.track),
                "player_name": wchar_to_str(pkt.player_name),
                "player_surname": wchar_to_str(pkt.player_surname),
                "player_nick": wchar_to_str(pkt.player_nick),
                "number_of_cars": int(pkt.num_cars),
                "number_of_sessions": int(pkt.number_of_sessions),
                "sector_count": int(pkt.sector_count),
                "max_fuel": float(pkt.max_fuel),
                "has_drs": bool(pkt.has_drs),
                "has_ers": bool(pkt.has_ers),
                "has_kers": bool(pkt.has_kers),
                "track_spline_length": float(pkt.track_spline_length),
                "track_configuration": wchar_to_str(pkt.track_configuration),
                "sm_version": wchar_to_str(pkt.sm_version),
                "ac_version": wchar_to_str(pkt.ac_version),
            }
        except Exception as e:
            logger.debug(f"Error reading static packet: {e}")
            return None
