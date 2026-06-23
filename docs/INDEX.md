# RaceControl Documentation Index

Complete documentation for the RaceControl telemetry system.

## Core Architecture

### [Architecture.md](Architecture.md)
System design and high-level architecture overview.
- Data flow and pipeline
- Component responsibilities
- Performance targets
- Failure handling strategy

### [Characterization.md](Characterization.md)
Project scope, goals, and feature definitions.
- MVP features
- Core capabilities
- Design principles
- Scope boundaries

## Implementation Details

### [TELEMETRY_READER.md](TELEMETRY_READER.md)
Assetto Corsa shared memory reader implementation.
- AC struct definitions (SPageFilePhysics/Graphic/Static, ~201 fields)
- AsyncACReader class design (~150 fields extracted)
- OpenFileMappingW + MapViewOfFile Windows native API
- 100Hz polling with 2-second auto-reconnect
- Lazy Windows API init for Linux dev compatibility

### [MODELS_IMPLEMENTATION.md](MODELS_IMPLEMENTATION.md)
Pydantic data models for telemetry and session state.
- WheelData (16 fields), EngineData (10 fields), PhysicsData (24 fields)
- GraphicsData (30 fields), StaticData (12 fields)
- Validation rules and constraints
- JSON serialization for WebSocket

### [MODELS_REFERENCE.md](MODELS_REFERENCE.md)
Quick reference for telemetry data structures.
- Field descriptions
- Units and constraints
- Type information

## Frontend

### [FRONTEND.md](FRONTEND.md)
Phase 3 frontend dashboard implementation.
- React + TypeScript + Vite + TailwindCSS 4
- WebSocket client with auto-reconnect
- Zustand state management with 15 alert types
- 11 dashboard components covering ~80 data values
- Components: SessionHeader, RaceStatusStrip, TelemetryOverview, SteeringGauge, GForceMeter, FuelWidget, ERSBattery, TirePanel, BrakePanel, DamagePanel, PaceGraph, AlertsPanel

## Status

### [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)
Current implementation status.
- Phase 1: Backend foundation ✓
- Phase 2: WebSocket streaming ✓
- Phase 3: React dashboard ✓ (enhanced with comprehensive data pipeline)
- ~150 AC fields extracted, ~95 normalized, ~80 consumed by dashboard

## Development Workflow

1. **Architecture Phase:** Review Architecture.md and Characterization.md
2. **Implementation Phase:** Reference TELEMETRY_READER.md, MODELS_IMPLEMENTATION.md
3. **Frontend Phase:** Review FRONTEND.md for component documentation
4. **Integration Phase:** Review current status in IMPLEMENTATION_COMPLETE.md
5. **Reference Phase:** Use MODELS_REFERENCE.md for quick lookups

## File Organization

```
docs/
├── Architecture.md              # System design
├── Characterization.md          # Project scope
├── TELEMETRY_READER.md          # Reader implementation
├── MODELS_IMPLEMENTATION.md     # Data models
├── MODELS_REFERENCE.md          # Quick reference
├── IMPLEMENTATION_COMPLETE.md   # Current status
├── FRONTEND.md                  # Frontend dashboard
└── INDEX.md                     # This file
```

## Quick Links

- **Backend Setup:** See backend README
- **Project Overview:** See root README
- **System Architecture:** See Architecture.md
