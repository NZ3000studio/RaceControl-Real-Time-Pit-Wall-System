"""Assetto Corsa shared memory struct definitions.

This module defines the ctypes structures that map to Assetto Corsa's shared
memory buffers on Windows. These structures are based on the AC telemetry API
and community-documented offsets.

Shared memory regions:
  - acpmf_physics: Updated at high frequency (~1000Hz), contains physics data
  - acpmf_graphics: Updated moderately, contains graphics/session info
  - acpmf_static: Rarely updated, contains static car/track info

References:
  - AC Forum: https://www.assettocorsa.net/forum/
  - Community telemetry docs and reverse-engineered offsets
  - AC modding documentation

Notes on field layout:
  - All structures use _pack_ = 1 to match binary memory layout
  - Wheel arrays are in order: [FL, FR, RL, RR] (Front-Left, Front-Right, etc)
  - Car arrays in physics are for all cars on track (use focusedCarIndex)
  - All floating point values are IEEE 754 single precision (32-bit)
"""

from ctypes import (
    Structure,
    c_float,
    c_int,
    c_char,
    c_ubyte,
    c_wchar,
    POINTER,
    sizeof,
)
from typing import Final

# Define wheel count constant
WHEELS: Final[int] = 4


class CarPhysics(Structure):
    """Physics data for a single car in the physics packet."""

    _pack_ = 1
    _fields_ = [
        ("speed", c_float),  # m/s
        ("throttle", c_float),  # 0-1
        ("steer", c_float),  # -1 to 1 (left/right input)
        ("brake", c_float),  # 0-1
        ("clutch", c_float),  # 0-1
        ("leftBlinker", c_ubyte),  # bool
        ("rightBlinker", c_ubyte),  # bool
        ("lights", c_ubyte),  # 0-3 (off, low, high)
        ("flashingLights", c_ubyte),  # bool
        ("headlightFlashing", c_ubyte),  # bool
        ("exhaustFlame", c_ubyte),  # bool
        ("wiper", c_ubyte),  # bool
        ("_padding0", c_ubyte * 2),  # padding
        ("gear", c_int),  # 0=R, 1=N, 2-7=gears
        ("rpm", c_float),  # RPM
        ("maxRpm", c_float),  # Max RPM
        ("maxTorque", c_float),  # Max torque
        ("brakePressure", c_float),  # Brake pressure
        ("fuel", c_float),  # Current fuel (liters)
        ("maxFuel", c_float),  # Max fuel capacity
        ("fuelPerLap", c_float),  # Fuel consumption per lap
        ("magnesum", c_ubyte),  # bool (magnesium wheels)
        ("_padding1", c_ubyte * 3),  # padding
        ("engineLimiter", c_ubyte),  # bool
        ("_padding2", c_ubyte * 3),  # padding
        # Wheel data (4 wheels: FL, FR, RL, RR)
        ("wheelAngularSpeed", c_float * WHEELS),  # rad/s
        ("slipAngle", c_float * WHEELS),  # radians
        ("slipRatio", c_float * WHEELS),  # slip ratio (0-1)
        ("ndSlip", c_float * WHEELS),  # normalized slip
        ("load", c_float * WHEELS),  # wheel load (kg)
        ("temps", c_float * WHEELS),  # wheel temperature (Celsius)
        ("wear", c_float * WHEELS),  # tire wear (0-1, 1=new)
        ("pressure", c_float * WHEELS),  # tire pressure (psi)
        ("tyreCoreTemp", c_float * WHEELS),  # tire core temp (Celsius)
        ("camber", c_float * WHEELS),  # camber angle (radians)
        ("suspension", c_float * WHEELS),  # suspension travel
        ("rideHeight", c_float * WHEELS),  # ride height
        ("brakeTempK", c_float * WHEELS),  # brake temp (Kelvin)
        ("brakePad", c_ubyte * WHEELS),  # brake pad material (0-6)
        ("_padding3", c_ubyte * 4),  # padding to next car
        ("brakeDiscTemp", c_float * WHEELS),  # brake disc temp (Celsius)
        ("clutchSlip", c_float),  # clutch slip ratio
        ("clutchEngaged", c_float),  # clutch engagement (0-1)
        ("rpmLimiterCut", c_float),  # limiter cut value
        ("turboBoostLevel", c_float),  # turbo boost level
        ("airDensity", c_float),  # air density (kg/m^3)
        ("airTemp", c_float),  # air temperature (Celsius)
        ("roadTemp", c_float),  # road temperature (Celsius)
        ("localAngularVelocity", c_float * 3),  # angular velocity (x, y, z)
        ("finalFF", c_float),  # final force feedback
        ("performanceMeter", c_float),  # performance meter
        ("engineBrake", c_int),  # engine braking enabled
        ("ersRecoveryLevel", c_float),  # ERS recovery level
        ("ersPowerLevel", c_float),  # ERS power level
        ("ersHeatCharging", c_float),  # ERS heat charging
        ("ersIsCharging", c_int),  # ERS is charging
        ("kersCharge", c_float),  # KERS charge (deprecated in newer AC)
        ("kersInput", c_float),  # KERS input (deprecated)
        ("drsAvailable", c_int),  # DRS available
        ("drsEngaged", c_int),  # DRS engaged
        ("antilockBrakesEnabled", c_int),  # ABS enabled
        ("tyreSpeedSmoothing", c_int),  # tyre speed smoothing
        ("ffEffect", c_float),  # force feedback effect
        ("slipSpeedKmh", c_float),  # slip speed in km/h
    ]


class PhysicsPacket(Structure):
    """Complete physics packet from acpmf_physics shared memory.

    This structure is updated frequently (100Hz+) and contains all physics
    data for all cars on track. Typically ~11KB in size.

    Estimated size for modern AC: ~12,000-14,000 bytes depending on car count.
    """

    _pack_ = 1
    _fields_ = [
        ("nbCars", c_int),  # Number of cars
        ("focusedCarIndex", c_int),  # Index of player car
        ("activeCars", c_int),  # Number of active cars
        ("_padding", c_ubyte * 60),  # Reserved/padding to reach offset 72
        ("carData", CarPhysics * 64),  # Up to 64 cars of data
    ]


class GraphicsPacket(Structure):
    """Graphics/session packet from acpmf_graphics shared memory.

    Contains session-level info (laps, position, status) and graphics
    settings. Updated less frequently than physics (~60Hz).

    Size: ~10KB
    """

    _pack_ = 1
    _fields_ = [
        ("packetId", c_int),  # Packet sequence ID
        ("status", c_int),  # 0=off, 1=replay, 2=live, 3=paused
        ("session", c_int),  # 0=practice, 1=qualify, 2=race, 3=hotlap, 4=time attack, 5=drift, 6=drag
        ("currentTime", c_char * 15),  # HH:MM:SS.mmm
        ("lastTime", c_char * 15),  # Last lap time
        ("bestTime", c_char * 15),  # Best lap time
        ("split", c_char * 15),  # Sector split time
        ("completedLaps", c_int),  # Completed laps
        ("position", c_int),  # Position in grid/race
        ("iCurrentTime", c_int),  # Current time in milliseconds
        ("iLastTime", c_int),  # Last lap time in milliseconds
        ("iBestTime", c_int),  # Best lap time in milliseconds
        ("sessionTimeLeft", c_float),  # Session time remaining (seconds)
        ("sessionTimeLeftDouble", c_float),  # Double precision time left
        ("sessionTimeTotal", c_float),  # Total session time
        ("isLapValid", c_int),  # Is current lap valid
        ("fuelXLap", c_float),  # Fuel remaining (estimated laps)
        ("rainLights", c_int),  # Rain lights on (bool)
        ("rainTyres", c_int),  # Rain tires equipped (bool)
        ("ambientTemp", c_float),  # Ambient temperature (Celsius)
        ("roadTemp", c_float),  # Road temperature (Celsius)
        ("bulletPoints", c_int),  # Bullet points for penalty
        ("crashState", c_int),  # Crash state
        ("numberOfTyresOut", c_int),  # Number of tires out of track
        ("lapInvalidated", c_int),  # Is lap invalidated
        ("maxContact", c_int),  # Max contact
        ("maxContactsPerLap", c_int),  # Max contacts per lap
        ("trackGripLevel", c_float),  # Track grip level
        ("isSetupMenuVisible", c_int),  # Setup menu visible
        ("mainDisplayIndex", c_int),  # Main display index
        ("secondaryDisplayIndex", c_int),  # Secondary display index
        ("tc", c_int),  # Traction control level
        ("tcCut", c_int),  # TC cut level
        ("engineMap", c_int),  # Engine map
        ("abs", c_int),  # ABS level
        ("fuelUsePerLap", c_float),  # Fuel consumption per lap (liters)
        ("radiationTemp", c_float),  # Radiation temperature
        ("ambientRadiation", c_float),  # Ambient radiation
        ("engineTemp", c_float),  # Engine temperature (Celsius)
        ("waterTemp", c_float),  # Water temperature (Celsius)
        ("brakeTemp", c_float),  # Brake temperature (Celsius)
        ("clutch", c_float),  # Clutch
        ("currentMaxRpm", c_int),  # Current max RPM
        ("mz", c_float),  # Magic number (not used)
        ("n2o", c_float),  # N2O (laughing gas)
        ("turboBoost", c_float),  # Turbo boost
        ("airDensity", c_float),  # Air density
        ("airTemp", c_float),  # Air temperature
        ("roadTemp2", c_float),  # Road temperature 2
        ("localAngularVelocity", c_float * 3),  # Local angular velocity
        ("finalFF", c_float),  # Final force feedback
        ("performanceMeter", c_float),  # Performance meter value
        ("engineBrake", c_int),  # Engine brake
        ("ersRecoveryLevel", c_float),  # ERS recovery level
        ("ersPowerLevel", c_float),  # ERS power level
        ("ersHeatCharging", c_float),  # ERS heat charging
        ("ersIsCharging", c_int),  # ERS is charging
        ("kersCharge", c_float),  # KERS charge
        ("kersInput", c_float),  # KERS input
        ("drsAvailable", c_int),  # DRS available
        ("drsEngaged", c_int),  # DRS engaged
        ("ignitionStarted", c_int),  # Ignition started
        ("brakesFirstApplied", c_int),  # Brakes first applied
        ("gearSelectionActive", c_int),  # Gear selection active
        ("differentialSwitch", c_int),  # Differential switch
        ("antiLockBrakes", c_int),  # Anti-lock brakes
        ("engineLimiter", c_int),  # Engine limiter
        ("currentGear", c_int),  # Current gear (0=N, 1-6=gears)
        ("pitLimiterOn", c_int),  # Pit limiter on
        ("abs", c_int),  # ABS (repeated field - actual layout may vary)
        ("turboSpinRate", c_float),  # Turbo spin rate
        ("turboAngularVelocity", c_float),  # Turbo angular velocity
        ("turboBoostAmount", c_float),  # Turbo boost amount
        ("airBumpSpeedFront", c_float),  # Air bump speed front
        ("airBumpSpeedRear", c_float),  # Air bump speed rear
        ("aeroDamage", c_float),  # Aero damage
        ("engineDamage", c_float),  # Engine damage
    ]


class StaticPacket(Structure):
    """Static info packet from acpmf_static shared memory.

    Contains static information that rarely changes during a session:
    car model, track, driver name, setup file, etc.

    Size: ~5-10KB
    """

    _pack_ = 1
    _fields_ = [
        ("smVersion", c_int),  # Shared memory version
        ("acVersion", c_int),  # AC version
        ("numberOfSessions", c_int),  # Number of sessions
        ("numberOfCars", c_int),  # Number of cars
        ("carModel", c_char * 64),  # Car model name (e.g., "ferrari_sf90")
        ("track", c_char * 64),  # Track name (e.g., "monza")
        ("playerName", c_char * 64),  # Player/driver name
        ("playerSurname", c_char * 64),  # Player surname
        ("playerNick", c_char * 64),  # Player nickname
        ("sectorCount", c_int),  # Number of sectors
        ("_padding", c_ubyte * 256),  # Padding for future expansion
        ("maxBrakeBias", c_float),  # Max brake bias
        ("fuel", c_float),  # Fuel
        ("maxFuel", c_float),  # Max fuel
        ("penaltiesEnabled", c_int),  # Penalties enabled
        ("aidFuelRate", c_float),  # Fuel aid rate
        ("aidTireRate", c_float),  # Tire wear aid rate
        ("aidMechanicalDamage", c_float),  # Mechanical damage aid
        ("aidAllowTraction", c_int),  # Allow traction control
        ("aidAllowAbs", c_int),  # Allow anti-lock brakes
        ("aidAllowStabilityControl", c_int),  # Allow stability control
        ("aidForceClosedDifferential", c_int),  # Force closed differential
        ("aidAutoClutch", c_int),  # Auto clutch
        ("aidAutoBlip", c_int),  # Auto blip
        ("hasDRS", c_int),  # Has DRS
        ("hasERS", c_int),  # Has ERS
        ("hasKERS", c_int),  # Has KERS
        ("kersMaxJ", c_float),  # KERS max joules
        ("hasHRS", c_int),  # Has hydraulic recovery system
        ("brakeTorque", c_float),  # Brake torque
        ("brakeBias", c_float),  # Brake bias
        # Track info
        ("trackSPlineLength", c_float),  # Track spline length (meters)
        ("trackConfiguration", c_char * 64),  # Track configuration
        ("ersMaxPower", c_float),  # ERS max power
        ("ersDeployWindow", c_int),  # ERS deploy window
        ("hybridType", c_int),  # Hybrid type
        ("isTimedSession", c_int),  # Is timed session
        ("hasExtraLap", c_int),  # Has extra lap
        ("carSkinNumber", c_int),  # Car skin number
        ("seriesSkinNumber", c_int),  # Series skin number
        ("saturationLevel", c_float),  # Saturation level
        ("formationLapType", c_int),  # Formation lap type
        ("autoShiftGears", c_int),  # Auto shift gears
        ("autoShiftSpecialGear", c_int),  # Auto shift special gear
        ("useCustomSetup", c_int),  # Use custom setup
    ]


# Helper function to get struct sizes
def get_struct_sizes() -> dict[str, int]:
    """Return the byte sizes of all struct types.

    Useful for validation and debugging.
    """
    return {
        "PhysicsPacket": sizeof(PhysicsPacket),
        "GraphicsPacket": sizeof(GraphicsPacket),
        "StaticPacket": sizeof(StaticPacket),
        "CarPhysics": sizeof(CarPhysics),
    }
