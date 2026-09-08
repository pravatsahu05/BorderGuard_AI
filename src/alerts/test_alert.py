import sys
from pathlib import Path

# Add project root and src subdirectories to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(BASE_DIR / "intrusion"))
sys.path.append(str(BASE_DIR / "risk"))
sys.path.append(str(BASE_DIR))

try:
    from intrusion.event import IntrusionEvent
except ImportError:
    from event import IntrusionEvent

try:
    from risk.risk_engine import RiskEngine
except ImportError:
    from risk_engine import RiskEngine

from alert_engine import AlertEngine



def main():

    print("=" * 70)
    print("       BORDERGUARD AI - ALERT ENGINE TEST")
    print("=" * 70)

    # --------------------------------------------------------
    # Create intrusion event.
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
    # Risk evaluation.
    # --------------------------------------------------------

    risk_engine = RiskEngine()

    risk_result = risk_engine.evaluate(event)

    # --------------------------------------------------------
    # Alert generation.
    # --------------------------------------------------------

    alert_engine = AlertEngine(minimum_severity="MEDIUM")

    alert = alert_engine.create_alert(
        event,
        risk_result,
    )

    if alert:

        print("\nALERT GENERATED")

        print(f"Alert ID   : " f"{alert.alert_id}")

        print(f"Event ID   : " f"{alert.event_id}")

        print(f"Severity   : " f"{alert.severity}")

        print(f"Risk Score : " f"{alert.risk_score:.2f}")

        print(f"Message    : " f"{alert.message}")

    else:

        print("\nNo alert generated.")

    print("=" * 70)


if __name__ == "__main__":
    main()
