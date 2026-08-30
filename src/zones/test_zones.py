import sys
from pathlib import Path

# Ensure src/zones is in sys.path
sys.path.append(str(Path(__file__).parent))

try:
    from zone_manager import ZoneManager
    from border_config import ZONES
except ImportError:
    from src.zones.zone_manager import ZoneManager
    from src.zones.border_config import ZONES


def main():

    print("=" * 60)
    print("       BORDERGUARD AI - ZONE ENGINE TEST")
    print("=" * 60)

    manager = ZoneManager(ZONES)

    test_points = [
        (100, 100),
        (100, 250),
        (100, 450),
        (900, 100),
        (900, 250),
        (900, 450),
    ]

    for point in test_points:

        zone = manager.get_zone(point)

        if zone is None:
            zone_name = "NONE"
        else:
            zone_name = zone.name

        print(f"Point {point} -> " f"{zone_name}")

    print("=" * 60)
    print("Zone test completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
