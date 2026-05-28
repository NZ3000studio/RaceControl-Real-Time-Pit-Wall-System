"""Telemetry data models for Assetto Corsa physics and graphics data.

This module provides Pydantic models to normalize raw AC shared memory data
into typed, validated telemetry containers. All models are JSON serializable
for WebSocket transmission to the frontend.

Models:
  - WheelData: Single wheel telemetry
  - EngineData: Engine parameters
  - PhysicsData: Complete physics frame
  - GraphicsData: Session and lap telemetry
  - StaticData: Car and track metadata
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
    """

    temperature: float = Field(..., description="Tire surface temperature (Celsius)")
    wear: float = Field(..., ge=0, le=100, description="Tire wear percentage (0-100)")
    load: float = Field(..., ge=0, description="Vertical load on tire (kg)")
    slip: float = Field(..., ge=0, le=1, description="Slip ratio (0-1)")
    brake_temperature: float = Field(..., description="Brake temperature (Celsius)")

    @field_validator("temperature", "brake_temperature")
    @classmethod
    def validate_temperature(cls, v):
        """Ensure temperature values are finite."""
        if v != v:  # NaN check
            raise ValueError("Temperature cannot be NaN")
        return v

    @field_validator("load")
    @classmethod
    def validate_load(cls, v):
        """Ensure load is non-negative."""
        if v < 0:
            return 0.0
        return v

    model_config = {"validate_assignment": True}


class EngineData(BaseModel):
    """Engine telemetry and control inputs.

    Attributes:
        rpm: Current engine RPM.
        max_rpm: Maximum engine RPM (red line).
        throttle: Throttle input percentage (0-1).
        brake: Brake input percentage (0-1).
        clutch: Clutch input percentage (0-1).
    """

    rpm: float = Field(..., ge=0, description="Current engine RPM")
    max_rpm: float = Field(..., ge=0, description="Maximum engine RPM")
    throttle: float = Field(..., ge=0, le=1, description="Throttle input (0-1)")
    brake: float = Field(..., ge=0, le=1, description="Brake input (0-1)")
    clutch: float = Field(..., ge=0, le=1, description="Clutch input (0-1)")

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
        velocity_x: Velocity X component in m/s.
        velocity_y: Velocity Y component in m/s.
        velocity_z: Velocity Z component in m/s.
        acceleration_x: Acceleration X component in m/s².
        acceleration_y: Acceleration Y component in m/s².
        acceleration_z: Acceleration Z component in m/s².
        rpm: Engine RPM.
        gear: Current gear (0=reverse, 1=neutral, 2-6=forward).
        throttle: Throttle input (0-1).
        brake: Brake input (0-1).
        handbrake: Handbrake input (0-1).
        steering: Steering input (-1 to 1, negative=left, positive=right).
        fuel: Current fuel in tank in liters.
        max_fuel: Fuel tank capacity in liters.
        wheels: Telemetry for 4 wheels [FL, FR, RL, RR].
        engine: Engine telemetry and control data.
        velocity: Magnitude of velocity vector in m/s.
        g_force: Lateral G-force magnitude.
    """

    speed: float = Field(..., ge=0, description="Forward velocity (m/s)")
    velocity_x: float = Field(..., description="Velocity X component (m/s)")
    velocity_y: float = Field(..., description="Velocity Y component (m/s)")
    velocity_z: float = Field(..., description="Velocity Z component (m/s)")
    acceleration_x: float = Field(..., description="Acceleration X (m/s²)")
    acceleration_y: float = Field(..., description="Acceleration Y (m/s²)")
    acceleration_z: float = Field(..., description="Acceleration Z (m/s²)")
    rpm: float = Field(..., ge=0, description="Engine RPM")
    gear: int = Field(..., ge=-1, le=6, description="Current gear (-1=R, 0=N, 1+=F)")
    throttle: float = Field(..., description="Throttle input (0-1)")
    brake: float = Field(..., description="Brake input (0-1)")
    handbrake: float = Field(..., description="Handbrake input (0-1)")
    steering: float = Field(..., description="Steering input (-1 to 1)")
    fuel: float = Field(..., ge=0, description="Fuel in tank (liters)")
    max_fuel: float = Field(..., ge=0, description="Fuel tank capacity (liters)")
    wheels: List[WheelData] = Field(..., min_length=4, max_length=4, description="Wheel data [FL, FR, RL, RR]")
    engine: EngineData = Field(..., description="Engine telemetry")
    velocity: float = Field(..., ge=0, description="Velocity magnitude (m/s)")
    g_force: float = Field(..., description="Lateral G-force")

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
        return max(0.0, min(1.0, v))

    @field_validator("steering", mode="before")
    @classmethod
    def clamp_steering(cls, v):
        """Clamp steering to -1 to 1 range."""
        return max(-1.0, min(1.0, v))

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
        fuel_estimate_remaining_laps: Estimated remaining laps on current fuel.
        abs: ABS setting (0-1).
        tc: Traction control setting (0-1).
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
    abs: float = Field(..., ge=0, le=1, description="ABS setting (0-1)")
    tc: float = Field(..., ge=0, le=1, description="Traction control setting (0-1)")

    @field_validator("last_sector_time", "lap_time", "fuel_estimate_remaining_laps", mode="before")
    @classmethod
    def validate_non_negative_time(cls, v):
        """Ensure non-negative time values."""
        if v < 0:
            return 0.0
        if v != v:  # NaN check
            raise ValueError("Time value cannot be NaN")
        return v

    @field_validator("abs", "tc", mode="before")
    @classmethod
    def clamp_assists(cls, v):
        """Clamp assist settings to 0-1 range."""
        return max(0.0, min(1.0, v))

    model_config = {"validate_assignment": True}


class StaticData(BaseModel):
    """Static car and track metadata.

    Attributes:
        car_model: Car model identifier/name.
        track_name: Track name/identifier.
        player_name: Driver name.
        air_temp: Ambient air temperature in Celsius.
        road_temp: Road surface temperature in Celsius.
    """

    car_model: str = Field(..., min_length=1, description="Car model name")
    track_name: str = Field(..., min_length=1, description="Track name")
    player_name: str = Field(..., min_length=1, description="Driver name")
    air_temp: float = Field(..., description="Ambient air temperature (Celsius)")
    road_temp: float = Field(..., description="Road temperature (Celsius)")

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
