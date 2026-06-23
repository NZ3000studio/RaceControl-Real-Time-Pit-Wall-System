"""Telemetry data models for Assetto Corsa physics and graphics data.

This module provides Pydantic models to normalize raw AC shared memory data
into typed, validated telemetry containers. All models are JSON serializable
for WebSocket transmission to the frontend.

Models:
  - WheelData: Single wheel telemetry (temps, wear, forces, brakes)
  - EngineData: Engine parameters + ERS/KERS
  - PhysicsData: Complete physics frame + orientation + damage
  - GraphicsData: Session and lap telemetry + delta + penalties
  - StaticData: Car and track metadata + pit window + specs
  - NormalizedTelemetry: Combined frame (physics + graphics + static)

Units:
  - Speed/velocity: m/s
  - Acceleration: m/s²
  - Temperature: Celsius
  - Fuel: liters
  - Load: kilograms
  - Time: seconds
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, field_validator


class WheelData(BaseModel):
    """Telemetry data for a single wheel/tire.

    Attributes:
        temperature: Tire surface temperature in Celsius.
        wear: Tire wear percentage (0-100).
        load: Vertical load on tire in kilograms.
        slip: Slip ratio (0-1), where 0=no slip, 1=full lockup/wheel spin.
        brake_temperature: Brake temperature in Celsius.
        pressure: Tire pressure in PSI.
        tire_core_temp: Tire core temperature in Celsius.
        temp_inner: Tire inner layer temperature (Celsius).
        temp_middle: Tire middle layer temperature (Celsius).
        temp_outer: Tire outer layer temperature (Celsius).
        brake_pressure: Brake line pressure at this wheel.
        pad_life: Brake pad remaining (0-100%).
        disc_life: Brake disc remaining (0-100%).
        tyre_force_x: Longitudinal tire force (N).
        tyre_force_y: Lateral tire force (N).
        self_aligning_torque: Self-aligning torque (Nm).
    """

    temperature: float = Field(..., description="Tire surface temperature (Celsius)")
    wear: float = Field(..., ge=0, le=100, description="Tire wear percentage (0-100)")
    load: float = Field(..., ge=0, description="Vertical load on tire (kg)")
    slip: float = Field(..., ge=0, le=1, description="Slip ratio (0-1)")
    brake_temperature: float = Field(..., description="Brake temperature (Celsius)")
    pressure: float = Field(default=0.0, ge=0, description="Tire pressure (PSI)")
    tire_core_temp: float = Field(default=0.0, description="Tire core temperature (Celsius)")
    temp_inner: float = Field(default=0.0, description="Inner layer temp (Celsius)")
    temp_middle: float = Field(default=0.0, description="Middle layer temp (Celsius)")
    temp_outer: float = Field(default=0.0, description="Outer layer temp (Celsius)")
    brake_pressure: float = Field(default=0.0, ge=0, description="Brake line pressure")
    pad_life: float = Field(default=0.0, ge=0, le=100, description="Brake pad remaining %")
    disc_life: float = Field(default=0.0, ge=0, le=100, description="Brake disc remaining %")
    tyre_force_x: float = Field(default=0.0, description="Longitudinal tire force (N)")
    tyre_force_y: float = Field(default=0.0, description="Lateral tire force (N)")
    self_aligning_torque: float = Field(default=0.0, description="Self-aligning torque (Nm)")

    @field_validator(
        "temperature", "brake_temperature", "tire_core_temp",
        "temp_inner", "temp_middle", "temp_outer",
    )
    @classmethod
    def validate_temperature(cls, v):
        """Ensure temperature values are finite."""
        if v != v:  # NaN check
            raise ValueError("Temperature cannot be NaN")
        return v

    @field_validator("load", "pressure", "brake_pressure", "pad_life", "disc_life")
    @classmethod
    def validate_non_negative(cls, v):
        """Ensure non-negative values."""
        if v < 0:
            return 0.0
        return v

    model_config = {"validate_assignment": True}


class EngineData(BaseModel):
    """Engine telemetry, control inputs, and ERS/KERS state.

    Attributes:
        rpm: Current engine RPM.
        max_rpm: Maximum engine RPM (red line).
        throttle: Throttle input percentage (0-1).
        brake: Brake input percentage (0-1).
        clutch: Clutch input percentage (0-1).
        kers_charge: KERS charge level.
        kers_current_kj: KERS energy in kJ.
        ers_power_level: ERS power delivery setting.
        ers_recovery_level: ERS recovery setting.
        ers_is_charging: ERS is actively charging.
    """

    rpm: float = Field(..., ge=0, description="Current engine RPM")
    max_rpm: float = Field(..., ge=0, description="Maximum engine RPM")
    throttle: float = Field(..., ge=0, le=1, description="Throttle input (0-1)")
    brake: float = Field(..., ge=0, le=1, description="Brake input (0-1)")
    clutch: float = Field(..., ge=0, le=1, description="Clutch input (0-1)")
    kers_charge: float = Field(default=0.0, ge=0, description="KERS charge level")
    kers_current_kj: float = Field(default=0.0, ge=0, description="KERS energy (kJ)")
    ers_power_level: int = Field(default=0, ge=0, description="ERS power level")
    ers_recovery_level: int = Field(default=0, ge=0, description="ERS recovery level")
    ers_is_charging: bool = Field(default=False, description="ERS is charging")

    @field_validator("rpm", "max_rpm")
    @classmethod
    def validate_rpm(cls, v):
        """Ensure RPM values are non-negative and finite."""
        if v < 0:
            return 0.0
        if v != v:  # NaN check
            raise ValueError("RPM cannot be NaN")
        return v

    model_config = {"validate_assignment": True}


class PhysicsData(BaseModel):
    """Complete physics frame from Assetto Corsa.

    All values in SI units (meters, seconds, kilograms, Celsius) except
    where noted. Represents the current state of vehicle physics.

    Attributes:
        speed: Forward velocity magnitude in m/s.
        velocity_x/y/z: Velocity components in m/s.
        acceleration_x/y/z: Acceleration components in m/s².
        rpm: Engine RPM.
        gear: Current gear (0=reverse, 1=neutral, 2-6=forward).
        throttle: Throttle input (0-1).
        brake: Brake input (0-1).
        handbrake: Handbrake input (0-1).
        steering: Steering input (-1 to 1, negative=left, positive=right).
        fuel: Current fuel in tank in liters.
        max_fuel: Fuel tank capacity in liters.
        wheels: Telemetry for 4 wheels [FL, FR, RL, RR].
        engine: Engine telemetry + ERS/KERS.
        velocity: Magnitude of velocity vector in m/s.
        g_force: Total G-force magnitude.
        heading: Car heading/yaw in radians.
        pitch: Car pitch in radians.
        roll: Car roll in radians.
        car_damage: 5-zone damage [body, engine, aero, susp_f, susp_r] (0-100%).
        suspension_damage: Per-corner suspension damage (0-100%).
        brake_bias: Front/rear brake bias.
    """

    speed: float = Field(..., ge=0, description="Forward velocity (m/s)")
    velocity_x: float = Field(..., description="Velocity X component (m/s)")
    velocity_y: float = Field(..., description="Velocity Y component (m/s)")
    velocity_z: float = Field(..., description="Velocity Z component (m/s)")
    acceleration_x: float = Field(..., description="Acceleration X (m/s²)")
    acceleration_y: float = Field(..., description="Acceleration Y (m/s²)")
    acceleration_z: float = Field(..., description="Acceleration Z (m/s²)")
    rpm: float = Field(..., ge=0, description="Engine RPM")
    gear: int = Field(..., ge=-1, le=7, description="Current gear (-1=R, 0=N, 1+=F)")
    throttle: float = Field(..., description="Throttle input (0-1)")
    brake: float = Field(..., description="Brake input (0-1)")
    handbrake: float = Field(..., description="Handbrake input (0-1)")
    steering: float = Field(..., description="Steering input (-1 to 1)")
    fuel: float = Field(..., ge=0, description="Fuel in tank (liters)")
    max_fuel: float = Field(..., ge=0, description="Fuel tank capacity (liters)")
    wheels: List[WheelData] = Field(..., min_length=4, max_length=4, description="Wheel data [FL, FR, RL, RR]")
    engine: EngineData = Field(..., description="Engine + ERS/KERS telemetry")
    velocity: float = Field(..., ge=0, description="Velocity magnitude (m/s)")
    g_force: float = Field(..., description="Total G-force")
    heading: float = Field(default=0.0, description="Car heading/yaw (rad)")
    pitch: float = Field(default=0.0, description="Car pitch (rad)")
    roll: float = Field(default=0.0, description="Car roll (rad)")
    car_damage: List[float] = Field(default_factory=lambda: [0,0,0,0,0], description="5-zone damage")
    suspension_damage: List[float] = Field(default_factory=lambda: [0,0,0,0], description="Per-corner suspension damage")
    brake_bias: float = Field(default=0.0, description="Brake bias")

    @field_validator("speed", "velocity_x", "velocity_y", "velocity_z", "velocity", "rpm", mode="before")
    @classmethod
    def validate_non_negative_numeric(cls, v):
        """Ensure non-negative values and clamp to 0 if negative."""
        if v < 0:
            return 0.0
        if v != v:  # NaN check
            raise ValueError("Value cannot be NaN")
        return v

    @field_validator("fuel", mode="before")
    @classmethod
    def validate_fuel(cls, v):
        """Ensure fuel is non-negative."""
        if v < 0:
            return 0.0
        if v != v:  # NaN check
            raise ValueError("Fuel cannot be NaN")
        return v

    @field_validator("throttle", "brake", "handbrake", mode="before")
    @classmethod
    def clamp_01_inputs(cls, v):
        """Clamp input values to valid 0-1 range."""
        return max(0.0, min(1.0, float(v)))

    @field_validator("steering", mode="before")
    @classmethod
    def clamp_steering(cls, v):
        """Clamp steering to -1 to 1 range."""
        return max(-1.0, min(1.0, float(v)))

    model_config = {"validate_assignment": True}


class GraphicsData(BaseModel):
    """Session and lap telemetry from graphics packet.

    Attributes:
        session_type: Type of session (0=practice, 1=qualify, 2=race, 3=hotlap, 4=time attack, 5=drift).
        session_status: Current session status (0=off, 1=replay, 2=live, 3=paused).
        completed_laps: Total number of completed laps.
        current_lap: Current lap number (1-based).
        current_sector: Current sector (0, 1, or 2).
        last_sector_time: Time of last completed sector in seconds.
        lap_time: Time of current lap in seconds.
        position: Grid/race position (1-based).
        num_cars: Total number of cars in session.
        fuel_estimate_remaining_laps: Estimated remaining laps on fuel.
        abs: ABS setting level.
        tc: Traction control setting level.
        track_grip_level: Track surface grip (0-1).
        drs_available: DRS is available.
        drs_engaged: DRS is currently open.
        tc_in_action: TC actively intervening.
        abs_in_action: ABS actively intervening.
        rain_lights: Rain lights on.
        rain_tires: Rain tires equipped.
        wind_speed: Wind speed (m/s).
        wind_direction: Wind direction (degrees).
        flag: Track flag (0=green, 1=yellow, 2=blue, 3=white, 4=checkered).
        pit_limiter: Pit limiter engaged.
        tyre_compound: Tire compound name.
        delta_lap_time: Delta to best lap in milliseconds.
        is_delta_positive: Delta is positive (losing time).
        fuel_used_per_lap: Fuel consumption per lap (liters).
        penalty_time: Active penalty time in seconds.
        penalty: Penalty type (0=none).
        stint_time_left: Driver stint time remaining (seconds).
        number_of_laps: Total laps in session.
        tc_cut: TC cut level.
        clock: Session clock time (seconds).
        mandatory_pit_done: Mandatory pit stop completed.
    """

    session_type: int = Field(..., ge=0, le=5, description="Session type (0-5)")
    session_status: int = Field(..., ge=0, le=3, description="Session status (0-3)")
    completed_laps: int = Field(..., ge=0, description="Total completed laps")
    current_lap: int = Field(..., ge=1, description="Current lap number (1-based)")
    current_sector: int = Field(..., ge=0, le=2, description="Current sector (0-2)")
    last_sector_time: float = Field(..., ge=0, description="Last sector time (seconds)")
    lap_time: float = Field(..., ge=0, description="Current lap time (seconds)")
    position: int = Field(..., ge=1, description="Position in race (1-based)")
    num_cars: int = Field(..., ge=1, description="Total cars in session")
    fuel_estimate_remaining_laps: float = Field(..., ge=0, description="Estimated remaining laps on fuel")
    abs: float = Field(..., ge=0, le=1, description="ABS setting level")
    tc: float = Field(..., ge=0, le=1, description="Traction control setting level")
    track_grip_level: float = Field(default=1.0, ge=0, le=1, description="Track surface grip (0-1)")
    drs_available: bool = Field(default=False, description="DRS is available")
    drs_engaged: bool = Field(default=False, description="DRS is engaged")
    tc_in_action: bool = Field(default=False, description="TC actively intervening")
    abs_in_action: bool = Field(default=False, description="ABS actively intervening")
    rain_lights: bool = Field(default=False, description="Rain lights on")
    rain_tires: bool = Field(default=False, description="Rain tires equipped")
    wind_speed: float = Field(default=0.0, ge=0, description="Wind speed (m/s)")
    wind_direction: float = Field(default=0.0, description="Wind direction (degrees)")
    flag: int = Field(default=0, ge=0, le=4, description="Track flag")
    pit_limiter: bool = Field(default=False, description="Pit limiter engaged")
    tyre_compound: str = Field(default="", description="Tire compound name")
    delta_lap_time: int = Field(default=0, description="Delta to best lap (ms)")
    is_delta_positive: bool = Field(default=False, description="Delta is positive (slower)")
    fuel_used_per_lap: float = Field(default=0.0, ge=0, description="Fuel used per lap (L)")
    penalty_time: float = Field(default=0.0, ge=0, description="Penalty time (seconds)")
    penalty: int = Field(default=0, ge=0, description="Penalty type")
    stint_time_left: int = Field(default=0, ge=0, description="Stint time remaining (s)")
    number_of_laps: int = Field(default=0, ge=0, description="Total session laps")
    tc_cut: int = Field(default=0, ge=0, description="TC cut level")
    clock: float = Field(default=0.0, ge=0, description="Session clock (s)")
    mandatory_pit_done: bool = Field(default=False, description="Mandatory pit completed")

    @field_validator("last_sector_time", "lap_time", "fuel_estimate_remaining_laps", mode="before")
    @classmethod
    def validate_non_negative_time(cls, v):
        """Ensure non-negative time values."""
        if v < 0:
            return 0.0
        if v != v:  # NaN check
            raise ValueError("Time value cannot be NaN")
        return v

    @field_validator("abs", "tc", "track_grip_level", mode="before")
    @classmethod
    def clamp_assists(cls, v):
        """Clamp assist/surface settings to 0-1 range."""
        return max(0.0, min(1.0, float(v)))

    model_config = {"validate_assignment": True}


class StaticData(BaseModel):
    """Static car and track metadata.

    Attributes:
        car_model: Car model identifier/name.
        track_name: Track name/identifier.
        player_name: Driver name.
        air_temp: Ambient air temperature in Celsius.
        road_temp: Road surface temperature in Celsius.
        pit_window_start: Pit window start lap.
        pit_window_end: Pit window end lap.
        max_power: Engine max power.
        max_torque: Engine max torque.
        kers_max_j: KERS max energy (J).
        ers_max_j: ERS max energy (J).
        is_timed_race: Session is time-limited.
    """

    car_model: str = Field(..., min_length=1, description="Car model name")
    track_name: str = Field(..., min_length=1, description="Track name")
    player_name: str = Field(..., min_length=1, description="Driver name")
    air_temp: float = Field(..., description="Ambient air temperature (Celsius)")
    road_temp: float = Field(..., description="Road temperature (Celsius)")
    pit_window_start: int = Field(default=0, ge=0, description="Pit window start lap")
    pit_window_end: int = Field(default=0, ge=0, description="Pit window end lap")
    max_power: float = Field(default=0.0, ge=0, description="Engine max power")
    max_torque: float = Field(default=0.0, ge=0, description="Engine max torque")
    kers_max_j: float = Field(default=0.0, ge=0, description="KERS max energy (J)")
    ers_max_j: float = Field(default=0.0, ge=0, description="ERS max energy (J)")
    is_timed_race: bool = Field(default=False, description="Timed race flag")

    @field_validator("air_temp", "road_temp")
    @classmethod
    def validate_temperature(cls, v):
        """Ensure temperature values are finite."""
        if v != v:  # NaN check
            raise ValueError("Temperature cannot be NaN")
        return v

    model_config = {"validate_assignment": True}


class NormalizedTelemetry(BaseModel):
    """Complete normalized telemetry frame.

    Combines physics, graphics, and static data into a single container
    for transmission to frontend via WebSocket.

    Attributes:
        physics: Physics data frame.
        graphics: Graphics/session data frame.
        static: Static car/track metadata.
        timestamp: Server timestamp when telemetry was processed (ISO format).
    """

    physics: PhysicsData = Field(..., description="Physics data")
    graphics: GraphicsData = Field(..., description="Graphics/session data")
    static: StaticData = Field(..., description="Static car/track data")
    timestamp: datetime = Field(..., description="Server timestamp (ISO format)")

    model_config = {"validate_assignment": True}
