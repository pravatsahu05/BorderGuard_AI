import time
import uuid

try:
    from alerts.alert import Alert
except ImportError:
    from alert import Alert



class AlertEngine:
    """
    Converts high-risk events into alerts.
    """

    def __init__(
        self,
        minimum_severity: str = "MEDIUM",
    ):

        self.minimum_severity = minimum_severity

        self.severity_levels = {
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
            "CRITICAL": 4,
        }

        self.alerts = []

    def should_alert(
        self,
        severity: str,
    ) -> bool:

        current_level = self.severity_levels.get(
            severity,
            0,
        )

        minimum_level = self.severity_levels.get(
            self.minimum_severity,
            2,
        )

        return current_level >= minimum_level

    def create_alert(
        self,
        event,
        risk_result,
    ):

        if not self.should_alert(risk_result.severity):

            return None

        alert_id = f"ALT-" f"{uuid.uuid4().hex[:8].upper()}"

        message = (
            f"{event.object_type.upper()} "
            f"#{event.track_id} triggered "
            f"{event.event_type} in "
            f"{event.current_zone} zone."
        )

        alert = Alert(
            alert_id=alert_id,
            event_id=event.event_id,
            timestamp=time.time(),
            camera_id=event.camera_id,
            track_id=event.track_id,
            object_type=event.object_type,
            message=message,
            severity=risk_result.severity,
            risk_score=risk_result.score,
        )

        self.alerts.append(alert)

        return alert
