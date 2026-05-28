# RaceControl Lead Engineer - Session Handoff

**Last Updated:** 2026-05-28 13:11  
**Status:** Phase 1 COMPLETE, Phase 2 READY  
**Session:** Implementation Checkpoint

---

## Executive Summary

RaceControl is a real-time telemetry system for Assetto Corsa racing simulation.

**Architecture:**
```
Assetto Corsa (Windows Shared Memory)
    ↓
Python Backend (FastAPI + asyncio + WebSockets)
    ↓
React Frontend (TypeScript, Vite, TailwindCSS, Zustand)
```

**Tech Stack:**
- Backend: Python 3.11+, FastAPI, asyncio, mmap, ctypes, Pydantic
- Frontend: React 18+, TypeScript, Vite, TailwindCSS, Zustand, Recharts
- Architecture: Monorepo, modular, async-first, backend-authoritative

---

## Project Status

### Phase 1: Backend Foundation ✅ COMPLETE

**Completed 2026-05-28:**

1. ✅ **Backend Scaffolding** (p1-1-1)
   - FastAPI app on localhost:8000
   - /health endpoint
   - venv with all dependencies
   - module structure ready
   - **Files:** main.py, config.py, requirements.txt, backend/README.md

2. ✅ **Shared Memory Reader** (p1-1-2)
   - AsyncACReader class (fully async, non-blocking)
   - AC struct definitions (PhysicsPacket, GraphicsPacket, StaticPacket)
   - 100Hz polling capability
   - Graceful AC connect/disconnect handling
   - Full type hints and error handling
   - **Files:** app/telemetry/ac_structs.py, app/telemetry/reader.py

3. ✅ **Telemetry Models** (p1-1-3)
   - Pydantic models: PhysicsData, GraphicsData, StaticData
   - WheelData, EngineData containers
   - NormalizedTelemetry combined frame
   - SessionType, SessionStatus enums
   - Full validation and JSON serialization
   - **Files:** app/models/telemetry.py, app/models/session.py

4. ✅ **Session Manager** (p1-1-4)
   - SessionManager class tracking lifecycle
   - Lap change detection
   - Session start/end detection
   - State management and resets
   - **Files:** app/session/manager.py

5. ✅ **Async Pipeline** (p1-1-5)
   - TelemetryPipeline orchestrating reader→normalize→buffer
   - 100Hz read, 20Hz broadcast throttle
   - Fully async coordination
   - get_pipeline() singleton factory
   - **Files:** app/telemetry/pipeline.py

### Phase 2: WebSocket Streaming ⏳ READY

**Next (4 tasks):**
1. p2-2-1: WebSocket Server - /ws/telemetry endpoint
2. p2-2-2: Broadcaster - Async broadcast loop at 20Hz
3. p2-2-3: CORS Config - Allow frontend localhost:5173
4. p2-2-4: Error Handling - Graceful failures, logging, reconnect

### Phase 3: Frontend & Integration ⏳ NOT STARTED

**7 tasks** - React dashboard, WebSocket client, Zustand store, components, etc.

---

## Architecture Decisions

### Backend Design
- **Backend Authoritative:** All race logic in backend only
- **Non-blocking:** Full async/await (no blocking calls anywhere)
- **Modular:** Separate concerns (reader, models, session, pipeline, websocket)
- **No Database:** MVP streams only, no persistence
- **Minimal Dependencies:** FastAPI + Pydantic + stdlib only

### Data Flow
```
AC Shared Memory → AsyncACReader (100Hz)
    ↓
TelemetryPipeline.normalize() → NormalizedTelemetry
    ↓
SessionManager.update() → SessionState
    ↓
Broadcast throttle (50ms intervals = 20Hz)
    ↓
WebSocket → Frontend clients
```

### Model Strategy
- Raw AC data captured in ac_structs.py (ctypes)
- Normalized to Pydantic models (type-safe, validated)
- SessionType/Status as enums for clarity
- All models JSON serializable for WebSocket

---

## Current Codebase Structure

```
RaceControl/
├── backend/
│   ├── main.py                          # FastAPI entry point
│   ├── config.py                        # Settings
│   ├── requirements.txt                 # Dependencies
│   ├── README.md                        # Backend setup guide
│   ├── venv/                            # Python virtual environment
│   └── app/
│       ├── telemetry/
│       │   ├── __init__.py
│       │   ├── ac_structs.py           # AC packet struct definitions
│       │   ├── reader.py               # AsyncACReader class
│       │   └── pipeline.py             # TelemetryPipeline orchestration
│       ├── models/
│       │   ├── __init__.py
│       │   ├── telemetry.py            # PhysicsData, GraphicsData, StaticData, NormalizedTelemetry
│       │   └── session.py              # SessionType, SessionStatus, SessionState
│       ├── session/
│       │   ├── __init__.py
│       │   └── manager.py              # SessionManager lifecycle tracking
│       └── websocket/
│           ├── __init__.py
│           ├── server.py               # [TODO p2-2-1] WebSocket endpoint
│           └── broadcaster.py          # [TODO p2-2-2] Broadcast loop
├── frontend/
│   └── [EMPTY - Phase 3]
├── docs/
│   ├── INDEX.md                        # Documentation index
│   ├── Architecture.md                 # System design
│   ├── Characterization.md             # Project scope
│   ├── TELEMETRY_READER.md             # Reader implementation details
│   ├── MODELS_IMPLEMENTATION.md        # Models implementation details
│   ├── MODELS_REFERENCE.md             # Quick reference
│   ├── IMPLEMENTATION_COMPLETE.md      # Phase 1 status
│   └── MANAGER.md                      # THIS FILE - handoff document
├── README.md                            # Project overview
└── .github/agents/manager.agent.md     # [Legacy - use docs/MANAGER.md instead]
```

---

## Next Immediate Actions (Phase 2)

### p2-2-1: WebSocket Server
**Goal:** Create /ws/telemetry endpoint with heartbeat

**Files to create:**
- `backend/app/websocket/server.py`

**Implementation:**
```python
@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Broadcast telemetry to this client
    # Handle disconnections
    # Send heartbeat/ping
```

**Acceptance Criteria:**
- ✓ Endpoint accepts WebSocket connections
- ✓ Clients connect/disconnect cleanly
- ✓ Heartbeat mechanism prevents timeout
- ✓ Multiple clients supported
- ✓ Full error handling

**Constraints:**
- No complex state machine - keep simple
- Use FastAPI WebSocket directly
- Non-blocking with asyncio

---

### p2-2-2: Broadcaster
**Goal:** Broadcast latest telemetry to all connected clients at 20Hz

**Files to create:**
- `backend/app/websocket/broadcaster.py`

**Implementation:**
```python
class TelemetryBroadcaster:
    async def broadcast(telemetry: NormalizedTelemetry):
        # Send to all connected clients
        # Handle disconnects gracefully
        # Serialize to JSON
        
    async def add_client(websocket):
        # Track active connections
        
    async def remove_client(websocket):
        # Clean up on disconnect
```

**Acceptance Criteria:**
- ✓ Broadcasts at exactly 20Hz (50ms intervals)
- ✓ All connected clients receive updates
- ✓ No data loss on normal operation
- ✓ Handles client disconnection without error
- ✓ JSON serialization correct

---

### p2-2-3: CORS Config
**Goal:** Allow frontend localhost:5173 to connect

**Files to modify:**
- `backend/main.py`

**Implementation:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### p2-2-4: Error Handling
**Goal:** Graceful failures, comprehensive logging

**Files to modify:**
- `backend/main.py` (startup/shutdown events)
- `backend/app/telemetry/pipeline.py` (try/except, recovery)
- `backend/app/websocket/` (connection errors)

**Requirements:**
- ✓ Try/except on all async operations
- ✓ Logging at INFO/WARNING/ERROR levels
- ✓ Graceful reconnect on AC restart
- ✓ No unhandled exceptions crash server
- ✓ Detailed error messages

---

## Known Issues & Risks

1. **AC Shared Memory Layout**
   - Risk: Struct offsets may vary by AC version
   - Mitigation: Documented in docs/TELEMETRY_READER.md, can be adjusted if needed
   - Status: ✅ Current version tested

2. **Windows Only**
   - Impact: Works only on Windows (AC runs Windows-only)
   - Documentation: In README.md and backend/README.md
   - Status: ✅ Acceptable for MVP

3. **WebSocket Latency**
   - Target: <100ms end-to-end
   - Throttle: 20Hz broadcast to reduce overhead
   - Status: ⏳ Will validate in Phase 2.2

4. **Frontend State Desync**
   - Prevention: Backend sends complete frames (not deltas)
   - Validation: Phase 3.3 Zustand store integration
   - Status: ⏳ Architecture ready

---

## How to Continue This Session

### If using task agent next:

```
You are continuing RaceControl MVP Phase 2 (WebSocket streaming).

CONTEXT:
- Phase 1 (backend foundation) completed 2026-05-28
- All telemetry ingestion working (reader, models, pipeline)
- Ready for WebSocket server implementation

NEXT TASK: p2-2-1 WebSocket Server
- Create /ws/telemetry endpoint
- Support multiple clients
- Implement heartbeat
- See docs/MANAGER.md for details

ARCHITECTURE:
- FastAPI backend with async/await
- Broadcast telemetry frames at 20Hz
- JSON serialization to frontend
- Error handling with graceful reconnect

FILES CREATED THIS SESSION:
- backend/app/telemetry/{reader.py, ac_structs.py, pipeline.py}
- backend/app/models/{telemetry.py, session.py}
- backend/app/session/manager.py
- docs/ consolidated with INDEX.md
- backend/README.md

DONT BREAK:
- Keep async/await non-blocking
- Maintain modular structure
- Backend authoritative only
- Type hints everywhere
```

### If continuing manually:

1. Read this MANAGER.md file (you are here)
2. Reference docs/INDEX.md for detailed docs
3. Check SQL todos table for exact task definitions
4. Start with p2-2-1 WebSocket Server
5. Update this file after each session

---

## Testing Checklist for Phase 2

- [ ] Server starts without errors on `python main.py`
- [ ] /health endpoint responds with {"status": "ok"}
- [ ] WebSocket connects from test client
- [ ] Telemetry broadcasts at ~20Hz when AC running
- [ ] Telemetry stops cleanly when AC closes
- [ ] Multiple WebSocket clients supported
- [ ] No memory leaks after 5 min continuous operation
- [ ] Graceful error messages in logs
- [ ] CORS headers correct for localhost:5173

---

## SQL Todo Status

**Query to check:**
```sql
SELECT id, title, status FROM todos ORDER BY id;
```

**Current breakdown:**
- Phase 1: 5 done ✅
- Phase 2: 4 pending (p2-2-1 through p2-2-4)
- Phase 3: 7 pending (p3-3-1 through p3-3-7)

**Update todo status after work:**
```sql
UPDATE todos SET status = 'in_progress' WHERE id = 'p2-2-1';
-- ... work ...
UPDATE todos SET status = 'done' WHERE id = 'p2-2-1';
```

---

## Important Principles (Do Not Violate)

1. **No Business Logic in Frontend**
   - Frontend visualizes only
   - All calculations in backend

2. **Backend Authoritative**
   - Only backend owns state
   - Frontend reads only

3. **Non-Blocking Only**
   - asyncio.sleep(), never time.sleep()
   - All I/O async

4. **Type Hints Required**
   - Every function signature
   - Every variable where non-obvious

5. **Modular Architecture**
   - Reader separate from normalization
   - Normalization separate from session
   - Session separate from broadcast
   - Each file ~300 lines max

6. **No Overengineering**
   - Minimal dependencies
   - Explicit > implicit
   - Simple > clever

---

## Documentation References

- **Architecture:** docs/Architecture.md
- **Reader Details:** docs/TELEMETRY_READER.md
- **Models Details:** docs/MODELS_IMPLEMENTATION.md
- **Status:** docs/IMPLEMENTATION_COMPLETE.md
- **Quick Ref:** docs/MODELS_REFERENCE.md
- **Backend Setup:** backend/README.md
- **Project Overview:** README.md

---

## Communication Protocol

**From AC Shared Memory:**
- Physics at 100Hz
- Graphics at 100Hz
- Static (rarely changes)

**From Backend to Frontend:**
- NormalizedTelemetry frames at 20Hz
- JSON format via WebSocket
- Complete frames (not deltas)

**From Frontend:**
- Connection/disconnect signals
- No commands back to backend (MVP)

---

## Continuation Checklist

Use this before starting next session:

- [ ] Read this MANAGER.md thoroughly
- [ ] Check SQL todos for current status
- [ ] Verify backend/ structure matches this doc
- [ ] Run `python main.py` in backend venv (should start)
- [ ] Check that Phase 1 files exist (reader, models, pipeline, session)
- [ ] Review task description for p2-2-1 in this file
- [ ] Update this MANAGER.md after work with:
  - [ ] New files created
  - [ ] Architecture changes
  - [ ] Known issues
  - [ ] Next steps

---

**End of Handoff Document**

For questions or clarifications, refer to docs/INDEX.md and individual doc files.

Good luck! The hard parts are done. WebSocket and React are straightforward from here.
