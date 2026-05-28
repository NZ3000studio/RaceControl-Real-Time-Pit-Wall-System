"""Session state manager for tracking Assetto Corsa session lifecycle.

Tracks session type, status, lap changes, and provides state transitions.
"""

import logging
from typing import Optional

from app.models.session import SessionState, SessionStatus, SessionType

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages session lifecycle and state transitions."""

    def __init__(self) -> None:
        """Initialize session manager."""
        self._current_state: Optional[SessionState] = None
        self._last_lap: int = 0
        self._session_started: bool = False

    def update(
        self,
        session_type: int,
        session_status: int,
        lap: int,
        completed_laps: int,
        position: int,
        fuel: float,
        max_fuel: float,
        driver: str,
        car: str,
        track: str,
    ) -> Optional[SessionState]:
        """Update session state from telemetry data.

        Args:
            session_type: AC session type code (0-5)
            session_status: AC session status code (0-3)
            lap: Current lap number
            completed_laps: Total completed laps
            position: Current grid position
            fuel: Current fuel in liters
            max_fuel: Fuel tank capacity in liters
            driver: Driver name
            car: Car model
            track: Track name

        Returns:
            Updated SessionState, or None if no state yet
        """
        from datetime import datetime

        session_type_enum = SessionType.from_ac_code(session_type)
        session_status_enum = SessionStatus.from_ac_code(session_status)

        # Detect session start
        if session_status_enum == SessionStatus.OFF and not self._session_started:
            return None

        if session_status_enum == SessionStatus.LIVE and not self._session_started:
            self._session_started = True
            logger.info(f"Session started: {session_type_enum} on {track}")

        # Detect lap change
        if lap > self._last_lap:
            logger.info(f"Lap change: {self._last_lap} → {lap}")
            self._last_lap = lap

        # Detect session end
        if session_status_enum == SessionStatus.OFF and self._session_started:
            self._session_started = False
            logger.info("Session ended")
            self._reset()
            return None

        # Create/update state
        self._current_state = SessionState(
            type=session_type_enum,
            status=session_status_enum,
            lap_count=lap,
            completed_laps=completed_laps,
            position=position,
            fuel_remaining=fuel,
            fuel_capacity=max_fuel,
            driver=driver,
            car=car,
            track=track,
            is_active=session_status_enum in (SessionStatus.LIVE, SessionStatus.REPLAY),
            updated_at=datetime.now(),
        )

        return self._current_state

    def get_state(self) -> Optional[SessionState]:
        """Get current session state.

        Returns:
            Current SessionState, or None if no active session
        """
        return self._current_state

    def is_active(self) -> bool:
        """Check if session is active.

        Returns:
            True if session running (live or replay), False otherwise
        """
        return self._current_state is not None and self._current_state.is_active

    def reset(self) -> None:
        """Reset session state."""
        self._reset()

    def _reset(self) -> None:
        """Internal reset."""
        self._current_state = None
        self._last_lap = 0
        self._session_started = False
