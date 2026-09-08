from scoring import (
    calculate_risk_score,
    classify_severity,
)


def main():

    print("=" * 70)
    print("       BORDERGUARD AI - RISK SCORING TEST")
    print("=" * 70)

    # --------------------------------------------------------
    # Scenario 1
    # --------------------------------------------------------

    print("\nScenario 1: Safe person")

    score, breakdown = calculate_risk_score(
        zone="SAFE",
        object_type="person",
        direction="STATIONARY",
        dwell_time=2.0,
        confidence=0.90,
        event_type="NONE",
    )

    severity = classify_severity(score)

    print(f"Risk Score : {score:.2f}")

    print(f"Severity   : {severity}")

    # --------------------------------------------------------
    # Scenario 2
    # --------------------------------------------------------

    print("\nScenario 2: Warning zone")

    score, breakdown = calculate_risk_score(
        zone="WARNING",
        object_type="person",
        direction="DOWN",
        dwell_time=8.0,
        confidence=0.90,
        event_type="DIRECTION_VIOLATION",
    )

    severity = classify_severity(score)

    print(f"Risk Score : {score:.2f}")

    print(f"Severity   : {severity}")

    # --------------------------------------------------------
    # Scenario 3
    # --------------------------------------------------------

    print("\nScenario 3: Restricted entry")

    score, breakdown = calculate_risk_score(
        zone="RESTRICTED",
        object_type="person",
        direction="DOWN",
        dwell_time=5.0,
        confidence=0.92,
        event_type="RESTRICTED_ZONE_ENTRY",
    )

    severity = classify_severity(score)

    print(f"Risk Score : {score:.2f}")

    print(f"Severity   : {severity}")

    # --------------------------------------------------------
    # Breakdown
    # --------------------------------------------------------

    print("\nFactor Breakdown:")

    for factor, data in breakdown.items():

        print(
            f"{factor:15s} "
            f"raw={data['raw_score']:6.2f} "
            f"weight={data['weight']:.2f} "
            f"contribution="
            f"{data['contribution']:6.2f}"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()
