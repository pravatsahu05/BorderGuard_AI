from intrusion_engine import IntrusionEngine


def print_event(event):

    if event is None:

        print("No event generated.")

        return

    print(f"Event ID      : {event.event_id}")

    print(f"Event Type    : {event.event_type}")

    print(f"Track ID      : {event.track_id}")

    print(f"Object Type   : {event.object_type}")

    print(f"Previous Zone : {event.previous_zone}")

    print(f"Current Zone  : {event.current_zone}")

    print(f"Direction     : {event.direction}")

    print(f"Speed         : {event.speed:.1f} px/s")

    print(f"Dwell Time    : {event.dwell_time:.1f}s")

    print(f"Severity      : {event.severity}")


def main():

    engine = IntrusionEngine(camera_id="CAM-01")

    print("=" * 60)
    print("     BORDERGUARD AI - INTRUSION ENGINE TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # Scenario 1 — Normal movement
    # --------------------------------------------------------

    print("\nScenario 1: SAFE -> WARNING")

    event = engine.evaluate(
        track_id=1,
        object_type="person",
        confidence=0.90,
        previous_zone="SAFE",
        current_zone="WARNING",
        direction="DOWN",
        speed=50.0,
        dwell_time=2.0,
    )

    print_event(event)

    # --------------------------------------------------------
    # Scenario 2 — Restricted entry
    # --------------------------------------------------------

    print("\nScenario 2: WARNING -> RESTRICTED")

    event = engine.evaluate(
        track_id=1,
        object_type="person",
        confidence=0.92,
        previous_zone="WARNING",
        current_zone="RESTRICTED",
        direction="DOWN",
        speed=60.0,
        dwell_time=1.0,
    )

    print_event(event)

    # --------------------------------------------------------
    # Scenario 3 — Staying inside
    # --------------------------------------------------------

    print("\nScenario 3: RESTRICTED -> RESTRICTED")

    event = engine.evaluate(
        track_id=1,
        object_type="person",
        confidence=0.92,
        previous_zone="RESTRICTED",
        current_zone="RESTRICTED",
        direction="STATIONARY",
        speed=0.0,
        dwell_time=5.0,
    )

    print_event(event)

    # --------------------------------------------------------
    # Scenario 4 — Restricted dwell violation
    # --------------------------------------------------------

    print("\nScenario 4: Restricted dwell")

    event = engine.evaluate(
        track_id=1,
        object_type="person",
        confidence=0.92,
        previous_zone="RESTRICTED",
        current_zone="RESTRICTED",
        direction="STATIONARY",
        speed=0.0,
        dwell_time=15.0,
    )

    print_event(event)

    # --------------------------------------------------------
    # Scenario 5 — Direction violation
    # --------------------------------------------------------

    print("\nScenario 5: Direction violation")

    event = engine.evaluate(
        track_id=2,
        object_type="person",
        confidence=0.88,
        previous_zone="SAFE",
        current_zone="WARNING",
        direction="UP",
        speed=70.0,
        dwell_time=3.0,
    )

    print_event(event)

    print("=" * 60)


if __name__ == "__main__":
    main()
