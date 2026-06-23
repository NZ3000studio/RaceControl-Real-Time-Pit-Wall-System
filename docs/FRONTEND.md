# Phase 3: React Frontend Dashboard

## Status: COMPLETE (Enhanced)

Real-time telemetry dashboard for the RaceControl system. Connects via WebSocket to the Python backend and renders live racing data from Assetto Corsa shared memory.

## Architecture

```
WebSocket (ws://localhost:8000/ws/telemetry)
    ↓ onmessage → JSON.parse → NormalizedTelemetry
websocket.ts service (auto-reconnect, exponential backoff)
    ↓ callback
useTelemetrySocket hook (useEffect lifecycle)
    ↓ setData / setConnected
Zustand store (telemetryStore.ts)
    ↓ selector subscriptions
React components (read-only visualization, 11 components)
```

## Stack

- **React 19** + TypeScript
- **Vite** bundler
- **TailwindCSS 4** (custom rc-* color tokens)
- **Zustand** state management
- **Recharts** for lap time chart

## File Structure

```
frontend/src/
├── types/telemetry.ts           # NormalizedTelemetry interfaces (6 types)
├── services/websocket.ts        # WebSocket client with reconnect
├── store/telemetryStore.ts      # Zustand store + 15 alert types
├── hooks/useTelemetrySocket.ts  # Connects WS → store
├── components/
│   ├── SessionHeader.tsx        # Session, car, track, temps, pit window, stint, penalties
│   ├── RaceStatusStrip.tsx      # DRS, sectors, flag, rain, TC/ABS, wind, grip
│   ├── TelemetryOverview.tsx    # Speed, RPM, gear, delta time, throttle, brake, fuel rate
│   ├── SteeringGauge.tsx        # Rotating SVG steering wheel + angle readout
│   ├── GForceMeter.tsx          # G-circle dot plot + lateral/longitudinal bars
│   ├── FuelWidget.tsx           # Fuel gauge, liters, laps remaining, fuel per lap
│   ├── ERSBattery.tsx           # KERS/ERS energy, charge bar, deploy/recovery mode
│   ├── TirePanel.tsx            # 4 tires: 5-layer temps, pressure, wear, brake detail
│   ├── BrakePanel.tsx           # Brake pressure per wheel, bias, pad/disc life
│   ├── DamagePanel.tsx          # 5-zone body damage + per-corner suspension damage
│   ├── PaceGraph.tsx            # Lap time history (Recharts line chart)
│   └── AlertsPanel.tsx          # Live alerts: fuel, tires, damage, flags, etc.
├── App.tsx                      # Dashboard grid layout
├── main.tsx                     # Entry point
└── index.css                    # Tailwind directives + theme
```

## Components

### SessionHeader
Horizontal bar showing session context. Color-coded status dot. Shows session type, status, track, car, driver, lap, position. Right side: air/road temperature, pit window laps, stint time remaining, active penalty timer.

### RaceStatusStrip
Compact status bar: DRS state (off/ready/on with colored indicator), sector S1/S2/S3, track flag (green/yellow/blue/white/checkered), rain/wet indicator, TC/ABS active, wind arrow + speed, track grip %. Auto-hides inactive indicators.

### TelemetryOverview
Main driver display. Large speed number (km/h, color-coded), delta time to best lap (green=improving, red=losing, formatted as ±s.sss), RPM with progress bar, gear number, throttle and brake bars. Shows fuel per lap rate when available.

### SteeringGauge
Rotating SVG steering wheel with 4 spokes and center hub. Rotates based on steering angle (±180° visual range). Shows numeric steering angle in degrees below the wheel.

### GForceMeter
G-circle visualization with dot plotting lateral vs longitudinal G-force. Outer/mid/inner reference rings, crosshairs with BRK/ACC/L/R labels. Below the circle: lateral and longitudinal G-force bar gauges with numeric readout. Total G-force displayed as a number.

### FuelWidget
Horizontal fuel gauge bar (green >30%, yellow 10-30%, red <10%). Shows liters remaining, tank capacity, estimated laps remaining from backend, and actual fuel consumption rate (L/lap).

### ERSBattery
Shows KERS/ERS energy in kJ. Battery charge percentage bar (cyan/yellow/red color zones). Deployment and recovery level numbers. Charging/idle state indicator. Auto-hides when car has no ERS/KERS.

### TirePanel
Full-width 2×2 grid of detailed tire cells (FL, FR, RL, RR). Each tire shows:
- **5-layer temperatures:** Surface, Core, Inner, Middle, Outer — with color coding
- **Tire pressure** in PSI
- **Wear** percentage with progress bar
- **Brake temperature** with color coding
- **Pad life** and **Disc life** mini progress bars

### BrakePanel
Per-wheel brake pressure visualization (vertical bar per wheel), brake bias percentage with distribution bar, pad life and disc life summary table for all 4 wheels.

### DamagePanel
5-zone body damage bars (Body, Engine, Aero, Suspension Front, Suspension Rear) with color coding (green/yellow/orange/red). Per-corner suspension damage mini-bars. Shows "No damage" when clean.

### PaceGraph
Recharts line chart of lap times. Accumulates lap history as laps are completed. Summary stats: best, last, average lap time.

### AlertsPanel
Live alert feed from store's `computeAlerts` function. 15 alert types:
- Fuel: critical (<2 laps), warning (<5 laps)
- Tires: heavy wear (<30%), moderate wear (<50%), overheating (>110°C), lockup/wheelspin (slip >30%), severe slip (>50%)
- Brakes: pad critical (<15%), disc critical (<15%)
- Engine: redline (>95% max RPM)
- Damage: severe (>50%), moderate (>20%), engine damage
- Session: DRS engaged, TC active, ABS active, pit limiter, pit window open
- Weather: rain lights/tires
- Track: yellow flag, penalty active
Shows "All systems nominal" when clear.

## Color System

Custom Tailwind tokens defined in `index.css`:

| Token | Use |
|-------|-----|
| `rc-bg` | Page background (#0f1117) |
| `rc-surface` | Card/panel background (#1a1d27) |
| `rc-border` | Borders (#2a2d3a) |
| `rc-accent` | Highlight/primary (cyan-blue) |
| `rc-warn` | Warnings (amber) |
| `rc-danger` | Critical alerts (red) |
| `rc-good` | Nominal/optimal (green) |
| `rc-text` | Primary text (#e2e4e9) |
| `rc-muted` | Secondary text (#8b8fa3) |

## Dashboard Layout

```
SessionHeader (full width) — session, car, track, temps, pit, stint, penalty
RaceStatusStrip (full width) — DRS, S1/S2/S3, flag, rain, TC/ABS, wind, grip

[3-column grid]
  Left column:
    TelemetryOverview (speed, RPM, gear, delta, throttle, brake, fuel rate)
    GForceMeter (G-circle + lateral/longitudinal bars)
    
  Center column:
    SteeringGauge (rotating steering wheel)
    PaceGraph (lap time history + stats)
    AlertsPanel (live alert feed)
    
  Right column:
    FuelWidget (fuel gauge + laps remaining + consumption rate)
    ERSBattery (ERS/KERS energy + charge bar + deploy/recovery)
    BrakePanel (brake pressure + bias + pad/disc life)
    DamagePanel (5-zone damage + suspension damage)

TirePanel (full width) — 4 tires × 5 temp layers + pressure + wear + brake detail
```

## Data Flow Constraints

- **Frontend never computes race logic** — alerts are threshold checks on already-normalized data
- **Complete frames only** — backend sends full NormalizedTelemetry, no deltas
- **Backend is authoritative** — all strategy and processing lives in Python
- **~80 data values consumed** across 11 components from the ~95 values sent over WebSocket
