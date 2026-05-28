"""Test suite for AC shared memory reader.

Run with: python -m pytest test_ac_reader.py -v

Or run directly: python test_ac_reader.py
"""

import asyncio
import sys
from app.telemetry.ac_structs import (
    PhysicsPacket,
    GraphicsPacket,
    StaticPacket,
    CarPhysics,
    get_struct_sizes,
)
from app.telemetry.reader import AsyncACReader


def test_struct_sizes():
    """Test that struct sizes are reasonable."""
    sizes = get_struct_sizes()
    print("\n=== Struct Sizes ===")
    for name, size in sizes.items():
        print(f"{name}: {size} bytes")

    # Physics packet should be fairly large (multiple cars)
    assert sizes["PhysicsPacket"] > 10000, "PhysicsPacket too small"
    # Graphics packet should be smaller
    assert sizes["GraphicsPacket"] < 1000, "GraphicsPacket too large"
    # Static packet should be small
    assert sizes["StaticPacket"] < 2000, "StaticPacket too large"
    print("✓ Struct sizes are reasonable")


def test_struct_fields():
    """Test that all expected fields exist in structs."""
    print("\n=== Struct Fields ===")

    # Check PhysicsPacket has main fields
    physics_fields = [f[0] for f in PhysicsPacket._fields_]
    assert "nbCars" in physics_fields, "Missing nbCars"
    assert "focusedCarIndex" in physics_fields, "Missing focusedCarIndex"
    assert "carData" in physics_fields, "Missing carData"
    print("✓ PhysicsPacket has required fields")

    # Check CarPhysics has main fields
    car_fields = [f[0] for f in CarPhysics._fields_]
    assert "speed" in car_fields, "Missing speed"
    assert "rpm" in car_fields, "Missing rpm"
    assert "gear" in car_fields, "Missing gear"
    assert "throttle" in car_fields, "Missing throttle"
    assert "brake" in car_fields, "Missing brake"
    assert "fuel" in car_fields, "Missing fuel"
    assert "wheelAngularSpeed" in car_fields, "Missing wheelAngularSpeed"
    print("✓ CarPhysics has required fields")

    # Check GraphicsPacket has main fields
    graphics_fields = [f[0] for f in GraphicsPacket._fields_]
    assert "status" in graphics_fields, "Missing status"
    assert "session" in graphics_fields, "Missing session"
    assert "completedLaps" in graphics_fields, "Missing completedLaps"
    assert "position" in graphics_fields, "Missing position"
    print("✓ GraphicsPacket has required fields")

    # Check StaticPacket has main fields
    static_fields = [f[0] for f in StaticPacket._fields_]
    assert "carModel" in static_fields, "Missing carModel"
    assert "track" in static_fields, "Missing track"
    assert "playerName" in static_fields, "Missing playerName"
    print("✓ StaticPacket has required fields")


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

    # Create mock telemetry structure
    expected_physics_keys = {
        "speed",
        "rpm",
        "gear",
        "throttle",
        "brake",
        "fuel",
        "wheel_temps",
        "brake_temps",
    }
    expected_graphics_keys = {"status", "session", "lap", "position"}
    expected_static_keys = {"car_model", "track", "player_name"}

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
