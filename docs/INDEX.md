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
- AC struct definitions (physics, graphics, static)
- AsyncACReader class design
- 100Hz polling mechanism
- Error handling and reconnection

### [MODELS_IMPLEMENTATION.md](MODELS_IMPLEMENTATION.md)
Pydantic data models for telemetry and session state.
- PhysicsData, GraphicsData, StaticData
- SessionState, SessionType, SessionStatus
- Validation rules and constraints
- JSON serialization

### [MODELS_REFERENCE.md](MODELS_REFERENCE.md)
Quick reference for telemetry data structures.
- Field descriptions
- Units and constraints
- Sample data
- Type information

## Status

### [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)
Completion status of Phase 1 implementation.
- Shared memory reader ✓
- Telemetry models ✓
- Session manager ✓
- Async pipeline ✓

### [FRONTEND.md](FRONTEND.md)
Phase 3 frontend dashboard implementation.
- React + TypeScript + Vite + TailwindCSS
- WebSocket client with auto-reconnect
- Zustand state management
- 6 dashboard components (telemetry, fuel, tires, pace, alerts, session)

## Development Workflow

1. **Architecture Phase:** Review Architecture.md and Characterization.md
2. **Implementation Phase:** Reference specific implementation docs (TELEMETRY_READER.md, MODELS_IMPLEMENTATION.md)
3. **Integration Phase:** Review current status in IMPLEMENTATION_COMPLETE.md
4. **Reference Phase:** Use MODELS_REFERENCE.md for quick lookups

## File Organization

```
docs/
├── Architecture.md              # System design
├── Characterization.md          # Project scope
├── TELEMETRY_READER.md          # Reader implementation
├── MODELS_IMPLEMENTATION.md     # Data models
├── MODELS_REFERENCE.md          # Quick reference
├── IMPLEMENTATION_COMPLETE.md   # Phase 1 status
├── FRONTEND.md                  # Phase 3 frontend
└── INDEX.md                     # This file
```

All documentation should be kept in this folder. Avoid scattering markdown files throughout the codebase.

## Quick Links

- **Backend Setup:** See [../backend/README.md](../backend/README.md)
- **Project Overview:** See [../README.md](../README.md)
- **System Architecture:** See Architecture.md
