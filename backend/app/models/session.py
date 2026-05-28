"""Session state and lifecycle models.

This module provides Pydantic models for tracking session state across
the telemetry lifecycle, including session type, status, and current
driver/car/track information.

Models:
  - SessionType: Enum for AC session types
  - SessionStatus: Enum for session state
  - SessionState: Current session state container
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SessionType(str, Enum):
    """Assetto Corsa session type enumeration.

    Attributes:
        PRACTICE: Free practice session.
        QUALIFY: Qualifying session.
        RACE: Race session.
        HOTLAP: Single hotlap mode.
        TIME_ATTACK: Time attack mode.
        DRIFT: Drift competition.
        UNKNOWN: Session type not recognized.
    """

    PRACTICE = "practice"
    QUALIFY = "qualify"
    RACE = "race"
    HOTLAP = "hotlap"
    TIME_ATTACK = "time_attack"
    DRIFT = "drift"
    UNKNOWN = "unknown"

    @classmethod
    def from_ac_code(cls, code: int) -> "SessionType":
        """Convert AC numeric session type to enum.

        AC session type codes:
            0: Practice
            1: Qualifying
            2: Race
            3: Hotlap
            4: Time attack
            5: Drift

        Args:
            code: Numeric session type from AC graphics packet.

        Returns:
            Corresponding SessionType enum value.
        """
        mapping = {
            0: cls.PRACTICE,
            1: cls.QUALIFY,
            2: cls.RACE,
            3: cls.HOTLAP,
            4: cls.TIME_ATTACK,
            5: cls.DRIFT,
        }
        return mapping.get(code, cls.UNKNOWN)


class SessionStatus(str, Enum):
    """Assetto Corsa session status enumeration.

    Attributes:
        OFF: Session not running.
        REPLAY: Replay mode.
        LIVE: Live session in progress.
        PAUSED: Session paused.
        UNKNOWN: Status not recognized.
    """

    OFF = "off"
    REPLAY = "replay"
    LIVE = "live"
    PAUSED = "paused"
    UNKNOWN = "unknown"

    @classmethod
    def from_ac_code(cls, code: int) -> "SessionStatus":
        """Convert AC numeric session status to enum.

        AC session status codes:
            0: Off
            1: Replay
            2: Live
            3: Paused

        Args:
            code: Numeric session status from AC graphics packet.

        Returns:
            Corresponding SessionStatus enum value.
        """
        mapping = {
            0: cls.OFF,
            1: cls.REPLAY,
            2: cls.LIVE,
            3: cls.PAUSED,
        }
        return mapping.get(code, cls.UNKNOWN)


class SessionState(BaseModel):
    """Current session state and metadata.

    Represents the complete session context including session type,
    status, lap information, driver/car/track info, and fuel state.

    Attributes:
        type: Session type (practice, qualify, race, etc).
        status: Current session status (off, live, paused, replay).
        lap_count: Current lap number (1-based).
        completed_laps: Total number of completed laps.
        position: Current position/place (1-based).
        fuel_remaining: Current fuel in tank in liters.
        fuel_capacity: Maximum fuel tank capacity in liters.
        driver: Driver name.
        car: Car model.
        track: Track name.
        is_active: True if session is currently running (live, not paused/off).
        updated_at: Timestamp of last update.
    """

    type: SessionType = Field(..., description="Session type")
    status: SessionStatus = Field(..., description="Session status")
    lap_count: int = Field(..., ge=1, description="Current lap number (1-based)")
    completed_laps: int = Field(..., ge=0, description="Total completed laps")
    position: int = Field(..., ge=1, description="Current position (1-based)")
    fuel_remaining: float = Field(..., ge=0, description="Fuel in tank (liters)")
    fuel_capacity: float = Field(..., ge=0, description="Fuel tank capacity (liters)")
    driver: str = Field(..., min_length=1, description="Driver name")
    car: str = Field(..., min_length=1, description="Car model")
    track: str = Field(..., min_length=1, description="Track name")
    is_active: bool = Field(..., description="True if session running (not paused/off)")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @property
    def fuel_percentage(self) -> float:
        """Calculate current fuel as percentage of tank capacity.

        Returns:
            Fuel percentage (0-100). Returns 0 if tank capacity is 0.
        """
        if self.fuel_capacity <= 0:
            return 0.0
        return (self.fuel_remaining / self.fuel_capacity) * 100.0

    @property
    def is_connected(self) -> bool:
        """Check if session is actively connected to game.

        Returns:
            True if status is LIVE or REPLAY (not OFF or PAUSED).
        """
        return self.status in (SessionStatus.LIVE, SessionStatus.REPLAY)

    model_config = {"validate_assignment": True}
