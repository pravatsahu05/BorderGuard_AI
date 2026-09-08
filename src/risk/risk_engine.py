try:
    from risk.risk_result import RiskResult
    from risk.scoring import calculate_risk_score, classify_severity
except ImportError:
    from risk_result import RiskResult
    from scoring import calculate_risk_score, classify_severity



class RiskEngine:
    """
    Converts an intrusion event into
    a transparent risk assessment.
    """

    def evaluate(
        self,
        event,
    ) -> RiskResult:

        score, breakdown = calculate_risk_score(
            zone=event.current_zone,
            object_type=event.object_type,
            direction=event.direction,
            dwell_time=event.dwell_time,
            confidence=event.confidence,
            event_type=event.event_type,
        )

        severity = classify_severity(score)

        return RiskResult(
            score=score,
            severity=severity,
            breakdown=breakdown,
        )
