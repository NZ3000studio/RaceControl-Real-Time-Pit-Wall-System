# RaceControl

Real-time telemetry dashboard for Assetto Corsa racing simulation.

Captures live game data from shared memory, processes racing insights in Python backend, streams via WebSocket to React dashboard.

## Quick Start

### Prerequisites

- Windows 10+ (for Assetto Corsa shared memory access)
- Python 3.11+
- Node.js 18+

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend runs on `http://127.0.0.1:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

### Run Together

1. Start backend: `cd backend && python main.py`
2. In another terminal, start frontend: `cd frontend && npm run dev`
3. Open `http://localhost:5173` in browser
4. Launch Assetto Corsa

## Architecture

```
Assetto Corsa (Windows Shared Memory)
    ↓
Python Backend (FastAPI + WebSockets)
    ├── Telemetry Reader (mmap, ctypes)
    ├── Normalizer (Pydantic models)
    ├── Session Manager
    └── WebSocket Server
    ↓
React Frontend (TypeScript, Vite, TailwindCSS)
    ├── WebSocket Client Hook
    ├── Zustand State Store
    └── Live Dashboard Components
```

## Technology

### Backend

- Python 3.11+
- FastAPI
- asyncio
- WebSockets
- Pydantic
- mmap (shared memory)
- ctypes (binary struct parsing)

### Frontend

- React 18+
- TypeScript
- Vite
- TailwindCSS
- Zustand (state management)
- Recharts (data visualization)

## Project Structure

```
RaceControl/
├── backend/               # Python FastAPI server
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   └── app/
│       ├── telemetry/     # Shared memory reading
│       ├── models/        # Data models
│       ├── session/       # Session state
│       └── websocket/     # Streaming
├── frontend/              # React dashboard
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── docs/                  # Architecture docs
└── README.md
```

## Features (MVP)

- ✓ Real-time telemetry ingestion from Assetto Corsa
- ✓ Live metrics display (speed, RPM, gear, fuel)
- ✓ Session tracking
- ✓ Auto-reconnect on disconnect
- ✓ WebSocket streaming at 20Hz

## Design Principles

1. **Backend Authoritative**: All race logic in backend only
2. **Frontend Visualization-Only**: Never computes strategy
3. **Real-Time First**: Designed for <100ms end-to-end latency
4. **Modular Architecture**: Clean separation of concerns
5. **No Overengineering**: Minimal dependencies, local-only

## Development Workflow

1. Make changes in `backend/` or `frontend/`
2. Backend auto-reloads on file changes (dev mode)
3. Frontend hot-reloads via Vite
4. Test via browser at `http://localhost:5173`

## API Endpoints

### Health Check

```
GET /health
```

Response:
```json
{"status": "ok"}
```

### WebSocket Telemetry Stream

```
WS /ws/telemetry
```

Receives telemetry frames at 20Hz:
```json
{
  "session": {"lap": 12, "status": "race"},
  "car": {"speed": 182, "rpm": 7200, "gear": 4},
  "fuel": {"current": 42.5, "consumption": 1.2}
}
```

## Troubleshooting

### Backend won't start

- Ensure Python 3.11+: `python --version`
- Check venv activation: `which python` (should show venv path)
- Reinstall deps: `pip install -r requirements.txt`

### Frontend won't connect

- Backend running on localhost:8000?
- Check browser console for WebSocket errors
- Try: `curl http://127.0.0.1:8000/health`

### No telemetry data

- Assetto Corsa running?
- Shared memory files exist in AC directory?
- Check backend logs for errors

## Performance Targets

- Shared memory poll rate: 100Hz
- WebSocket broadcast: 20Hz
- End-to-end latency: <100ms
- Stable 5+ minute operation

## Future Roadmap

- Fuel strategy calculations
- Tire temperature analysis
- Pace tracking and deltas
- Replay/demo mode
- Advanced alerting system
- Lap timing breakdown

## Documentation

- [Architecture](docs/Architecture.md) - System design
- [Backend README](backend/README.md) - Backend setup & structure
- [Characterization](docs/Characterization.md) - Project scope & goals

## License

Private project.
