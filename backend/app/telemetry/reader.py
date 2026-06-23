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

# Windows API setup — lazy init to allow import on Linux
_kernel32 = None


def _get_kernel32():
    """Get kernel32 handle (Windows only). Returns None on Linux."""
    global _kernel32
    if _kernel32 is None:
        if os.name == "nt":
            _kernel32 = ctypes.windll.kernel32
            _kernel32.OpenFileMappingW.restype = wintypes.HANDLE
            _kernel32.OpenFileMappingW.argtypes = [
                wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR,
            ]
            _kernel32.MapViewOfFile.restype = wintypes.LPVOID
            _kernel32.MapViewOfFile.argtypes = [
                wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD,
                wintypes.DWORD, ctypes.c_size_t,
            ]
            _kernel32.UnmapViewOfFile.restype = wintypes.BOOL
            _kernel32.UnmapViewOfFile.argtypes = [wintypes.LPCVOID]
            _kernel32.CloseHandle.restype = wintypes.BOOL
            _kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    return _kernel32

FILE_MAP_READ = 0x0004


def _open_shared_memory(name: str, size: int) -> Optional[int]:
    """Open a named shared memory region and map it into our address space.

    Returns the mapped view pointer, or None on failure.
    """
    k32 = _get_kernel32()
    if k32 is None:
        logger.warning("Assetto Corsa shared memory is Windows-only")
        return None

    handle = k32.OpenFileMappingW(FILE_MAP_READ, False, name)
    if not handle:
        return None

    view = k32.MapViewOfFile(handle, FILE_MAP_READ, 0, 0, size)
    k32.CloseHandle(handle)  # handle not needed after MapViewOfFile

    if not view:
        return None

    return view


def _close_shared_memory(view: Optional[int], size: int) -> None:
    """Unmap a shared memory view."""
    k32 = _get_kernel32()
    if view and k32:
        k32.UnmapViewOfFile(view)


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
        k32 = _get_kernel32()
        for view in [self._physics_view, self._graphics_view, self._static_view]:
            if view and k32:
                try:
                    k32.UnmapViewOfFile(view)
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
                "speed": float(pkt.speed_kmh / 3.6),
                "rpm": float(pkt.rpm),
                "gear": int(pkt.gear),
                "throttle": float(pkt.gas),
                "brake": float(pkt.brake),
                "clutch": float(pkt.clutch),
                "handbrake": 0.0,
                "steer": float(pkt.steer_angle),
                "fuel": float(pkt.fuel),
                "fuel_per_lap": 0.0,
                # 3D motion
                "velocity": [float(pkt.velocity[i]) for i in range(3)],
                "acc_g": [float(pkt.acc_g[i]) for i in range(3)],
                "heading": float(pkt.heading),
                "pitch": float(pkt.pitch),
                "roll": float(pkt.roll),
                "cg_height": float(pkt.cg_height),
                "ride_height": [float(pkt.ride_height[i]) for i in range(2)],
                "local_velocity": [float(pkt.local_velocity[i]) for i in range(3)],
                "local_angular_velocity": [
                    float(pkt.local_angular_vel[i]) for i in range(3)
                ],
                # Wheels: 4-element arrays
                "wheel_speeds": [float(pkt.wheel_angular_speed[i]) for i in range(4)],
                "wheel_slip_angle": [float(pkt.slip_angle[i]) for i in range(4)],
                "wheel_slip_ratio": [float(pkt.slip_ratio[i]) for i in range(4)],
                "wheel_load": [float(pkt.wheel_load[i]) for i in range(4)],
                "wheel_temps": [float(pkt.tyre_temp[i]) for i in range(4)],
                "wheel_wear": [float(pkt.tyre_wear[i]) for i in range(4)],
                "wheel_pressure": [float(pkt.wheels_pressure[i]) for i in range(4)],
                "tire_core_temps": [float(pkt.tyre_core_temperature[i]) for i in range(4)],
                "tyre_temp_inner": [float(pkt.tyre_temp_i[i]) for i in range(4)],
                "tyre_temp_middle": [float(pkt.tyre_temp_m[i]) for i in range(4)],
                "tyre_temp_outer": [float(pkt.tyre_temp_o[i]) for i in range(4)],
                "tyre_dirty_level": [float(pkt.tyre_dirty_level[i]) for i in range(4)],
                "camber_rad": [float(pkt.camber_rad[i]) for i in range(4)],
                # Brakes
                "brake_temps": [float(pkt.brake_temp[i]) for i in range(4)],
                "brake_pressure": [float(pkt.brake_pressure[i]) for i in range(4)],
                "pad_life": [float(pkt.pad_life[i]) for i in range(4)],
                "disc_life": [float(pkt.disc_life[i]) for i in range(4)],
                "brake_bias": float(pkt.brake_bias),
                # Tire forces
                "tyre_force_x": [float(pkt.fx[i]) for i in range(4)],
                "tyre_force_y": [float(pkt.fy[i]) for i in range(4)],
                "self_aligning_torque": [float(pkt.mz[i]) for i in range(4)],
                # Suspension
                "suspension_travel": [float(pkt.suspension_travel[i]) for i in range(4)],
                "suspension_damage": [float(pkt.suspension_damage[i]) for i in range(4)],
                # Damage
                "car_damage": [float(pkt.car_damage[i]) for i in range(5)],
                # Engine / temps
                "engine_temp": float(pkt.water_temp),
                "air_temp": float(pkt.air_temp),
                "road_temp": float(pkt.road_temp),
                "air_density": float(pkt.air_density),
                "turbo_boost": float(pkt.turbo_boost),
                "current_max_rpm": int(pkt.current_max_rpm),
                # DRS
                "drs": float(pkt.drs),
                "drs_available": bool(pkt.drs_available),
                "drs_engaged": bool(pkt.drs_enabled),
                # TC / ABS
                "tc": float(pkt.tc),
                "tc_in_action": bool(pkt.tc_in_action),
                "abs": float(pkt.abs),
                "abs_in_action": bool(pkt.abs_in_action),
                # ERS / KERS
                "kers_charge": float(pkt.kers_charge),
                "kers_input": float(pkt.kers_input),
                "kers_current_kj": float(pkt.kers_current_kj),
                "ers_recovery_level": int(pkt.ers_recovery_level),
                "ers_power_level": int(pkt.ers_power_level),
                "ers_heat_charging": int(pkt.ers_heat_charging),
                "ers_is_charging": int(pkt.ers_is_charging),
                # Misc
                "final_ff": float(pkt.final_ff),
                "performance_meter": float(pkt.performance_meter),
                "engine_brake": int(pkt.engine_brake),
                "auto_shifter_on": bool(pkt.auto_shifter_on),
                "ballast": float(pkt.ballast),
                "number_of_tyres_out": int(pkt.number_of_tyres_out),
                # Vibrations (FFB)
                "kerb_vibration": float(pkt.kerb_vibration),
                "slip_vibrations": float(pkt.slip_vibrations),
                "g_vibrations": float(pkt.g_vibrations),
                "abs_vibrations": float(pkt.abs_vibrations),
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
                "session_index": int(pkt.session_index),
                "lap": int(pkt.completed_laps),
                "position": int(pkt.position),
                "number_of_laps": int(pkt.number_of_laps),
                # Fuel
                "fuel_remaining": float(pkt.fuel_estimated_laps),
                "fuel_used_per_lap": float(pkt.fuel_used_per_lap),
                "used_fuel": float(pkt.used_fuel),
                # Lap times (strings + ms ints)
                "is_lap_valid": bool(pkt.is_valid_lap),
                "current_time": wchar_to_str(pkt.current_time),
                "last_time": wchar_to_str(pkt.last_time),
                "best_time": wchar_to_str(pkt.best_time),
                "split_time": wchar_to_str(pkt.split),
                "i_current_time": int(pkt.i_current_time),
                "i_last_time": int(pkt.i_last_time),
                "i_best_time": int(pkt.i_best_time),
                "i_split": int(pkt.i_split),
                # Delta
                "delta_lap_time": wchar_to_str(pkt.delta_lap_time),
                "i_delta_lap_time": int(pkt.i_delta_lap_time),
                "is_delta_positive": bool(pkt.is_delta_positive),
                "estimated_lap_time": wchar_to_str(pkt.estimated_lap_time),
                # Session time
                "session_time_left": float(pkt.session_time_left),
                "clock": float(pkt.clock),
                # Track / environment
                "track_grip_level": float(pkt.surface_grip),
                "wind_speed": float(pkt.wind_speed),
                "wind_direction": float(pkt.wind_direction),
                "rain_lights": bool(pkt.rain_lights),
                "rain_tires": bool(pkt.rain_tyres),
                "track_status": wchar_to_str(pkt.track_status),
                # Assists
                "traction_control": int(pkt.tc),
                "tc_cut": int(pkt.tc_cut),
                "abs_level": int(pkt.abs),
                "engine_map": int(pkt.engine_map),
                # Pit / penalties
                "pit_limiter": bool(pkt.is_in_pit_lane),
                "is_in_pit": bool(pkt.is_in_pit),
                "penalty_time": float(pkt.penalty_time),
                "penalty": int(pkt.penalty),
                "flag": int(pkt.flag),
                "mandatory_pit_done": bool(pkt.mandatory_pit_done),
                # Stint
                "driver_stint_time_left": int(pkt.driver_stint_time_left),
                "driver_stint_total_time_left": int(pkt.driver_stint_total_time_left),
                # Tyre / car info
                "tyre_compound": wchar_to_str(pkt.tyre_compound),
                "current_sector_index": int(pkt.current_sector_index),
                "last_sector_time": int(pkt.last_sector_time),
                "distance_traveled": float(pkt.distance_traveled),
                "active_cars": int(pkt.active_cars),
                # Other
                "engine_temp": float(pkt.exhaust_temperature),
                "packet_id": int(pkt.packet_id),
                "replay_time_multiplier": float(pkt.replay_time_multiplier),
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
                "track_configuration": wchar_to_str(pkt.track_configuration),
                "player_name": wchar_to_str(pkt.player_name),
                "player_surname": wchar_to_str(pkt.player_surname),
                "player_nick": wchar_to_str(pkt.player_nick),
                "car_skin": wchar_to_str(pkt.car_skin),
                "number_of_cars": int(pkt.num_cars),
                "number_of_sessions": int(pkt.number_of_sessions),
                "sector_count": int(pkt.sector_count),
                # Car specs
                "max_fuel": float(pkt.max_fuel),
                "max_rpm": int(pkt.max_rpm),
                "max_power": float(pkt.max_power),
                "max_torque": float(pkt.max_torque),
                "max_turbo_boost": float(pkt.max_turbo_boost),
                "tyre_radius": [float(pkt.tyre_radius[i]) for i in range(4)],
                "suspension_max_travel": [float(pkt.suspension_max_travel[i]) for i in range(4)],
                # Track
                "track_spline_length": float(pkt.track_spline_length),
                # Features
                "has_drs": bool(pkt.has_drs),
                "has_ers": bool(pkt.has_ers),
                "has_kers": bool(pkt.has_kers),
                # ERS/KERS capacity
                "kers_max_j": float(pkt.kers_max_j),
                "ers_max_j": float(pkt.ers_max_j),
                # Session
                "is_timed_race": bool(pkt.is_timed_race),
                "has_extra_lap": bool(pkt.has_extra_lap),
                "pit_window_start": int(pkt.pit_window_start),
                "pit_window_end": int(pkt.pit_window_end),
                "is_online": bool(pkt.is_online),
                # Assists
                "penalties_enabled": bool(pkt.penalties_enabled),
                "aid_fuel_rate": float(pkt.aid_fuel_rate),
                "aid_tire_rate": float(pkt.aid_tire_rate),
                "aid_mechanical_damage": float(pkt.aid_mechanical_damage),
                "aid_allow_tyre_blankets": bool(pkt.aid_allow_tyre_blankets),
                "aid_stability": float(pkt.aid_stability),
                "aid_auto_clutch": bool(pkt.aid_auto_clutch),
                "aid_auto_blip": bool(pkt.aid_auto_blip),
                # Versions
                "sm_version": wchar_to_str(pkt.sm_version),
                "ac_version": wchar_to_str(pkt.ac_version),
            }
        except Exception as e:
            logger.debug(f"Error reading static packet: {e}")
            return None
