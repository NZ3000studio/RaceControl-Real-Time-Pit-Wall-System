# Telemetry Pydantic Models - Implementation Summary

## Overview
Successfully implemented comprehensive Pydantic models for the RaceControl telemetry system, providing typed, validated containers for Assetto Corsa physics and session data.

## Files Created

### 1. `backend/app/models/telemetry.py` (275 lines)
Core telemetry data models for physics and graphics data normalization.

**Models Implemented:**
- **WheelData**: Single wheel telemetry (temperature, wear, load, slip, brake_temperature)
- **EngineData**: Engine parameters (rpm, max_rpm, throttle, brake, clutch)
- **PhysicsData**: Complete physics frame (19 typed fields including velocity, acceleration, RPM, fuel, 4x wheels)
- **GraphicsData**: Session/lap telemetry (session type/status, lap info, position, fuel estimate, assists)
- **StaticData**: Car/track metadata (car_model, track_name, player_name, temperatures)
- **NormalizedTelemetry**: Combined frame (physics + graphics + static + timestamp)

**Key Features:**
- Full Pydantic v2 validation with `field_validator` decorators
- Input clamping for control inputs (throttle, brake, steering)
- Constraint validation for bounded fields (wear 0-100%, slip 0-1, assists 0-1)
- JSON serialization for WebSocket transmission
- Complete docstrings for all models and fields
- SI unit compliance (m/s, m/s², Celsius, liters, kilograms)

### 2. `backend/app/models/session.py` (165 lines)
Session state and lifecycle management models.

**Models Implemented:**
- **SessionType** enum: PRACTICE, QUALIFY, RACE, HOTLAP, TIME_ATTACK, DRIFT, UNKNOWN
  - Includes `from_ac_code()` helper to convert AC numeric codes (0-5) to enum values
- **SessionStatus** enum: OFF, REPLAY, LIVE, PAUSED, UNKNOWN
  - Includes `from_ac_code()` helper to convert AC numeric codes (0-3) to enum values
- **SessionState**: Complete session context model
  - 11 typed fields including type, status, lap info, position, fuel, driver/car/track
  - Properties: `fuel_percentage` (computed), `is_connected` (readonly)
  - Full validation and JSON serialization

**Key Features:**
- Enum conversion helpers for seamless AC integration
- Computed properties for derived data (fuel %, connection status)
- Pydantic v2 validation with `validate_assignment=True`
- Complete docstrings including AC code documentation

## Validation Implementation

### Clamping Validators (mode="before")
- **PhysicsData**: Clamps throttle/brake/handbrake to 0-1, steering to -1..1
- **PhysicsData**: Clamps speed/velocity/RPM to ≥0 (prevents negative physics)
- **GraphicsData**: Clamps assist settings (ABS, TC) to 0-1
- **GraphicsData**: Clamps time values to ≥0

### Constraint Validators (Field constraints)
- **WheelData**: wear 0-100%, slip 0-1
- **All models**: Non-negative for speed, RPM, fuel, load, temps
- **All models**: Non-null/non-empty strings where required
- **NaN detection**: Temperature, RPM, fuel validated for NaN values

## Acceptance Criteria - All Met ✓

✓ All 6 telemetry models created (WheelData, EngineData, PhysicsData, GraphicsData, StaticData, NormalizedTelemetry)
✓ All 3 session models created (SessionType, SessionStatus, SessionState)
✓ Full type hints on all fields (verified: WheelData=5, PhysicsData=19, etc.)
✓ Pydantic v2 syntax (BaseModel, field_validator, Field)
✓ Validation for invalid values (constraints + clamping)
✓ All docstrings present (9 models verified)
✓ Models can be imported: `from app.models.telemetry import NormalizedTelemetry`
✓ Models validate correctly with sample data
✓ JSON serializable (model_dump_json, model_validate_json)
✓ No business logic (data containers only)

## Testing Results

### Validation Tests ✓
- Rejects wear > 100%
- Rejects slip > 1.0
- Rejects negative RPM
- Clamps throttle 1.5 → 1.0
- Clamps brake -0.5 → 0.0
- Clamps steering 2.0 → 1.0
- Rejects empty strings

### Integration Tests ✓
- Sample data creates valid models
- JSON round-trip serialization works
- Enum conversion (AC codes to enums) works
- SessionState properties (fuel_percentage, is_connected) work
- 1103-byte JSON payload for realistic telemetry frame

### Existing Tests ✓
- 2 existing tests passed
- 3 async tests skipped (expected, require pytest-asyncio plugin)
- No regression

## Usage Example

```python
from datetime import datetime
from app.models.telemetry import PhysicsData, GraphicsData, StaticData, NormalizedTelemetry
from app.models.session import SessionType, SessionStatus, SessionState

# Create telemetry frame
telemetry = NormalizedTelemetry(
    physics=physics_data,
    graphics=graphics_data,
    static=static_data,
    timestamp=datetime.now(),
)

# Serialize for WebSocket
json_payload = telemetry.model_dump_json()

# Create session state
session = SessionState(
    type=SessionType.from_ac_code(graphics_data.session_type),
    status=SessionStatus.from_ac_code(graphics_data.session_status),
    ...
)

# Use properties
fuel_percentage = session.fuel_percentage  # 0-100
is_connected = session.is_connected       # True if LIVE or REPLAY
```

## Integration Points

These models are designed to work with:
- **AsyncACReader** (backend/app/telemetry/reader.py): Provides raw dict data → validated models
- **WebSocket Manager**: Serializes models → JSON → frontend
- **Session Manager** (Phase 1.4): Tracks session lifecycle using SessionState
- **Async Pipeline** (Phase 1.5): Reader → Models → Session Manager → WebSocket

## Next Steps

Phase 1.4: Implement SessionManager to track session lifecycle  
Phase 1.5: Build async pipeline to use reader + models + session manager  
Phase 2.0: WebSocket server integration for frontend data transmission
