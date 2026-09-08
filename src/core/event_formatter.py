import json
from typing import Any, Optional

try:
    from core.event_summary import EventSummary
except ImportError:
    from src.core.event_summary import EventSummary


def create_event_summary(
    event,
    risk_result,
    alert=None,
) -> EventSummary:
    """
    Convert an intrusion event, risk result and optional alert into an EventSummary.
    """
    if event is None:
        return None

    return EventSummary(
        event_id=getattr(event, "event_id", ""),
        camera_id=getattr(event, "camera_id", ""),
        track_id=getattr(event, "track_id", 0),
        object_type=getattr(event, "object_type", ""),
        previous_zone=getattr(event, "previous_zone", ""),
        current_zone=getattr(event, "current_zone", ""),
        direction=getattr(event, "direction", ""),
        event_type=getattr(event, "event_type", ""),
        risk_score=float(getattr(risk_result, "score", 0.0)) if risk_result else 0.0,
        severity=getattr(risk_result, "severity", "LOW") if risk_result else "LOW",
        alert_id=(getattr(alert, "alert_id", None) if alert is not None else None),
        alert_active=(alert is not None),
    )


class EventFormatter:
    """
    Formats events, risk assessments, alerts, and summaries for display or logging.
    """

    @staticmethod
    def format_event(event) -> str:
        if event is None:
            return "No Event"
        return (
            f"[EVENT {getattr(event, 'event_id', '')}] Type={getattr(event, 'event_type', '')} | "
            f"Track #{getattr(event, 'track_id', 0)} ({getattr(event, 'object_type', '')}) | "
            f"Zone: {getattr(event, 'previous_zone', '')} -> {getattr(event, 'current_zone', '')} | Severity: {getattr(event, 'severity', '')}"
        )

    @staticmethod
    def format_risk(risk_result) -> str:
        if risk_result is None:
            return "No Risk Assessment"
        score = getattr(risk_result, "score", 0.0)
        sev = getattr(risk_result, "severity", "")
        return f"[RISK] Score: {score:.1f}/100 | Severity: {sev}"

    @staticmethod
    def format_alert(alert) -> str:
        if alert is None:
            return "No Alert"
        aid = getattr(alert, "alert_id", "")
        sev = getattr(alert, "severity", "")
        msg = getattr(alert, "message", "")
        return f"[ALERT {aid}] Severity: {sev} | Message: {msg}"

    @staticmethod
    def format_summary(summary: Any) -> str:
        if summary is None:
            return "No Summary"
        if hasattr(summary, "to_dict"):
            d = summary.to_dict()
        elif isinstance(summary, dict):
            d = summary
        else:
            d = str(summary)
        return f"=== SECURITY SUMMARY ===\n{json.dumps(d, indent=2)}"
