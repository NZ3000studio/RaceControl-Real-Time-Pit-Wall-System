"""Assetto Corsa shared memory struct definitions.

Correct wire-format structs based on simetry crate (Rust #[repr(C, packed(4))]).
All strings are UTF-16LE wide char arrays ([u16; N] in Rust, c_uint16 * N here).
"""

from ctypes import Structure, c_int32, c_float, c_uint16, sizeof
from typing import Final

WHEELS: Final[int] = 4
WCHAR_TIME: Final[int] = 15  # Wide chars for lap/clock strings
WCHAR_TYRE: Final[int] = 33  # Wide chars for compound/name strings


class SPageFilePhysics(Structure):
    """Physics packet from acpmf_physics — single player car data."""

    _pack_ = 4
    _fields_ = [
        ("packet_id", c_int32),
        ("gas", c_float),
        ("brake", c_float),
        ("fuel", c_float),
        ("gear", c_int32),
        ("rpm", c_int32),
        ("steer_angle", c_float),
        ("speed_kmh", c_float),
        ("velocity", c_float * 3),
        ("acc_g", c_float * 3),
        ("wheel_slip", c_float * WHEELS),
        ("wheel_load", c_float * WHEELS),
        ("wheels_pressure", c_float * WHEELS),
        ("wheel_angular_speed", c_float * WHEELS),
        ("tyre_wear", c_float * WHEELS),
        ("tyre_dirty_level", c_float * WHEELS),
        ("tyre_core_temperature", c_float * WHEELS),
        ("camber_rad", c_float * WHEELS),
        ("suspension_travel", c_float * WHEELS),
        ("drs", c_float),
        ("tc", c_float),
        ("heading", c_float),
        ("pitch", c_float),
        ("roll", c_float),
        ("cg_height", c_float),
        ("car_damage", c_float * 5),
        ("number_of_tyres_out", c_int32),
        ("pit_limiter_on", c_int32),
        ("abs", c_float),
        ("kers_charge", c_float),
        ("kers_input", c_float),
        ("auto_shifter_on", c_int32),
        ("ride_height", c_float * 2),
        ("turbo_boost", c_float),
        ("ballast", c_float),
        ("air_density", c_float),
        ("air_temp", c_float),
        ("road_temp", c_float),
        ("local_angular_vel", c_float * 3),
        ("final_ff", c_float),
        ("performance_meter", c_float),
        ("engine_brake", c_int32),
        ("ers_recovery_level", c_int32),
        ("ers_power_level", c_int32),
        ("ers_heat_charging", c_int32),
        ("ers_is_charging", c_int32),
        ("kers_current_kj", c_float),
        ("drs_available", c_int32),
        ("drs_enabled", c_int32),
        ("brake_temp", c_float * WHEELS),
        ("clutch", c_float),
        ("tyre_temp_i", c_float * WHEELS),
        ("tyre_temp_m", c_float * WHEELS),
        ("tyre_temp_o", c_float * WHEELS),
        ("is_ai_controlled", c_int32),
        ("tyre_contact_point", (c_float * 3) * WHEELS),
        ("tyre_contact_normal", (c_float * 3) * WHEELS),
        ("tyre_contact_heading", (c_float * 3) * WHEELS),
        ("brake_bias", c_float),
        ("local_velocity", c_float * 3),
        ("p2p_activations", c_int32),
        ("p2p_status", c_int32),
        ("current_max_rpm", c_int32),
        ("mz", c_float * WHEELS),
        ("fx", c_float * WHEELS),
        ("fy", c_float * WHEELS),
        ("slip_ratio", c_float * WHEELS),
        ("slip_angle", c_float * WHEELS),
        ("tc_in_action", c_int32),
        ("abs_in_action", c_int32),
        ("suspension_damage", c_float * WHEELS),
        ("tyre_temp", c_float * WHEELS),
        ("water_temp", c_float),
        ("brake_pressure", c_float * WHEELS),
        ("front_brake_compound", c_int32),
        ("rear_brake_compound", c_int32),
        ("pad_life", c_float * WHEELS),
        ("disc_life", c_float * WHEELS),
        ("ignition_on", c_int32),
        ("starter_engine_on", c_int32),
        ("is_engine_running", c_int32),
        ("kerb_vibration", c_float),
        ("slip_vibrations", c_float),
        ("g_vibrations", c_float),
        ("abs_vibrations", c_float),
    ]


class SPageFileGraphic(Structure):
    """Graphics/session packet from acpmf_graphics."""

    _pack_ = 4
    _fields_ = [
        ("packet_id", c_int32),
        ("status", c_int32),  # 0=off, 1=replay, 2=live, 3=paused
        ("session", c_int32),  # 0=practice, 1=qualify, 2=race, ...
        ("current_time", c_uint16 * WCHAR_TIME),
        ("last_time", c_uint16 * WCHAR_TIME),
        ("best_time", c_uint16 * WCHAR_TIME),
        ("split", c_uint16 * WCHAR_TIME),
        ("completed_laps", c_int32),
        ("position", c_int32),
        ("i_current_time", c_int32),
        ("i_last_time", c_int32),
        ("i_best_time", c_int32),
        ("session_time_left", c_float),
        ("distance_traveled", c_float),
        ("is_in_pit", c_int32),
        ("current_sector_index", c_int32),
        ("last_sector_time", c_int32),
        ("number_of_laps", c_int32),
        ("tyre_compound", c_uint16 * WCHAR_TYRE),
        ("replay_time_multiplier", c_float),
        ("normalized_car_position", c_float),
        ("active_cars", c_int32),
        ("car_coordinates", (c_float * 3) * 60),
        ("car_id", c_int32 * 60),
        ("player_car_id", c_int32),
        ("penalty_time", c_float),
        ("flag", c_int32),
        ("penalty", c_int32),
        ("ideal_line_on", c_int32),
        ("is_in_pit_lane", c_int32),
        ("surface_grip", c_float),
        ("mandatory_pit_done", c_int32),
        ("wind_speed", c_float),
        ("wind_direction", c_float),
        ("is_setup_menu_visible", c_int32),
        ("main_display_index", c_int32),
        ("secondary_display_index", c_int32),
        ("tc", c_int32),
        ("tc_cut", c_int32),
        ("engine_map", c_int32),
        ("abs", c_int32),
        ("fuel_used_per_lap", c_float),
        ("rain_lights", c_int32),
        ("flashing_lights", c_int32),
        ("lights_stage", c_int32),
        ("exhaust_temperature", c_float),
        ("wiper_lv", c_int32),
        ("driver_stint_total_time_left", c_int32),
        ("driver_stint_time_left", c_int32),
        ("rain_tyres", c_int32),
        ("session_index", c_int32),
        ("used_fuel", c_float),
        ("delta_lap_time", c_uint16 * WCHAR_TIME),
        ("i_delta_lap_time", c_int32),
        ("estimated_lap_time", c_uint16 * WCHAR_TIME),
        ("i_estimated_lap_time", c_int32),
        ("is_delta_positive", c_int32),
        ("i_split", c_int32),
        ("is_valid_lap", c_int32),
        ("fuel_estimated_laps", c_float),
        ("track_status", c_uint16 * WCHAR_TYRE),
        ("missing_mandatory_pits", c_int32),
        ("clock", c_float),
        ("direction_lights_left", c_int32),
        ("direction_lights_right", c_int32),
    ]


class SPageFileStatic(Structure):
    """Static info packet from acpmf_static."""

    _pack_ = 4
    _fields_ = [
        ("sm_version", c_uint16 * WCHAR_TIME),
        ("ac_version", c_uint16 * WCHAR_TIME),
        ("number_of_sessions", c_int32),
        ("num_cars", c_int32),
        ("car_model", c_uint16 * WCHAR_TYRE),
        ("track", c_uint16 * WCHAR_TYRE),
        ("player_name", c_uint16 * WCHAR_TYRE),
        ("player_surname", c_uint16 * WCHAR_TYRE),
        ("player_nick", c_uint16 * WCHAR_TYRE),
        ("sector_count", c_int32),
        ("max_torque", c_float),
        ("max_power", c_float),
        ("max_rpm", c_int32),
        ("max_fuel", c_float),
        ("suspension_max_travel", c_float * WHEELS),
        ("tyre_radius", c_float * WHEELS),
        ("max_turbo_boost", c_float),
        ("deprecated_1", c_float),
        ("deprecated_2", c_float),
        ("penalties_enabled", c_int32),
        ("aid_fuel_rate", c_float),
        ("aid_tire_rate", c_float),
        ("aid_mechanical_damage", c_float),
        ("aid_allow_tyre_blankets", c_int32),
        ("aid_stability", c_float),
        ("aid_auto_clutch", c_int32),
        ("aid_auto_blip", c_int32),
        ("has_drs", c_int32),
        ("has_ers", c_int32),
        ("has_kers", c_int32),
        ("kers_max_j", c_float),
        ("engine_brake_settings_count", c_int32),
        ("ers_power_controller_count", c_int32),
        ("track_spline_length", c_float),
        ("track_configuration", c_uint16 * WCHAR_TYRE),
        ("ers_max_j", c_float),
        ("is_timed_race", c_int32),
        ("has_extra_lap", c_int32),
        ("car_skin", c_uint16 * WCHAR_TYRE),
        ("reversed_grid_positions", c_int32),
        ("pit_window_start", c_int32),
        ("pit_window_end", c_int32),
        ("is_online", c_int32),
    ]


def wchar_to_str(arr) -> str:
    """Decode a c_uint16 array (UTF-16LE) to a Python string."""
    return bytes(arr).decode("utf-16-le", errors="ignore").rstrip("\x00")


def get_struct_sizes() -> dict[str, int]:
    return {
        "Physics": sizeof(SPageFilePhysics),
        "Graphics": sizeof(SPageFileGraphic),
        "Static": sizeof(SPageFileStatic),
    }
