# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

RaceControl — real-time telemetry dashboard for Assetto Corsa racing simulation. Reads shared memory from the game, processes via Python backend, streams via WebSocket to a React dashboard.

## Commands

```bash
# Backend
cd backend && source venv/bin/activate && python main.py   # start server on :8000
cd backend && python -m pytest test_ac_reader.py -v         # run tests

# Frontend
cd frontend && npm install && npm run dev                    # Vite dev server on :5173
```

## Architecture

```
Assetto Corsa (Windows Shared Memory: acpmf_physics/graphics/static)
    ↓ mmap + ctypes (100Hz poll)
AsyncACReader → TelemetryPipeline._normalize() → NormalizedTelemetry
    ↓ throttle to 20Hz
TelemetryBroadcaster → WebSocket /ws/telemetry → React frontend
    ↓
SessionManager (tracks lap changes, session lifecycle)
```

**Singleton factories** (global instances, lazy init):
- `get_pipeline()` → `TelemetryPipeline` (owns reader + session manager)
- `get_broadcaster()` → `TelemetryBroadcaster` (broadcasts at 20Hz)
- `get_manager()` → `ConnectionManager` (tracks WebSocket clients)

**Data flow:** `reader.py:read()` returns raw dicts → `pipeline.py:_normalize()` constructs Pydantic models → buffered at `_latest_telemetry` → broadcaster reads and pushes JSON to all WebSocket clients.

## Key Constraints

- **Backend authoritative**: all race logic in backend only. Frontend visualizes, never computes strategy.
- **Windows only**: shared memory reader uses Windows named memory maps (`acpmf_*`). Will fail gracefully on Linux.
- **Non-blocking everywhere**: `asyncio.sleep()`, never `time.sleep()`. All I/O is async.
- **Complete frames over WebSocket**: backend sends full `NormalizedTelemetry` frames, not deltas.
- **Type hints required** on all function signatures.
- **No database**: MVP streams only, no persistence.
- **No overengineering**: minimal dependencies, explicit over implicit.

## Current Phase

Phase 1 (backend foundation), Phase 2 (WebSocket streaming), and Phase 3 (React frontend) are complete. 

Status tracking is in `docs/INDEX.md` — read it before starting a new session.
