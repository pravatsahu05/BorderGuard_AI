import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(BASE_DIR / "intrusion"))
sys.path.append(str(BASE_DIR))

try:
    from intrusion.event import IntrusionEvent
except ImportError:
    from event import IntrusionEvent

from risk_engine import RiskEngine



def main():

    print("=" * 70)
    print("       BORDERGUARD AI - RISK ENGINE TEST")
    print("=" * 70)

    # --------------------------------------------------------
    # Create simulated intrusion event.
    # --------------------------------------------------------

    event = IntrusionEvent(
        event_id="EVT-DEMO001",
        timestamp=0.0,
        camera_id="CAM-01",
        track_id=12,
        object_type="person",
        confidence=0.92,
        previous_zone="WARNING",
        current_zone="RESTRICTED",
        direction="DOWN",
        speed=85.0,
        event_type="RESTRICTED_ZONE_ENTRY",
        dwell_time=5.0,
        severity="HIGH",
    )

    # --------------------------------------------------------
    # Evaluate risk.
    # --------------------------------------------------------

    engine = RiskEngine()

    result = engine.evaluate(event)

    # --------------------------------------------------------
    # Display result.
    # --------------------------------------------------------

    print(f"\nEvent ID : {event.event_id}")

    print(f"Risk     : {result.score:.2f}")

    print(f"Severity : {result.severity}")

    print("\nBreakdown:")

    for factor, data in result.breakdown.items():

        print(f"{factor:15s} " f"{data['contribution']:.2f}")

    print("=" * 70)


if __name__ == "__main__":
    main()
