```md
# ARCHITECTURE.md

# Real-Time Pit Wall System Architecture

## Overview

The system is designed as a local real-time telemetry platform for Assetto Corsa.

It consists of:
- A Python backend responsible for telemetry ingestion and processing
- A React frontend responsible for visualization and UI interaction
- A WebSocket communication layer between both systems

The architecture prioritizes:
- Low latency
- Clean separation of concerns
- Real-time responsiveness
- Simplicity and maintainability

---

# High-Level Architecture

```text
Assetto Corsa
    ↓
Windows Shared Memory
    ↓
Telemetry Reader (Python)
    ↓
Processing Engine
    ↓
Session State Manager
    ↓
WebSocket Broadcast Server
    ↓
React Frontend Dashboard
```

---

# Repository Structure

```text
pit-wall-system/
│
├── backend/
│   ├── app/
│   │   ├── telemetry/
│   │   ├── processing/
│   │   ├── session/
│   │   ├── websocket/
│   │   ├── replay/
│   │   └── models/
│   │
│   ├── main.py
│   ├── requirements.txt
│   └── config.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── store/
│   │   ├── services/
│   │   ├── layouts/
│   │   └── types/
│   │
│   ├── package.json
│   └── vite.config.ts
│
├── docs/
│   ├── CHARACTERIZATION.md
│   ├── ARCHITECTURE.md
│   └── API_SPEC.md
│
└── scripts/
```

---

# Backend Architecture

## Responsibilities

The backend is the authoritative source of truth.

It is responsible for:

* Reading telemetry from shared memory
* Parsing binary telemetry structures
* Processing race calculations
* Managing session state
* Broadcasting structured updates
* Recording replay sessions

The frontend must never calculate racing logic.

---

# Backend Pipeline

```text
Shared Memory Reader
        ↓
Telemetry Normalization
        ↓
Processing Engine
        ↓
Session State Manager
        ↓
WebSocket Broadcast
```

---

# Shared Memory Layer

## Purpose

Reads raw telemetry directly from Assetto Corsa shared memory regions.

## Technologies

* mmap
* ctypes
* asyncio

## Shared Memory Regions

* acpmf_physics
* acpmf_graphics
* acpmf_static

## Responsibilities

* Read raw binary memory
* Parse binary structs
* Convert values into typed Python models
* Handle polling loop timing

---

# Telemetry Processing Layer

## Purpose

Transforms raw telemetry into meaningful race insights.

## Responsibilities

* Fuel calculations
* Tire temperature analysis
* Pace delta calculations
* Pit window estimation
* Alert generation

## Design Rule

Processing layer must remain independent from UI rendering.

---

# Session State Manager

## Purpose

Maintains global session state.

## Tracks

* Current session type
* Current lap
* Race status
* Connection state
* Replay mode state

## Responsibilities

* Session lifecycle transitions
* Reset handling
* Synchronization between modules

---

# WebSocket Layer

## Purpose

Streams telemetry updates to frontend clients.

## Technology

FastAPI WebSockets

## Endpoint

```text
/ws/telemetry
```

## Responsibilities

* Client connection handling
* Broadcast updates
* Reconnect support
* Heartbeat/ping handling

---

# Update Frequency Model

## Internal Read Frequency

Shared memory polling may occur at high frequency.

Example:

```text
100Hz
```

## Broadcast Frequency

Frontend updates are throttled.

Target:

```text
10–30Hz
```

This prevents:

* unnecessary UI renders
* websocket flooding
* CPU waste

---

# Replay System Architecture

## Purpose

Allow playback of recorded telemetry sessions.

## Flow

```text
Live Telemetry
      ↓
Replay Recorder
      ↓
Stored Session File
      ↓
Replay Engine
      ↓
WebSocket Stream
```

## Responsibilities

* Record structured telemetry frames
* Preserve timing intervals
* Simulate live playback

---

# Frontend Architecture

## Responsibilities

* Render telemetry data
* Visualize graphs and indicators
* Manage UI state
* Handle WebSocket connection lifecycle

The frontend must not contain race strategy logic.

---

# Frontend Stack

* React
* TypeScript
* Vite
* TailwindCSS
* Zustand
* Recharts

---

# Frontend Data Flow

```text
WebSocket Connection
        ↓
Telemetry Service
        ↓
Zustand Store
        ↓
UI Components
```

---

# Frontend Modules

## Components

Reusable UI widgets.

Examples:

* FuelWidget
* TirePanel
* PaceGraph
* SessionHeader

---

## Hooks

Examples:

* useTelemetrySocket
* useSessionState

---

## Store

Global realtime telemetry state.

Managed with Zustand.

---

# State Management Principles

## Backend Owns Truth

The backend computes and validates telemetry data.

## Frontend Displays State

Frontend visualizes already-processed data.

This avoids:

* duplicated logic
* inconsistent calculations
* frontend desynchronization

---

# Communication Protocol

## Transport

WebSocket

## Message Format

JSON

## Example

```json
{
  "session": {
    "lap": 12,
    "status": "race"
  },
  "car": {
    "speed": 182,
    "rpm": 7200,
    "gear": 4
  },
  "fuel": {
    "remaining_laps": 4.2
  },
  "strategy": {
    "pit_window_open": true
  }
}
```

---

# Failure Handling

## Supported Recovery Cases

* Game closed
* Game reopened
* WebSocket disconnect
* Frontend refresh
* Replay interruption

## Recovery Strategy

* Automatic reconnect attempts
* State reset on invalid session
* Graceful degradation when telemetry unavailable

---

# Performance Goals

## Target Latency

```text
<100ms end-to-end
```

## Stability Goals

* Continuous operation during race sessions
* Minimal frame drops
* Stable frontend rendering

---

# Architectural Principles

## Separation of Concerns

Each layer has a single responsibility.

## Backend Authority

Race logic exists only in backend.

## Real-Time Optimization

System designed around continuous streaming.

## Modular Design

Features remain isolated and replaceable.

## MVP Simplicity

Avoid unnecessary infrastructure in early versions.

---

# Future Expansion Possibilities

Potential future upgrades:

* Electron wrapper
* Multi-sim support
* Advanced analytics
* Online session sync
* AI-assisted strategy recommendations

These are intentionally excluded from MVP architecture.

---

# Summary

The system architecture is designed as a lightweight local telemetry platform with:

* low-level game integration
* real-time processing
* structured backend logic
* responsive frontend visualization

The architecture emphasizes clarity, maintainability, and real-world engineering practices while remaining achievable for a solo full-stack project.
