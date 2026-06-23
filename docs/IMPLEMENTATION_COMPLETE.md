# RaceControl — Implementation Status

## Status: Phase 1-3 Complete, Enhanced Data Pipeline

All three phases complete with comprehensive data pipeline expansion.

---

## Phase 1: Backend Foundation ✅

### Shared Memory Reader (`ac_structs.py` + `reader.py`)
- **`SPageFilePhysics`** — ~105 physics fields extracted (~800B struct)
- **`SPageFileGraphic`** — ~66 graphics/session fields extracted (~1,500B struct)
- **`SPageFileStatic`** — ~30 static car/track fields extracted (~688B struct)
- Windows native API: `OpenFileMappingW` + `MapViewOfFile` (correctly handles AC's `Local\` namespace)
- Lazy Windows API init allows import on Linux for development/testing
- 100Hz polling with 2-second auto-reconnect

### Normalization Pipeline (`pipeline.py`)
- Raw dict → Pydantic `NormalizedTelemetry` transformation
- 4 `WheelData` (16 fields each), `EngineData` (10 fields), `PhysicsData` (24 fields)
- Real G-force computed from 3D acceleration vector
- Real `max_rpm` from AC static struct (no estimation)
- Real `max_fuel` from AC static struct
- Real 3D velocity and acceleration vectors
- Real air/road temperature from physics struct

### Data Models (`models/telemetry.py`)
- **WheelData:** 16 fields — 5-layer temps, wear, load, slip, brake temp, pressure, brake pressure, pad/disc life, tire forces (Fx/Fy/Mz)
- **EngineData:** 10 fields — RPM, max RPM, throttle, brake, clutch, KERS charge/energy, ERS power/recovery/charging
- **PhysicsData:** 24 fields — speed, 3D velocity/accel, RPM, gear, inputs, fuel, wheels, engine, G-force, heading/pitch/roll, damage, brake bias
- **GraphicsData:** 30 fields — session, laps, sectors, times, delta, fuel, assists, conditions, DRS, flags, penalties, pit, stint
- **StaticData:** 12 fields — car/track/player, temps, pit window, engine specs, ERS capacity, timed race
- **NormalizedTelemetry:** Combined frame with timestamp

### Session Manager
- Session type/status tracking
- Lap change detection
- Position and fuel tracking

---

## Phase 2: WebSocket Streaming ✅

- FastAPI WebSocket endpoint at `/ws/telemetry`
- 20Hz throttled broadcast (50ms interval)
- Connection manager with client tracking
- Auto-reconnect on AC start/restart
- Graceful handling of AC not running

---

## Phase 3: React Dashboard ✅ (Enhanced)

### 11 Dashboard Components

| Component | Data Rendered |
|-----------|--------------|
| **SessionHeader** | Session type/status, track, car, driver, lap, position, air/road temp, pit window, stint time, penalty |
| **RaceStatusStrip** | DRS state, S1/S2/S3, track flag, rain/wet, TC/ABS active, wind arrow, track grip % |
| **TelemetryOverview** | Speed (km/h), delta time (±s.sss, green/red), RPM bar, gear, throttle/brake bars, fuel/lap rate |
| **SteeringGauge** | Rotating SVG steering wheel + degree readout + steering bar |
| **GForceMeter** | G-circle dot plot + lateral/longitudinal G bars + total G |
| **FuelWidget** | Fuel % bar, liters remaining/max, laps remaining, L/lap consumption |
| **ERSBattery** | KERS energy (kJ), charge % bar, deploy/recovery levels, charging state |
| **TirePanel** | 5-layer temps (surface/core/inner/mid/outer), pressure, wear, brake temp, pad/disc life — per wheel |
| **BrakePanel** | Brake pressure per wheel (vertical bars), brake bias %, pad/disc life summary |
| **DamagePanel** | 5-zone body damage + per-corner suspension damage (green→red) |
| **PaceGraph** | Lap time history line chart + best/last/average stats |
| **AlertsPanel** | 15 alert types: fuel, tires, brakes, engine, damage, flags, penalties, session events |

### Data Coverage

| Layer | Fields |
|-------|--------|
| AC Shared Memory (3 structs) | ~201 |
| Reader extraction | ~150 |
| NormalizedTelemetry (Pydantic) | ~95 |
| Frontend consumed by components | ~80 |

---

## Files Summary

```
backend/app/
├── telemetry/
│   ├── ac_structs.py         (243 lines) C struct definitions
│   ├── reader.py             (~370 lines) Async shared memory reader
│   └── pipeline.py           (~310 lines) Normalization pipeline
├── models/
│   ├── telemetry.py          (~310 lines) Pydantic models
│   └── session.py            Session state models
├── session/manager.py        Session lifecycle manager
└── websocket/
    ├── broadcaster.py        20Hz throttled broadcast
    └── server.py             Connection manager

frontend/src/
├── types/telemetry.ts        TypeScript interfaces (6 types)
├── services/websocket.ts     WebSocket client with reconnect
├── store/telemetryStore.ts   Zustand store + 15 alert types
├── hooks/useTelemetrySocket.ts
├── components/
│   ├── SessionHeader.tsx     + temps, pit window, stint, penalty
│   ├── RaceStatusStrip.tsx   DRS, sectors, flag, rain, TC/ABS, wind, grip
│   ├── TelemetryOverview.tsx + delta time, fuel rate
│   ├── SteeringGauge.tsx     Rotating SVG steering wheel
│   ├── GForceMeter.tsx       G-circle + lateral/longitudinal bars
│   ├── FuelWidget.tsx        + fuel per lap consumption rate
│   ├── ERSBattery.tsx        KERS/ERS energy + charge + deploy/recovery
│   ├── TirePanel.tsx         5-layer temps + pressure + pad/disc life
│   ├── BrakePanel.tsx        Brake pressure + bias + pad/disc life
│   ├── DamagePanel.tsx       5-zone damage + suspension damage
│   ├── PaceGraph.tsx         Lap time history
│   └── AlertsPanel.tsx       Enhanced with 15 alert types
└── App.tsx                   3-column + full-width layout
```

## Known Issues

1. **`fuel_used_per_lap`** — AC's graphics struct has this field; extracted and shown, accuracy depends on AC version
2. **air/road temp** — Read from physics struct (AC provides these); may read 0°C in some cars/conditions
3. **3-layer tire temps** — Extracted from AC physics struct; most cars provide these
4. **Opponent positions** — `car_coordinates[60][3]` available but not yet extracted (track map feature reserved)

## What's Not Yet Wired

- Opponent car coordinates (60 cars × 3D position + IDs) — for track map
- Contact patch data (12×3 floats per corner) — advanced physics
- Push-to-pass (IndyCar-specific)
- A few low-value cosmetic fields (lights stage, wiper level, turn signals, setup menu state)
