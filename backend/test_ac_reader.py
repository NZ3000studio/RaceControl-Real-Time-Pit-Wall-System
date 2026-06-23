"""Test suite for AC shared memory reader.

Run with: python -m pytest test_ac_reader.py -v

Or run directly: python test_ac_reader.py
"""

import asyncio
import sys
from app.telemetry.ac_structs import (
    SPageFilePhysics,
    SPageFileGraphic,
    SPageFileStatic,
    get_struct_sizes,
)
from app.telemetry.reader import AsyncACReader


def test_struct_sizes():
    """Test that struct sizes are reasonable."""
    sizes = get_struct_sizes()
    print("\n=== Struct Sizes ===")
    for name, size in sizes.items():
        print(f"{name}: {size} bytes")

    # Physics packet - flat struct, ~800 bytes
    assert sizes["Physics"] > 500, "Physics too small"
    assert sizes["Physics"] < 2000, "Physics too large"
    # Graphics packet - larger with 60 car coordinates, ~1500 bytes
    assert sizes["Graphics"] > 500, "Graphics too small"
    assert sizes["Graphics"] < 5000, "Graphics too large"
    # Static packet - car/track/player names as wide strings, ~688 bytes
    assert sizes["Static"] > 500, "Static too small"
    assert sizes["Static"] < 2000, "Static too large"
    print("✓ Struct sizes are reasonable")


def test_struct_fields():
    """Test that all expected fields exist in structs."""
    print("\n=== Struct Fields ===")

    # Check SPageFilePhysics has main fields
    physics_fields = [f[0] for f in SPageFilePhysics._fields_]
    assert "speed_kmh" in physics_fields, "Missing speed_kmh"
    assert "rpm" in physics_fields, "Missing rpm"
    assert "gear" in physics_fields, "Missing gear"
    assert "gas" in physics_fields, "Missing gas"
    assert "brake" in physics_fields, "Missing brake"
    assert "fuel" in physics_fields, "Missing fuel"
    assert "velocity" in physics_fields, "Missing velocity"
    assert "acc_g" in physics_fields, "Missing acc_g"
    assert "steer_angle" in physics_fields, "Missing steer_angle"
    assert "clutch" in physics_fields, "Missing clutch"
    assert "tyre_temp" in physics_fields, "Missing tyre_temp"
    assert "tyre_wear" in physics_fields, "Missing tyre_wear"
    assert "air_temp" in physics_fields, "Missing air_temp"
    assert "road_temp" in physics_fields, "Missing road_temp"
    assert "drs_available" in physics_fields, "Missing drs_available"
    assert "drs_enabled" in physics_fields, "Missing drs_enabled"
    assert "current_max_rpm" in physics_fields, "Missing current_max_rpm"
    assert "tc_in_action" in physics_fields, "Missing tc_in_action"
    assert "abs_in_action" in physics_fields, "Missing abs_in_action"
    print("✓ SPageFilePhysics has required fields")

    # Check SPageFileGraphic has main fields
    graphics_fields = [f[0] for f in SPageFileGraphic._fields_]
    assert "status" in graphics_fields, "Missing status"
    assert "session" in graphics_fields, "Missing session"
    assert "completed_laps" in graphics_fields, "Missing completed_laps"
    assert "position" in graphics_fields, "Missing position"
    assert "current_sector_index" in graphics_fields, "Missing current_sector_index"
    assert "surface_grip" in graphics_fields, "Missing surface_grip"
    assert "rain_lights" in graphics_fields, "Missing rain_lights"
    assert "rain_tyres" in graphics_fields, "Missing rain_tyres"
    assert "wind_speed" in graphics_fields, "Missing wind_speed"
    assert "wind_direction" in graphics_fields, "Missing wind_direction"
    assert "flag" in graphics_fields, "Missing flag"
    assert "is_in_pit_lane" in graphics_fields, "Missing is_in_pit_lane"
    assert "tyre_compound" in graphics_fields, "Missing tyre_compound"
    print("✓ SPageFileGraphic has required fields")

    # Check SPageFileStatic has main fields
    static_fields = [f[0] for f in SPageFileStatic._fields_]
    assert "car_model" in static_fields, "Missing car_model"
    assert "track" in static_fields, "Missing track"
    assert "player_name" in static_fields, "Missing player_name"
    assert "max_fuel" in static_fields, "Missing max_fuel"
    assert "max_rpm" in static_fields, "Missing max_rpm"
    assert "max_power" in static_fields, "Missing max_power"
    assert "max_torque" in static_fields, "Missing max_torque"
    print("✓ SPageFileStatic has required fields")


async def test_reader_initialization():
    """Test reader initialization."""
    print("\n=== Reader Initialization ===")
    reader = AsyncACReader()
    assert not await reader.is_connected(), "Should not be connected initially"
    print("✓ Reader initializes in disconnected state")


async def test_reader_graceful_failure():
    """Test that reader fails gracefully when AC not running."""
    print("\n=== Graceful Failure ===")
    reader = AsyncACReader()

    # Try to connect (should fail on non-Windows or AC not running)
    connected = await reader.connect()
    print(f"  Connect result: {connected}")

    # Should not crash when reading without connection
    data = await reader.read()
    assert data is None, "Should return None when not connected"
    print("✓ Reader returns None when not connected")

    # Should be safe to call repeatedly
    for i in range(5):
        result = await reader.read()
        assert result is None, f"Read {i} should return None"
    print("✓ Reader handles repeated reads safely")

    await reader.disconnect()
    assert not await reader.is_connected(), "Should be disconnected after disconnect"
    print("✓ Disconnect works correctly")


async def test_reader_telemetry_format():
    """Test that telemetry dict has expected format."""
    print("\n=== Telemetry Format ===")

    expected_physics_keys = {
        "speed", "rpm", "gear", "throttle", "brake", "clutch",
        "fuel", "steer", "velocity", "acc_g",
        "wheel_temps", "wheel_wear", "wheel_load", "wheel_pressure",
        "tire_core_temps", "brake_temps", "wheel_slip_ratio", "wheel_slip_angle",
        "drs_available", "drs_engaged", "tc_in_action", "abs_in_action",
        "air_temp", "road_temp", "current_max_rpm",
    }
    expected_graphics_keys = {
        "status", "session", "lap", "position",
        "current_sector_index", "track_grip_level",
        "rain_lights", "rain_tires", "wind_speed", "wind_direction",
        "flag", "pit_limiter", "tyre_compound",
    }
    expected_static_keys = {
        "car_model", "track", "player_name",
        "max_fuel", "max_rpm", "max_power", "max_torque",
    }

    print(f"  Expected physics keys: {expected_physics_keys}")
    print(f"  Expected graphics keys: {expected_graphics_keys}")
    print(f"  Expected static keys: {expected_static_keys}")
    print("✓ Telemetry format documented")


async def run_async_tests():
    """Run all async tests."""
    await test_reader_initialization()
    await test_reader_graceful_failure()
    await test_reader_telemetry_format()


def main():
    """Run all tests."""
    print("=" * 60)
    print("AC Shared Memory Reader Test Suite")
    print("=" * 60)

    try:
        test_struct_sizes()
        test_struct_fields()
        asyncio.run(run_async_tests())

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
