# Phase 3: React Frontend Dashboard

## Status: COMPLETE

Real-time telemetry dashboard for the RaceControl system. Connects via WebSocket to the Python backend and renders live racing data.

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
React components (read-only visualization)
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
├── types/telemetry.ts           # NormalizedTelemetry interfaces
├── services/websocket.ts        # WebSocket client with reconnect
├── store/telemetryStore.ts      # Zustand store + alert computation
├── hooks/useTelemetrySocket.ts  # Connects WS → store
├── components/
│   ├── SessionHeader.tsx        # Session type, status, track, car, driver
│   ├── TelemetryOverview.tsx    # Speed, RPM, gear, throttle, brake
│   ├── FuelWidget.tsx           # Fuel gauge, laps remaining
│   ├── TirePanel.tsx            # 4 tires: temp, wear, brake temp
│   ├── PaceGraph.tsx            # Lap time history (Recharts line)
│   └── AlertsPanel.tsx          # Live alerts: fuel, tires, engine
├── App.tsx                      # Dashboard grid layout
├── main.tsx                     # Entry point
└── index.css                    # Tailwind directives + theme
```

## Components

### SessionHeader
Horizontal bar showing session context. Color-coded status dot (green=Live, yellow=Paused, gray=Off). Shows track, car, driver, lap, position. Disconnected badge when WebSocket drops.

### TelemetryOverview
Main driver display. Large speed number (km/h, color-coded), RPM with progress bar (green/yellow/red zones), gear number, throttle and brake bars.

### FuelWidget
Horizontal fuel gauge bar (green >30%, yellow 10-30%, red <10%). Shows liters remaining, tank capacity, and estimated laps from the backend.

### TirePanel
2x2 grid of tire cells (FL, FR, RL, RR). Each shows surface temperature (color-coded: cold=blue, optimal=green, warm=yellow, hot=red), wear percentage with progress bar, and brake temperature.

### PaceGraph
Recharts line chart of lap times. Accumulates lap history as laps are completed. Shows best lap as a green dashed reference line. Summary stats: best, last, average lap time.

### AlertsPanel
Live alert feed from the store's `computeAlerts` function. Alerts for: low fuel, tire wear, tire overheating, engine near redline. Shows "All systems nominal" when clear.

## Color System

Custom Tailwind tokens defined in `index.css`:

| Token | Use |
|-------|-----|
| `rc-bg` | Page background (#0f1117) |
| `rc-surface` | Card/panel background (#1a1d27) |
| `rc-border` | Borders (#2a2d3a) |
| `rc-accent` | Highlight/primary (blue) |
| `rc-warn` | Warnings (amber) |
| `rc-danger` | Critical alerts (red) |
| `rc-good` | Nominal/optimal (green) |
| `rc-text` | Primary text (#e2e4e9) |
| `rc-muted` | Secondary text (#8b8fa3) |

## Data Flow Constraints

- **Frontend never computes race logic** — alerts are simple threshold checks on already-normalized data
- **Complete frames only** — backend sends full NormalizedTelemetry, no deltas
- **Backend is authoritative** — all strategy and processing lives in Python
