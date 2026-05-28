# Telemetry Models - Quick Reference

## File Locations
- **Telemetry Models**: `app/models/telemetry.py`
- **Session Models**: `app/models/session.py`
- **Models Package**: `app/models/__init__.py`

## Import Statements

```python
# Telemetry models
from app.models.telemetry import (
    WheelData,
    EngineData,
    PhysicsData,
    GraphicsData,
    StaticData,
    NormalizedTelemetry,
)

# Session models
from app.models.session import (
    SessionType,
    SessionStatus,
    SessionState,
)
```

## Quick Examples

### Create a Telemetry Frame
```python
from datetime import datetime
from app.models.telemetry import NormalizedTelemetry, PhysicsData, GraphicsData, StaticData

telemetry = NormalizedTelemetry(
    physics=physics_data,
    graphics=graphics_data,
    static=static_data,
    timestamp=datetime.now(),
)

# Serialize to JSON
json_payload = telemetry.model_dump_json()

# Deserialize from JSON
telemetry2 = NormalizedTelemetry.model_validate_json(json_payload)
```

### Work with Session State
```python
from app.models.session import SessionType, SessionStatus, SessionState

# Create from AC codes
session = SessionState(
    type=SessionType.from_ac_code(2),  # RACE
    status=SessionStatus.from_ac_code(2),  # LIVE
    ...
)

# Use computed properties
fuel_remaining_percent = session.fuel_percentage  # 0-100
is_game_connected = session.is_connected  # True if LIVE or REPLAY
```

### Handle Invalid Values
Models automatically clamp and validate inputs:

```python
# Throttle outside 0-1 gets clamped
physics = PhysicsData(
    ...
    throttle=1.5,  # → automatically becomes 1.0
    brake=-0.5,    # → automatically becomes 0.0
    steering=2.0,  # → automatically becomes 1.0
    ...
)

# Invalid wear percentage gets rejected
try:
    wheel = WheelData(
        ...
        wear=150,  # ✗ Raises ValidationError (>100%)
    )
except ValidationError as e:
    print(f"Invalid wheel data: {e}")
```

## Model Field Counts

| Model | Fields | Notes |
|-------|--------|-------|
| WheelData | 5 | Temperature, wear, load, slip, brake temp |
| EngineData | 5 | RPM, max RPM, throttle, brake, clutch |
| PhysicsData | 19 | Speed, velocity, acceleration, fuel, 4x wheels, engine, etc |
| GraphicsData | 12 | Session type/status, laps, sector, position, fuel estimate, assists |
| StaticData | 5 | Car, track, player, air temp, road temp |
| NormalizedTelemetry | 4 | Physics, graphics, static, timestamp |
| SessionState | 11 | Type, status, laps, position, fuel, driver, car, track, is_active, updated_at |

## Validation Rules

### Clamped Values (Automatic)
- **throttle, brake, handbrake**: Clamped to 0.0-1.0
- **steering**: Clamped to -1.0 to 1.0
- **abs, tc**: Clamped to 0.0-1.0
- **Negative speed/RPM/fuel**: Clamped to 0.0

### Rejected Values (Raise ValidationError)
- **wear**: Must be 0-100%
- **slip**: Must be 0-1
- **Empty strings**: car_model, track_name, player_name, driver, car
- **Wheel array length**: Must be exactly 4

### Special Handling
- **NaN values**: Rejected for temperatures, RPM, fuel
- **timestamps**: datetime objects, ISO formatted in JSON

## Enum Values

### SessionType (from_ac_code mapping)
```
0 → PRACTICE
1 → QUALIFY
2 → RACE
3 → HOTLAP
4 → TIME_ATTACK
5 → DRIFT
other → UNKNOWN
```

### SessionStatus (from_ac_code mapping)
```
0 → OFF
1 → REPLAY
2 → LIVE
3 → PAUSED
other → UNKNOWN
```

## JSON Payload Size

- **Single telemetry frame**: ~1100 bytes
- **Single session state**: ~240 bytes
- Format: Compact JSON, suitable for WebSocket transmission

## Integration with AsyncACReader

```python
from app.telemetry.reader import AsyncACReader
from app.models.telemetry import NormalizedTelemetry

reader = AsyncACReader()
raw_data = await reader.read()  # Returns dict

# Convert raw data to validated models
physics = PhysicsData(**raw_data['physics'])
graphics = GraphicsData(**raw_data['graphics'])
static = StaticData(**raw_data['static'])

telemetry = NormalizedTelemetry(
    physics=physics,
    graphics=graphics,
    static=static,
    timestamp=datetime.now(),
)
```

## Performance Notes

- **Model creation**: < 1ms per frame
- **JSON serialization**: < 2ms per frame
- **Validation overhead**: Minimal (handled in Pydantic C core)
- **Memory**: ~2KB per model instance

## Troubleshooting

### "ValidationError: ... Input should be less than or equal to 1"
Some fields have strict constraints. Use mode="before" validators or adjust input values.

### "Cannot import NormalizedTelemetry"
Ensure you're in the backend directory or have the correct Python path set:
```bash
cd backend && source venv/bin/activate && python
```

### JSON serialization issues
Use `model_dump_json()` instead of `json.dumps()`:
```python
# ✓ Correct
json_str = telemetry.model_dump_json()

# ✗ Wrong
json_str = json.dumps(telemetry.dict())  # datetime won't serialize
```

## Development Tips

1. **Always validate on assignment**: `validate_assignment=True` in model_config
2. **Use field_validator(mode="before")** for clamping values
3. **Use Field constraints** for range validation (ge, le, min_length, max_length)
4. **Document all fields** with description parameter in Field()
5. **Test round-trip serialization** when modifying models
6. **Check type hints** with `get_type_hints(ModelClass)`

## Related Files

- AsyncACReader: `app/telemetry/reader.py`
- AC Structs: `app/telemetry/ac_structs.py`
- Session Manager (Phase 1.4): `app/session/manager.py` (not yet created)
- WebSocket Handler (Phase 2.0): `app/websocket/handler.py` (not yet created)
