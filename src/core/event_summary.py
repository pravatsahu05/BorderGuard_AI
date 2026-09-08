from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class EventSummary:
    """
    UI-friendly security event representation and session summary tracker.
    """
    event_id: str = ""
    camera_id: str = ""
    track_id: int = 0
    object_type: str = ""
    previous_zone: str = ""
    current_zone: str = ""
    direction: str = ""
    event_type: str = ""
    risk_score: float = 0.0
    severity: str = "LOW"
    alert_id: Optional[str] = None
    alert_active: bool = False

    # Session aggregation stats
    total_events: int = 0
    events_by_type: Dict[str, int] = field(default_factory=dict)
    events_by_severity: Dict[str, int] = field(default_factory=dict)
    total_risks: int = 0
    total_alerts: int = 0
    high_risk_count: int = 0

    def add_event(self, event, risk_result=None, alert=None):
        self.total_events += 1
        event_type = getattr(event, "event_type", "UNKNOWN")
        self.events_by_type[event_type] = self.events_by_type.get(event_type, 0) + 1

        sev = getattr(event, "severity", "LOW")
        if risk_result and hasattr(risk_result, "severity"):
            sev = risk_result.severity
        self.events_by_severity[sev] = self.events_by_severity.get(sev, 0) + 1

        if risk_result:
            self.total_risks += 1
            if getattr(risk_result, "severity", None) in ("HIGH", "CRITICAL"):
                self.high_risk_count += 1

        if alert:
            self.total_alerts += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "camera_id": self.camera_id,
            "track_id": self.track_id,
            "object_type": self.object_type,
            "previous_zone": self.previous_zone,
            "current_zone": self.current_zone,
            "direction": self.direction,
            "event_type": self.event_type,
            "risk_score": self.risk_score,
            "severity": self.severity,
            "alert_id": self.alert_id,
            "alert_active": self.alert_active,
            "total_events": self.total_events,
            "events_by_type": dict(self.events_by_type),
            "events_by_severity": dict(self.events_by_severity),
            "total_risks": self.total_risks,
            "total_alerts": self.total_alerts,
            "high_risk_count": self.high_risk_count,
        }

    def reset(self):
        self.total_events = 0
        self.events_by_type.clear()
        self.events_by_severity.clear()
        self.total_risks = 0
        self.total_alerts = 0
        self.high_risk_count = 0
