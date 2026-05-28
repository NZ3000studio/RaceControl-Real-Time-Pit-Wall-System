# Telemetry Ingestion Module

Low-level Assetto Corsa shared memory reader with async interface.

## Overview

This module provides a non-blocking async interface to read telemetry from Assetto Corsa's Windows shared memory regions.

**Key features:**
- 100Hz polling (10ms default interval, configurable)
- Full async/await interface (no blocking calls)
- Graceful handling of AC connect/disconnect
- Automatic reconnection on AC restart
- Type hints throughout
- Comprehensive error handling and logging

**Platform:** Windows only (uses Windows named shared memory)

## Files

### `ac_structs.py`

Defines ctypes structures that map to Assetto Corsa's binary shared memory layouts:

- **`PhysicsPacket`** (~25KB)
  - Main physics data structure
  - Contains array of `CarPhysics` (up to 64 cars)
  - Updated at high frequency (~100Hz+)
  - Fields: speed, RPM, gear, throttle, brake, fuel, tire data, temperatures, etc.

- **`CarPhysics`** (~401 bytes per car)
  - Physics data for a single car
  - Wheels stored as arrays: [FL, FR, RL, RR] (Front-Left, Front-Right, Rear-Left, Rear-Right)
  - Includes: speeds, slip, temps, load, wear, pressure, suspension data

- **`GraphicsPacket`** (~360 bytes)
  - Session-level and graphics data
  - Updated moderately (~60Hz)
  - Fields: lap number, position, session status, lap times, fuel remaining, ambient conditions, etc.

- **`StaticPacket`** (~792 bytes)
  - Static information (rarely changes)
  - Fields: car model, track name, player name, session count, track spline length, etc.

### `reader.py`

Implements `AsyncACReader` class:

```python
class AsyncACReader:
    """Read telemetry from Assetto Corsa shared memory.
    
    Non-blocking async interface for polling AC shared memory.
    Handles connection/disconnection gracefully.
    """
    
    async def connect() -> bool:
        """Connect to AC shared memory. Returns True if successful."""
    
    async def is_connected() -> bool:
        """Check current connection state."""
    
    async def read() -> dict | None:
        """Read latest telemetry frame.
        
        Returns dict with 'physics', 'graphics', 'static' keys.
        Returns None if not connected.
        """
    
    async def disconnect() -> None:
        """Clean up resources."""
```

## Usage

### Basic Example

```python
import asyncio
from app.telemetry.reader import AsyncACReader

async def main():
    reader = AsyncACReader()
    
    # Connect to AC
    if not await reader.connect():
        print("AC not running")
        return
    
    # Read telemetry in a loop
    for _ in range(100):
        telemetry = await reader.read()
        if telemetry:
            print(f"Speed: {telemetry['physics']['speed']} m/s")
            print(f"RPM: {telemetry['physics']['rpm']}")
            print(f"Lap: {telemetry['graphics']['lap']}")
        
        await asyncio.sleep(0.01)  # 100Hz polling
    
    await reader.disconnect()

asyncio.run(main())
```

### Integration with FastAPI

```python
# In your FastAPI app
reader = AsyncACReader()

@app.on_event("startup")
async def startup():
    await reader.connect()

@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket):
    await websocket.accept()
    while True:
        telemetry = await reader.read()
        if telemetry:
            await websocket.send_json(telemetry)
        await asyncio.sleep(0.01)  # 100Hz

@app.on_event("shutdown")
async def shutdown():
    await reader.disconnect()
```

## Telemetry Data Structure

### Physics Data (from `read()['physics']`)

```python
{
    'speed': float,              # m/s
    'rpm': float,                # RPM
    'gear': int,                 # 0=R, 1=N, 2-7=forward gears
    'throttle': float,           # 0-1
    'brake': float,              # 0-1
    'clutch': float,             # 0-1
    'fuel': float,               # liters
    'max_fuel': float,           # liters
    'steer': float,              # -1 to 1 (steering input)
    'wheel_speeds': list[float], # [FL, FR, RL, RR] rad/s
    'wheel_temps': list[float],  # [FL, FR, RL, RR] Celsius
    'wheel_wear': list[float],   # [FL, FR, RL, RR] 0-1 (1=new)
    'brake_temps': list[float],  # [FL, FR, RL, RR] Kelvin
    'engine_temp': float,        # Celsius
    'road_temp': float,          # Celsius
    'turbo_boost': float,        # PSI
    # ... and many more fields
}
```

### Graphics Data (from `read()['graphics']`)

```python
{
    'status': int,               # 0=off, 1=replay, 2=live, 3=paused
    'session': int,              # 0=practice, 1=qualify, 2=race, etc
    'lap': int,                  # current lap number
    'position': int,             # grid/race position
    'fuel_remaining': float,     # estimated laps
    'current_time': str,         # HH:MM:SS.mmm
    'best_time': str,            # HH:MM:SS.mmm
    'session_time_left': float,  # seconds
    'ambient_temp': float,       # Celsius
    'rain_tires': bool,          # rain tires equipped
    'drs_available': bool,       # DRS available (if applicable)
    # ... and more
}
```

### Static Data (from `read()['static']`)

```python
{
    'car_model': str,            # e.g., "ferrari_sf90"
    'track': str,                # e.g., "monza"
    'player_name': str,          # driver name
    'player_nick': str,          # driver nickname
    'number_of_cars': int,       # cars in session
    'sector_count': int,         # track sectors
    # ... and more
}
```

## Polling Strategy

The reader uses asynchronous polling with configurable interval:

```python
reader = AsyncACReader(poll_interval=0.01)  # 100Hz (10ms)
```

**Non-blocking:** Uses `asyncio.sleep()`, not `time.sleep()`, so it can coexist with other async tasks.

**Graceful degradation:** If AC disconnects, `read()` returns `None` and waits for reconnection.

**No spin-waiting:** Respects the configured poll interval to avoid CPU waste.

## Error Handling

The reader is designed to be robust:

- **AC not running:** `connect()` returns False, `read()` returns None
- **AC crashes during session:** `read()` returns None, automatically waits for reconnection
- **Corrupted memory:** Caught and logged, returns None for that frame
- **Permission errors:** Handled gracefully with debug logging

Example error-safe usage:

```python
reader = AsyncACReader()

while True:
    # Attempt connection
    if not await reader.is_connected():
        await reader.connect()  # Retries on failure
        continue
    
    # Read telemetry
    telemetry = await reader.read()
    if telemetry:
        process_telemetry(telemetry)
    
    await asyncio.sleep(0.01)
```

## Struct Layout Notes

### Finding/Updating Struct Offsets

If Assetto Corsa updates its struct layout:

1. **Research sources:**
   - AC modding forums: https://www.assettocorsa.net/forum/
   - Community telemetry docs
   - Reverse-engineer from AC executable or modding tools

2. **Validate changes:**
   - Run with AC connected and verify reasonable values
   - Check specific fields (e.g., RPM should be 0-8000, speed 0-300+)

3. **Update process:**
   - Modify `_fields_` in appropriate struct
   - Verify struct size with `get_struct_sizes()`
   - Test against running AC instance

### Memory Layout Rules

- **`_pack_ = 1`**: Ensures no padding between fields (matches AC's binary layout)
- **Byte order**: Little-endian (standard on Windows, ctypes handles automatically)
- **Arrays**: Wheels always [FL, FR, RL, RR] (Front-Left, Front-Right, Rear-Left, Rear-Right)
- **Car arrays**: In `PhysicsPacket`, use `focusedCarIndex` to get player car

## Testing

### Without AC Running

```bash
# Should fail gracefully
python -c "
import asyncio
from app.telemetry.reader import AsyncACReader

async def test():
    reader = AsyncACReader()
    connected = await reader.connect()
    print(f'Connected: {connected}')  # Should be False
    data = await reader.read()
    print(f'Data: {data}')  # Should be None

asyncio.run(test())
"
```

### With AC Running (on Windows)

```python
# Should succeed and show live telemetry
import asyncio
from app.telemetry.reader import AsyncACReader

async def test():
    reader = AsyncACReader()
    if await reader.connect():
        telemetry = await reader.read()
        print(f"Speed: {telemetry['physics']['speed']} m/s")
        print(f"Lap: {telemetry['graphics']['lap']}")
    await reader.disconnect()

asyncio.run(test())
```

## Performance Characteristics

- **Memory usage:** ~40KB for reader instance + mapped shared memory (~35KB)
- **CPU usage:** Minimal at 100Hz polling (~1% on modern CPU)
- **Latency:** <10ms from AC update to application read
- **Polling jitter:** Depends on system load, typically <1ms

## Limitations

1. **Windows only** - Uses Windows named shared memory API
2. **Single instance** - Reader reads player car only (via `focusedCarIndex`)
3. **No multiplayer telemetry** - Only reads local player data
4. **Shared memory corruption** - If AC or Windows are unstable, shared memory can become corrupted

## Architecture Alignment

This module is the **critical path** for telemetry ingestion:

```
Assetto Corsa
    ↓
[Windows Shared Memory]
    ↓
[AsyncACReader] ← you are here
    ↓
Telemetry Normalization (next phase)
    ↓
Processing Pipeline
    ↓
WebSocket Broadcast
```

## Future Enhancements

Not in MVP scope but noted for later:

- [ ] Multi-car telemetry support
- [ ] AC version detection and auto-struct-validation
- [ ] Memory-mapped file caching
- [ ] Telemetry recording/replay
- [ ] Linux/Mac support via alternative APIs

---

**References:**
- Assetto Corsa Forums: https://www.assettocorsa.net/forum/
- AC Modding Documentation
- Community-maintained struct documentation (search "AC telemetry struct")
