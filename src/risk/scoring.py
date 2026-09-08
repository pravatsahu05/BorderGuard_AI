try:
    from risk.config import RISK_CONFIG
except (ImportError, ValueError):
    from .config import RISK_CONFIG



def calculate_dwell_score(
    dwell_time: float,
    maximum_seconds: float = 20.0,
) -> float:

    if dwell_time <= 0:
        return 0.0

    if maximum_seconds <= 0:
        return 100.0

    score = (dwell_time / maximum_seconds) * 100.0

    return min(
        100.0,
        max(0.0, score),
    )


def calculate_confidence_score(
    confidence: float,
) -> float:

    confidence = min(
        1.0,
        max(0.0, confidence),
    )

    return confidence * 100.0


def calculate_risk_score(
    zone: str,
    object_type: str,
    direction: str,
    dwell_time: float,
    confidence: float,
    event_type: str,
):
    """
    Calculate a transparent weighted risk score.

    Returns:
        risk_score, factor_breakdown
    """

    config = RISK_CONFIG

    # --------------------------------------------------------
    # Individual factor scores.
    # --------------------------------------------------------

    zone_score = config["zone_scores"].get(
        zone,
        0,
    )

    object_score = config["object_scores"].get(
        object_type.lower(),
        50,
    )

    direction_score = config["direction_scores"].get(
        direction,
        20,
    )

    dwell_score = calculate_dwell_score(dwell_time)

    confidence_score = calculate_confidence_score(confidence)

    event_score = config["event_scores"].get(
        event_type,
        50,
    )

    # --------------------------------------------------------
    # Weights.
    # --------------------------------------------------------

    weights = config["weights"]

    # --------------------------------------------------------
    # Weighted contributions.
    # --------------------------------------------------------

    zone_contribution = zone_score * weights["zone"]

    object_contribution = object_score * weights["object_type"]

    direction_contribution = direction_score * weights["direction"]

    dwell_contribution = dwell_score * weights["dwell_time"]

    confidence_contribution = confidence_score * weights["confidence"]

    event_contribution = event_score * weights["event_type"]

    # --------------------------------------------------------
    # Final score.
    # --------------------------------------------------------

    total_score = (
        zone_contribution
        + object_contribution
        + direction_contribution
        + dwell_contribution
        + confidence_contribution
        + event_contribution
    )

    total_score = min(
        100.0,
        max(0.0, total_score),
    )

    # --------------------------------------------------------
    # Breakdown for explainability.
    # --------------------------------------------------------

    breakdown = {
        "zone": {
            "raw_score": zone_score,
            "weight": weights["zone"],
            "contribution": zone_contribution,
        },
        "object_type": {
            "raw_score": object_score,
            "weight": weights["object_type"],
            "contribution": object_contribution,
        },
        "direction": {
            "raw_score": direction_score,
            "weight": weights["direction"],
            "contribution": direction_contribution,
        },
        "dwell_time": {
            "raw_score": dwell_score,
            "weight": weights["dwell_time"],
            "contribution": dwell_contribution,
        },
        "confidence": {
            "raw_score": confidence_score,
            "weight": weights["confidence"],
            "contribution": confidence_contribution,
        },
        "event_type": {
            "raw_score": event_score,
            "weight": weights["event_type"],
            "contribution": event_contribution,
        },
    }

    return (
        total_score,
        breakdown,
    )


def classify_severity(
    risk_score: float,
) -> str:
    """
    Convert risk score into severity level.
    """

    thresholds = RISK_CONFIG["severity_thresholds"]

    if risk_score >= thresholds["CRITICAL"]:

        return "CRITICAL"

    if risk_score >= thresholds["HIGH"]:

        return "HIGH"

    if risk_score >= thresholds["MEDIUM"]:

        return "MEDIUM"

    return "LOW"
