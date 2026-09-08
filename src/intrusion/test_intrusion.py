from intrusion_detector import IntrusionDetector


def main():

    detector = IntrusionDetector(camera_id="CAM-01")

    print("=" * 60)
    print("       BORDERGUARD AI - INTRUSION TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # Simulate a normal transition.
    # --------------------------------------------------------

    event = detector.evaluate(
        track_id=1,
        object_type="person",
        confidence=0.91,
        previous_zone="SAFE",
        current_zone="WARNING",
        direction="DOWN",
        speed=80.0,
        dwell_time=2.5,
    )

    print(f"SAFE -> WARNING: {event}")

    # --------------------------------------------------------
    # Simulate an intrusion.
    # --------------------------------------------------------

    event = detector.evaluate(
        track_id=1,
        object_type="person",
        confidence=0.91,
        previous_zone="WARNING",
        current_zone="RESTRICTED",
        direction="DOWN",
        speed=95.0,
        dwell_time=1.2,
    )

    print("\nWARNING -> RESTRICTED:")

    if event:

        print(f"Event ID      : {event.event_id}")

        print(f"Event Type    : {event.event_type}")

        print(f"Track ID      : {event.track_id}")

        print(f"Object        : {event.object_type}")

        print(f"Previous Zone : {event.previous_zone}")

        print(f"Current Zone  : {event.current_zone}")

        print(f"Direction     : {event.direction}")

        print(f"Speed         : {event.speed:.1f} px/s")

        print(f"Severity      : {event.severity}")

    else:

        print("No intrusion detected.")

    print("=" * 60)


if __name__ == "__main__":
    main()
