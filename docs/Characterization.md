# Real-Time Pit Wall System (Assetto Corsa Telemetry Dashboard)

## Overview
A local real-time telemetry system for racing simulation. It reads live game data from Assetto Corsa shared memory, processes it in a Python backend, and streams structured insights to a web-based dashboard for live race strategy support.

The system runs locally and is designed to be installable and usable by non-developers as a standalone tool.

---

## Goals
- Capture live telemetry from Assetto Corsa shared memory in real time
- Convert raw game data into meaningful racing insights
- Stream processed data to a web dashboard via WebSockets
- Provide a clean, readable UI for non-technical users
- Support replay mode for demo purposes without running the game

---

## Core Features

### Real-Time Telemetry
- Speed, RPM, gear
- Fuel consumption + estimated laps remaining
- Tire temperatures and wear estimation
- Lap timing and pace tracking

### Strategy Insights
- Pit window estimation
- Tire degradation warnings
- Fuel strategy updates
- Pace delta tracking

### Replay Mode (Demo Mode)
- Record telemetry sessions
- Replay race data in real time
- Used for demos without game dependency

---

## System Architecture

```text
Assetto Corsa (Shared Memory)
        ↓
Python Backend (FastAPI + WebSockets)
        ↓
WebSocket Stream
        ↓
React Frontend Dashboard
````

---

## Backend (Python)

### Responsibilities

* Read shared memory telemetry from Assetto Corsa
* Parse binary data into structured objects
* Process racing logic (fuel, tires, pace, strategy)
* Manage session lifecycle (start, lap change, end)
* Stream updates via WebSockets
* Record telemetry for replay mode

### Tech Stack

* Python
* FastAPI
* WebSockets (async)
* mmap / ctypes
* pydantic
* asyncio

### Internal Modules

* telemetry_reader (shared memory interface)
* processor (calculations + strategy logic)
* session_manager (state handling)
* replay_recorder (log telemetry)
* websocket_server (streaming layer)

---

## Frontend (React)

### Responsibilities

* Display real-time telemetry dashboard
* Render graphs and live indicators
* Manage UI state from WebSocket stream
* Provide clean, non-technical user experience

### Tech Stack

* React
* TypeScript
* Vite
* TailwindCSS
* Zustand (state management)
* Recharts (data visualization)

### UI Components

* Telemetry overview panel
* Fuel strategy widget
* Tire condition indicators
* Pace graph
* Alerts / warnings panel
* Session status header

---

## Data Flow

1. Game writes telemetry to shared memory
2. Python backend reads memory at fixed interval
3. Raw data is parsed and normalized
4. Processing engine calculates insights
5. Structured data is broadcast via WebSocket
6. React frontend updates UI in real time

---

## Communication Protocol

### WebSocket Frequency

* 10–30 updates per second (UI optimized, not raw physics rate)

### Message Example

```json
{
  "session": {
    "status": "race",
    "lap": 12
  },
  "car": {
    "speed": 182,
    "rpm": 7200,
    "gear": 4
  },
  "fuel": {
    "remaining_laps": 4.2
  },
  "tires": {
    "front_left_temp": 91
  },
  "strategy": {
    "pit_window_open": true
  }
}
```

---

## Performance Targets

* End-to-end latency: < 100ms
* Stable real-time stream (no data drops under normal load)
* Efficient frontend rendering (no excessive re-renders)
* Automatic reconnect on WebSocket failure
* Low CPU usage for continuous background running

---

## Deployment Model

### Local App Mode (Primary)

* One-click launcher
* Starts Python backend automatically
* Opens React UI in browser
* No manual setup required for end users

### Optional Future Upgrade

* Electron wrapper for full desktop application experience

---

## Design Principles

* Backend is the single source of truth
* Frontend only visualizes data (no business logic)
* System is modular and separated by responsibility
* Avoid overengineering in MVP stage
* Optimize for real-time performance and stability
* Focus on usability for non-developers

---

## Scope Control (MVP Boundaries)

Not included in initial version:

* Multiplayer synchronization
* Cloud backend or online accounts
* Advanced AI strategy engine
* Machine learning predictions
* External integrations beyond Assetto Corsa

---

## Value Proposition

This project demonstrates:

* Real-time systems engineering
* Low-level OS integration (shared memory)
* Full-stack architecture design
* Streaming data pipelines
* Backend processing logic design
* Product-level UI/UX thinking
* Practical deployment of local applications

---

## Summary

A local real-time telemetry and strategy system for racing simulation that transforms raw game data into actionable insights through a Python backend and a React dashboard, designed for both usability and engineering depth.
 
