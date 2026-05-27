# RaceControl Backend

Real-time telemetry ingestion and WebSocket streaming for Assetto Corsa.

## Architecture

```
Assetto Corsa (Shared Memory)
    ↓
Telemetry Reader (mmap + ctypes)
    ↓
Normalization & Models (Pydantic)
    ↓
Session State Manager
    ↓
WebSocket Broadcaster
    ↓
Frontend Clients
```

## Quick Start

### Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

Server runs on `http://127.0.0.1:8000`

- `/health` - Health check
- `/ws/telemetry` - WebSocket telemetry stream (when implemented)

## Project Structure

```
backend/
├── main.py                 # FastAPI entry point
├── config.py              # Configuration (host, port, log level)
├── requirements.txt       # Python dependencies
└── app/
    ├── telemetry/         # Shared memory reading
    │   ├── reader.py      # AC shared memory interface
    │   ├── ac_structs.py  # Physics/graphics/static struct defs
    │   └── pipeline.py    # Read → normalize → buffer pipeline
    ├── models/            # Pydantic models
    │   ├── telemetry.py   # Telemetry data models
    │   └── session.py     # Session state models
    ├── session/           # Session lifecycle management
    │   └── manager.py     # Session state tracking
    └── websocket/         # WebSocket streaming
        ├── server.py      # WebSocket endpoint
        └── broadcaster.py # Broadcast telemetry to clients
```

## Development

### Test Endpoints

```bash
curl http://127.0.0.1:8000/health
```

### Logs

Check `INFO` level logs for startup/shutdown events.

## Key Modules

### `telemetry/reader.py`
- Reads AC shared memory (physics, graphics, static)
- Polls at 100Hz
- Handles AC connect/disconnect gracefully
- Returns raw telemetry dict

### `models/`
- Pydantic models for type safety
- PhysicsData, GraphicsData, NormalizedTelemetry
- Validates all telemetry inputs

### `session/manager.py`
- Tracks session lifecycle
- Detects lap changes, session end
- Manages resets

### `websocket/broadcaster.py`
- Broadcasts telemetry frames at 20Hz
- Handles client connections/reconnections
- JSON serialization

## Design Principles

- **Backend Authoritative**: All race logic computed in backend
- **No Business Logic in Models**: Models are data containers only
- **Async/Await**: All I/O non-blocking
- **Minimal Dependencies**: FastAPI + Pydantic only
- **Type Hints**: Full typing throughout

## Environment Variables

Optional `.env` file:

```
HOST=127.0.0.1
PORT=8000
LOG_LEVEL=INFO
RELOAD=true
```

## Performance Targets

- Shared memory read: 100Hz
- WebSocket broadcast: 20Hz
- End-to-end latency: <100ms

## Windows Only

Requires Windows for shared memory access to Assetto Corsa.
